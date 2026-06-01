let token = localStorage.getItem('token') || '';

// Same-domain Railway deploy works with empty API base URL.
// If you host frontend separately, set window.API_BASE_URL before loading this file.
const API_BASE_URL = (window.API_BASE_URL || '').replace(/\/$/, '');

function authHeaders() {
  return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

async function api(path, options = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;
  const res = await fetch(url, { ...options, headers: { ...authHeaders(), ...(options.headers || {}) } });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  if (!res.ok) throw data;
  return data;
}

function pretty(data) { return JSON.stringify(data, null, 2); }
function setText(id, data) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = typeof data === 'string' ? data : pretty(data);
}

function showPage(id) {
  document.getElementById('loginPage').classList.add('hidden');
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
  if (id === 'dashboard') loadDashboard();
  if (id === 'bots') loadBots();
  if (id === 'history') loadHistory();
}

async function login() {
  try {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: email.value, password: password.value })
    });
    token = data.access_token;
    localStorage.setItem('token', token);
    setText('loginMsg', 'Login success');
    showPage('dashboard');
  } catch (e) { setText('loginMsg', e); }
}

function logout() {
  token = '';
  localStorage.removeItem('token');
  location.reload();
}

async function loadDashboard() {
  try { setText('healthBox', await api('/api/health')); } catch (e) { setText('healthBox', e); }
  try { setText('balanceBox', await api('/api/binance/balance')); } catch (e) { setText('balanceBox', e); }
  try { setText('priceBox', await api('/api/binance/price/BTCUSDT')); } catch (e) { setText('priceBox', e); }
}

async function connectBinance() {
  try {
    const data = await api('/api/binance/connect', {
      method: 'POST',
      body: JSON.stringify({ api_key: apiKey.value.trim(), secret_key: secretKey.value.trim(), is_testnet: isTestnet.checked })
    });
    apiKey.value = '';
    secretKey.value = '';
    setText('binanceMsg', data);
  } catch (e) { setText('binanceMsg', e); }
}

async function permissionCheck() {
  try { setText('binanceMsg', await api('/api/binance/permission-check')); }
  catch (e) { setText('binanceMsg', e); }
}

async function createBot() {
  try {
    const payload = {
      bot_name: botName.value,
      symbol: symbol.value,
      strategy_type: 'TREND_BREAKOUT',
      paper_trading: paperTrading.checked,
      max_usable_percent: Number(maxUsable.value),
      stop_loss_percent: Number(stopLoss.value),
      take_profit_percent: Number(takeProfit.value),
      daily_loss_limit_percent: Number(dailyLoss.value),
      max_trade_per_day: Number(maxTrade.value),
      cooldown_minutes: 360
    };
    setText('botMsg', await api('/api/bots', { method: 'POST', body: JSON.stringify(payload) }));
    loadBots();
  } catch (e) { setText('botMsg', e); }
}

async function loadBots() {
  try {
    const data = await api('/api/bots');
    const box = document.getElementById('botList');
    box.innerHTML = '';
    (data.data || []).forEach(bot => {
      const div = document.createElement('div');
      div.className = 'bot-card';
      div.innerHTML = `
        <strong>${bot.bot_name}</strong><br>
        ${bot.symbol} • ${bot.status} • Max usable ${bot.max_usable_percent}% • Paper: ${bot.paper_trading}
        <div class="bot-actions">
          <button onclick="botAction(${bot.id}, 'start')">Start</button>
          <button onclick="botAction(${bot.id}, 'pause')">Pause</button>
          <button onclick="botAction(${bot.id}, 'stop')">Stop</button>
          <button onclick="runOnce(${bot.id})">Run Once</button>
          <button class="danger" onclick="botAction(${bot.id}, 'emergency-stop')">Emergency Stop</button>
        </div>`;
      box.appendChild(div);
    });
  } catch (e) { document.getElementById('botList').innerText = pretty(e); }
}

async function botAction(id, action) {
  try { alert(pretty(await api(`/api/bots/${id}/${action}`, { method: 'POST' }))); loadBots(); }
  catch (e) { alert(pretty(e)); }
}

async function runOnce(id) {
  try { alert(pretty(await api(`/api/bots/${id}/run-once`, { method: 'POST' }))); loadHistory(); }
  catch (e) { alert(pretty(e)); }
}

async function loadHistory() {
  try { setText('ordersBox', await api('/api/trades/orders')); } catch (e) { setText('ordersBox', e); }
  try { setText('logsBox', await api('/api/trades/logs')); } catch (e) { setText('logsBox', e); }
  try { setText('safetyBox', await api('/api/trades/safety-events')); } catch (e) { setText('safetyBox', e); }
}

if (token) showPage('dashboard');
