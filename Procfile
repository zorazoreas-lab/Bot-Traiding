<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Binance Auto Aggressive Bot</title>
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <h1>Auto Aggressive Bot</h1>
      <p class="muted">Spot only • Safety Lock active</p>
      <nav>
        <button onclick="showPage('dashboard')">Dashboard</button>
        <button onclick="showPage('binance')">Binance API</button>
        <button onclick="showPage('bots')">Bot Setting</button>
        <button onclick="showPage('history')">History</button>
      </nav>
    </aside>

    <main>
      <section id="loginPage" class="card login-card">
        <h2>Admin Login</h2>
        <label>Email</label>
        <input id="email" value="admin@example.com" />
        <label>Password</label>
        <input id="password" type="password" value="ChangeMe123!" />
        <button class="primary" onclick="login()">Login</button>
        <pre id="loginMsg"></pre>
      </section>

      <section id="dashboard" class="page hidden">
        <div class="topbar">
          <h2>Dashboard</h2>
          <button onclick="loadDashboard()">Refresh</button>
        </div>
        <div class="grid">
          <div class="card"><h3>Health</h3><pre id="healthBox">-</pre></div>
          <div class="card"><h3>Balance</h3><pre id="balanceBox">Connect API first</pre></div>
          <div class="card"><h3>BTCUSDT Price</h3><pre id="priceBox">-</pre></div>
        </div>
      </section>

      <section id="binance" class="page hidden">
        <h2>Binance API Connection</h2>
        <div class="warning">Never enable withdrawal permission for this bot.</div>
        <div class="card form-card">
          <label>API Key</label>
          <input id="apiKey" placeholder="Binance API Key" />
          <label>Secret Key</label>
          <input id="secretKey" type="password" placeholder="Binance Secret Key" />
          <label><input id="isTestnet" type="checkbox" checked /> Use Testnet</label>
          <button class="primary" onclick="connectBinance()">Connect & Check Permission</button>
          <button onclick="permissionCheck()">Re-check Permission</button>
          <pre id="binanceMsg"></pre>
        </div>
      </section>

      <section id="bots" class="page hidden">
        <h2>Create Auto Aggressive Bot</h2>
        <div class="card form-card">
          <label>Bot Name</label>
          <input id="botName" value="BTC Aggressive Safety Bot" />
          <label>Symbol</label>
          <input id="symbol" value="BTCUSDT" />
          <label>Max Usable Balance % (max 70)</label>
          <input id="maxUsable" type="number" value="50" />
          <label>Stop Loss %</label>
          <input id="stopLoss" type="number" value="3" />
          <label>Take Profit %</label>
          <input id="takeProfit" type="number" value="5" />
          <label>Daily Loss Limit %</label>
          <input id="dailyLoss" type="number" value="5" />
          <label>Max Trade Per Day</label>
          <input id="maxTrade" type="number" value="3" />
          <label><input id="paperTrading" type="checkbox" checked /> Paper Trading</label>
          <button class="primary" onclick="createBot()">Create Bot</button>
          <pre id="botMsg"></pre>
        </div>
        <h3>Your Bots</h3>
        <div id="botList"></div>
      </section>

      <section id="history" class="page hidden">
        <h2>History & Safety Events</h2>
        <button onclick="loadHistory()">Refresh</button>
        <div class="grid">
          <div class="card"><h3>Orders</h3><pre id="ordersBox">-</pre></div>
          <div class="card"><h3>Logs</h3><pre id="logsBox">-</pre></div>
          <div class="card"><h3>Safety Events</h3><pre id="safetyBox">-</pre></div>
        </div>
      </section>
    </main>
  </div>
  <script src="/static/app.js"></script>
</body>
</html>
