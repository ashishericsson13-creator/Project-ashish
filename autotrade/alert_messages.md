# TradingView alert setup

Create **four alerts per symbol** on a chart with Money Line applied.
For each: Condition = `Money Line MASTER` → pick the alert below,
Trigger = **Once Per Bar Close**, Expiration = open-ended,
Notifications → Webhook URL = `https://YOUR_SERVER/hook`.

Paste the matching JSON as the alert **Message**. Nothing else goes in the box.

---

### 1. Open a trend position — condition `BUY — any grade`

```json
{"secret":"REPLACE_ME","ticker":"{{ticker}}","exchange":"{{exchange}}","action":"buy","source":"buySignal","price":{{close}},"stop":{{plot("Money Line")}},"tf":"{{interval}}","bar":"{{time}}"}
```

### 2. Open on a confirmed bottom — condition `Bottom confirmed`

```json
{"secret":"REPLACE_ME","ticker":"{{ticker}}","exchange":"{{exchange}}","action":"buy","source":"botSig","price":{{close}},"stop":{{plot("Money Line")}},"tf":"{{interval}}","bar":"{{time}}"}
```

### 3. Close the position — condition `SELL`

```json
{"secret":"REPLACE_ME","ticker":"{{ticker}}","exchange":"{{exchange}}","action":"sell","source":"sellSignal","price":{{close}},"stop":{{plot("Money Line")}},"tf":"{{interval}}","bar":"{{time}}"}
```

### 4. Close the long-term hold — condition `Exit the long-term hold`

```json
{"secret":"REPLACE_ME","ticker":"{{ticker}}","exchange":"{{exchange}}","action":"sell","source":"exSig","price":{{close}},"stop":{{plot("Money Line")}},"tf":"{{interval}}","bar":"{{time}}"}
```

---

## Why these placeholders

| Placeholder | Gives |
|---|---|
| `{{ticker}}` | symbol, e.g. `AAPL` |
| `{{close}}` | the bar's close — the signal price |
| `{{plot("Money Line")}}` | the stop. This is why no Pine change was needed: the money line is already a named plot |
| `{{time}}` | bar open time in UTC — used to reject duplicate deliveries |

## Two things that will bite you

1. **Trigger must be "Once Per Bar Close".** On "Once Per Bar" the alert fires on an
   unconfirmed bar, and a weekly signal can appear on Monday and be gone by Friday.
2. **`{{plot("Money Line")}}` is the stop for a long.** If the money line sits *above*
   price the server rejects the order rather than sizing off a negative distance.
