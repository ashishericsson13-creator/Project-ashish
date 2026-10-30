"""
Money Line → Interactive Brokers bridge.

TradingView fires an alert, posts JSON here, this places the order.

Everything below the parsing is a refusal. The happy path is about twenty
lines; the rest exists because a webhook endpoint is a public URL and a
malformed payload is indistinguishable from a real one until you check.
"""
import json, logging, os, threading
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from ib_async import IB, LimitOrder, Stock

load_dotenv()

HOST          = os.getenv("IB_HOST", "127.0.0.1")
PORT          = int(os.getenv("IB_PORT", "7497"))
CLIENT_ID     = int(os.getenv("IB_CLIENT_ID", "17"))
SECRET        = os.getenv("WEBHOOK_SECRET", "")
LIVE          = os.getenv("TRADING_MODE", "PAPER").strip().upper() == "LIVE"
RISK_PCT      = float(os.getenv("RISK_PCT", "1.0"))
MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", "5"))
MAX_ORDER_USD = float(os.getenv("MAX_ORDER_USD", "2500"))
MIN_STOP_PCT  = float(os.getenv("MIN_STOP_PCT", "2.0"))
MAX_STOP_PCT  = float(os.getenv("MAX_STOP_PCT", "25.0"))
ALLOWLIST     = {s.strip().upper() for s in os.getenv("ALLOWLIST", "").split(",") if s.strip()}
RTH_ONLY      = os.getenv("RTH_ONLY", "true").lower() == "true"

BASE = Path(__file__).resolve().parent
KILL = BASE / "KILL"              # touch this file and every order stops
LOG  = BASE / "trades.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(message)s",
    handlers=[logging.FileHandler(LOG), logging.StreamHandler()],
)
log = logging.getLogger("bridge")

app = Flask(__name__)
ib = IB()
_lock = threading.Lock()
_seen: set[str] = set()           # (ticker, action, bar) already acted on


class Refused(Exception):
    """A signal we will not act on. The reason is the message."""


def connect() -> None:
    if not ib.isConnected():
        ib.connect(HOST, PORT, clientId=CLIENT_ID, timeout=10)
        log.info("connected to IBKR %s:%s as %s", HOST, PORT, "LIVE" if LIVE else "PAPER")


def equity() -> float:
    for row in ib.accountSummary():
        if row.tag == "NetLiquidation":
            return float(row.value)
    raise Refused("could not read NetLiquidation from the account")


def open_positions() -> dict[str, float]:
    return {p.contract.symbol.upper(): p.position for p in ib.positions() if p.position}


def validate(p: dict) -> dict:
    """Every way a payload can be wrong, in one place."""
    if KILL.exists():
        raise Refused("KILL file present — trading halted")
    if not SECRET or p.get("secret") != SECRET:
        raise Refused("bad or missing secret")

    action = str(p.get("action", "")).lower()
    if action not in ("buy", "sell"):
        raise Refused(f"action must be buy or sell, got {action!r}")

    ticker = str(p.get("ticker", "")).upper().strip()
    if not ticker:
        raise Refused("no ticker")
    if ticker not in ALLOWLIST:
        raise Refused(f"{ticker} is not on the allowlist")

    try:
        price = float(p["price"])
        stop = float(p["stop"])
    except (KeyError, TypeError, ValueError):
        raise Refused("price and stop must both be numbers")
    if price <= 0:
        raise Refused(f"price {price} is not positive")

    bar = str(p.get("bar", ""))
    key = f"{ticker}|{action}|{bar}"
    if key in _seen:
        raise Refused(f"duplicate delivery for {key}")

    return {"ticker": ticker, "action": action, "price": price,
            "stop": stop, "bar": bar, "key": key,
            "source": str(p.get("source", "?"))}


def size(sig: dict) -> int:
    """1% of equity at risk, then every cap that can shrink it."""
    price, stop = sig["price"], sig["stop"]

    if stop >= price:
        raise Refused(f"stop {stop} is not below price {price} — not a long setup")
    stop_pct = (price - stop) / price * 100
    if stop_pct < MIN_STOP_PCT:
        raise Refused(f"stop is {stop_pct:.1f}% away, under the {MIN_STOP_PCT}% floor")
    if stop_pct > MAX_STOP_PCT:
        raise Refused(f"stop is {stop_pct:.1f}% away, over the {MAX_STOP_PCT}% ceiling")

    risk = equity() * RISK_PCT / 100
    qty = int(risk / (price - stop))
    capped = int(MAX_ORDER_USD / price)
    if qty > capped:
        log.info("size capped by MAX_ORDER_USD: %d → %d shares", qty, capped)
        qty = capped
    if qty < 1:
        raise Refused(f"1% of equity buys less than one share at {price}")
    return qty


def place(sig: dict) -> dict:
    connect()
    held = open_positions()
    ticker, action = sig["ticker"], sig["action"]

    if action == "buy":
        if ticker in held:
            raise Refused(f"already long {ticker}, not adding")
        if len(held) >= MAX_POSITIONS:
            raise Refused(f"{len(held)} positions open, limit is {MAX_POSITIONS}")
        qty = size(sig)
    else:
        qty = int(abs(held.get(ticker, 0)))
        if qty == 0:
            raise Refused(f"no position in {ticker} to sell")

    contract = Stock(ticker, "SMART", "USD")
    ib.qualifyContracts(contract)

    # A limit 0.3% through the signal price. Market orders on a weekly gap
    # fill wherever the book happens to be, which on NOW last week was 31% away.
    pad = sig["price"] * 0.003
    limit = round(sig["price"] + pad if action == "buy" else sig["price"] - pad, 2)

    order = LimitOrder(action.upper(), qty, limit, tif="DAY", outsideRth=not RTH_ONLY)
    trade = ib.placeOrder(contract, order)
    log.info("ORDER %s %d %s @ %.2f limit (signal %.2f stop %.2f, %s)",
             action.upper(), qty, ticker, limit, sig["price"], sig["stop"], sig["source"])
    return {"ok": True, "ticker": ticker, "action": action,
            "qty": qty, "limit": limit, "orderId": trade.order.orderId}


@app.post("/hook")
def hook():
    raw = request.get_data(as_text=True)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        log.warning("REFUSED unparseable body: %s", raw[:200])
        return jsonify({"ok": False, "error": "body is not JSON"}), 400

    with _lock:
        try:
            sig = validate(payload)
            result = place(sig)
            _seen.add(sig["key"])
            return jsonify(result), 200
        except Refused as r:
            log.warning("REFUSED %s  (payload: %s)", r, {k: v for k, v in payload.items() if k != "secret"})
            return jsonify({"ok": False, "refused": str(r)}), 200
        except Exception:
            log.exception("FAILED while handling a signal")
            return jsonify({"ok": False, "error": "internal"}), 500


@app.get("/health")
def health():
    try:
        connect()
        return jsonify({"ok": True, "mode": "LIVE" if LIVE else "PAPER",
                        "equity": equity(), "positions": open_positions(),
                        "halted": KILL.exists()}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 503


if __name__ == "__main__":
    if LIVE and PORT in (7497, 4002):
        raise SystemExit("TRADING_MODE=LIVE but IB_PORT is a paper port. Refusing to start.")
    if not LIVE and PORT in (7496, 4001):
        raise SystemExit("IB_PORT is a live port but TRADING_MODE is not LIVE. Refusing to start.")
    if not SECRET or SECRET == "CHANGE_ME":
        raise SystemExit("WEBHOOK_SECRET is unset. Refusing to start.")
    log.info("starting in %s mode, allowlist=%s", "LIVE" if LIVE else "PAPER", sorted(ALLOWLIST))
    app.run(host="0.0.0.0", port=int(os.getenv("WEB_PORT", "8080")))
