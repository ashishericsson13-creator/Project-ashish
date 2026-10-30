# Money Line → Interactive Brokers

TradingView alert → webhook → IBKR order. Longs only, 1% risk, max 5 positions.

## Order of operations

### 1. IBKR account
- Individual, **Cash** account (exempt from the pattern-day-trader rule below $25k).
- **IBKR Lite** if eligible — $0 commission on US stocks.
- Enable **fractional shares**: at $10k a single AAPL share is 3.5% of the book.
- Your paper account comes free with the live one. Same API, different port.

### 2. TWS or IB Gateway
Gateway is the better choice — no charts, far less memory, built to stay up.

`Configure → API → Settings`:
- ✅ Enable ActiveX and Socket Clients
- ✅ Read-Only API → **off** (it must be able to place orders)
- Socket port: `4002` paper, `4001` live
- Trusted IP: `127.0.0.1`

Gateway logs out daily. Set `Configure → Lock and Exit → Auto restart`,
or it will be asleep when a signal fires.

### 3. Server
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install flask ib_async python-dotenv
cp config.example.env .env
python3 -c "import secrets;print(secrets.token_urlsafe(32))"   # paste into WEBHOOK_SECRET
python3 server.py
```

Check it: `curl localhost:8080/health` → equity, open positions, mode.

### 4. Expose it
TradingView must reach the URL over **HTTPS**. Either a VPS with a domain and
Caddy in front, or `cloudflared tunnel` from a machine at home. Do not open a
bare port — the only thing between the internet and your orders is the secret.

### 5. Alerts
See `alert_messages.md`. Four per symbol, **Once Per Bar Close**.

### 6. First trade
Set `MAX_ORDER_USD=300` for the first week. You chose live from day one, so the
smallest size is doing the job paper trading would otherwise do.

## The controls

| Control | Does |
|---|---|
| `touch KILL` | every subsequent order is refused. No restart needed. |
| `MAX_ORDER_USD` | hard dollar ceiling per order, whatever the risk maths says |
| `ALLOWLIST` | a symbol not listed is refused and logged |
| `MIN/MAX_STOP_PCT` | rejects a stop too close to size sanely or too far to be a stop |
| duplicate guard | same ticker + action + bar time acts once |
| `TRADING_MODE` | must read exactly `LIVE`; the port must agree or it will not start |

## What it does not do

- **Longs only.** A `sell` closes a position; it never opens a short.
- **No bracket orders.** The stop lives in the script, not at the broker: if the
  server is down when price hits it, nothing happens. Adding a broker-side stop
  on entry is the first upgrade worth making.
- **No partial exits.** `AT TARGET` says bank a third to a half — the bot sells all
  or nothing.
- **No reconciliation on restart.** It reads positions from IBKR each time, so it
  will not double-buy, but it does not know about fills it never saw.

## Reading the log

`trades.log` has one line per decision. `REFUSED` lines are the ones to read —
they are the system declining, usually correctly. If you see the same refusal
every week, the alert is misconfigured, not the stock.
