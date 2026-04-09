import time
import json
import random
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import paho.mqtt.client as mqtt

# -----------------------------
# CONFIGURAÇÕES
# -----------------------------

BROKER = "mqtt"
PORT = 1883
TOPIC = "senai/pii_toy"

ETAPAS = [
    "MONTAGEM_ESTRUTURAL",
    "PINTURA",
    "INSTALACAO_MOTOR",
    "ACABAMENTO_INTERNO",
    "INSPECAO_FINAL",
    "LIBERACAO_TRANSPORTE"
]

ETAPAS_LABELS = [
    "Montagem Estrutural",
    "Pintura",
    "Instalação Motor",
    "Acabamento Interno",
    "Inspeção Final",
    "Liberação Transporte"
]

TEMPOS_ETAPA_MIN = [2, 3, 3, 4, 2, 1]
TEMPOS_ETAPA_MAX = [5, 7, 6, 8, 5, 3]

# -----------------------------
# ESTADO GLOBAL
# -----------------------------

linha = [None] * len(ETAPAS)
tempo_restante = [0] * len(ETAPAS)
fila_entrada = []

historico = []
carros_finalizados = 0
simulacao_ativa = False
lock = threading.Lock()

contador_chassi = 1

# -----------------------------
# MQTT
# -----------------------------

mqtt_client = mqtt.Client()
mqtt_connected = False

def conectar_mqtt():
    global mqtt_connected
    try:
        mqtt_client.connect(BROKER, PORT, 60)
        mqtt_client.loop_start()
        mqtt_connected = True
        print("MQTT conectado.")
    except Exception as e:
        print(f"MQTT não disponível: {e}")
        mqtt_connected = False

def publicar(chassi, etapa, status):
    payload = {
        "chassi": chassi,
        "etapa": etapa,
        "status": status,
        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
    }
    msg = json.dumps(payload)
    if mqtt_connected:
        try:
            mqtt_client.publish(TOPIC, msg)
        except:
            pass
    print(msg)
    with lock:
        historico.append({
            "chassi": chassi,
            "etapa": etapa,
            "status": status,
            "hora": datetime.now().strftime("%H:%M:%S")
        })
        if len(historico) > 200:
            historico.pop(0)

# -----------------------------
# SIMULAÇÃO
# -----------------------------

def timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def gerar_chassi():
    global contador_chassi
    c = f"CHASSI_{str(contador_chassi).zfill(5)}"
    contador_chassi += 1
    return c

def tick():
    global carros_finalizados, simulacao_ativa
    with lock:
        # percorre de trás para frente
        for i in reversed(range(len(ETAPAS))):
            if linha[i] is not None:
                tempo_restante[i] -= 1
                if tempo_restante[i] <= 0:
                    chassi = linha[i]
                    publicar(chassi, ETAPAS[i], "Finalizado")
                    if i == len(ETAPAS) - 1:
                        carros_finalizados += 1
                        linha[i] = None
                    else:
                        if linha[i + 1] is None:
                            linha[i + 1] = chassi
                            tempo_restante[i + 1] = random.randint(
                                TEMPOS_ETAPA_MIN[i + 1], TEMPOS_ETAPA_MAX[i + 1]
                            )
                            publicar(chassi, ETAPAS[i + 1], "Iniciado")
                            linha[i] = None

        # entra novo carro se houver na fila e etapa 0 livre
        if fila_entrada and linha[0] is None:
            chassi = fila_entrada.pop(0)
            linha[0] = chassi
            tempo_restante[0] = random.randint(TEMPOS_ETAPA_MIN[0], TEMPOS_ETAPA_MAX[0])
            publicar(chassi, ETAPAS[0], "Iniciado")

def loop_simulacao():
    global simulacao_ativa
    simulacao_ativa = True
    while True:
        with lock:
            tem_trabalho = any(c is not None for c in linha) or len(fila_entrada) > 0
        if not tem_trabalho:
            simulacao_ativa = False
            break
        tick()
        time.sleep(1)

thread_simulacao = None

def garantir_thread():
    global thread_simulacao, simulacao_ativa
    if not simulacao_ativa or thread_simulacao is None or not thread_simulacao.is_alive():
        thread_simulacao = threading.Thread(target=loop_simulacao, daemon=True)
        thread_simulacao.start()

# -----------------------------
# FLASK APP
# -----------------------------

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Linha de Produção — SENAI</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow+Condensed:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0c10;
    --panel: #0f1318;
    --border: #1e2530;
    --accent: #00e5ff;
    --accent2: #ff6b00;
    --green: #00ff88;
    --yellow: #ffd600;
    --red: #ff3d3d;
    --text: #c8d6e5;
    --muted: #4a5568;
    --mono: 'Share Tech Mono', monospace;
    --sans: 'Barlow Condensed', sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Grid de fundo */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .container {
    position: relative;
    z-index: 1;
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px 20px;
  }

  /* HEADER */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px;
    margin-bottom: 28px;
  }

  .logo {
    font-family: var(--sans);
    font-weight: 800;
    font-size: 22px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .logo-icon {
    width: 34px;
    height: 34px;
    border: 2px solid var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: var(--accent);
    animation: pulse-border 2s infinite;
  }

  @keyframes pulse-border {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,229,255,0.4); }
    50% { box-shadow: 0 0 0 6px rgba(0,229,255,0); }
  }

  .status-bar {
    display: flex;
    gap: 20px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--muted);
  }

  .status-item { display: flex; align-items: center; gap: 6px; }
  .status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--muted);
  }
  .status-dot.online { background: var(--green); box-shadow: 0 0 8px var(--green); }
  .status-dot.busy { background: var(--yellow); box-shadow: 0 0 8px var(--yellow); animation: blink 1s infinite; }

  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  /* GRID PRINCIPAL */
  .main-grid {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  /* PAINÉIS */
  .panel {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 20px;
    position: relative;
  }

  .panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
  }

  .panel.orange::before { background: var(--accent2); }
  .panel.green::before { background: var(--green); }

  .panel-title {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .panel.orange .panel-title { color: var(--accent2); }
  .panel.green .panel-title { color: var(--green); }

  .panel-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }

  /* INPUTS */
  .input-group {
    margin-bottom: 16px;
  }

  label {
    display: block;
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  input[type="text"],
  input[type="number"] {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: var(--mono);
    font-size: 14px;
    padding: 10px 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(0,229,255,0.1);
  }

  .panel.orange input:focus {
    border-color: var(--accent2);
    box-shadow: 0 0 0 2px rgba(255,107,0,0.1);
  }

  .btn {
    width: 100%;
    padding: 12px;
    font-family: var(--sans);
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    border: none;
    cursor: pointer;
    transition: all 0.15s;
    position: relative;
    overflow: hidden;
  }

  .btn-primary {
    background: var(--accent);
    color: var(--bg);
  }

  .btn-primary:hover {
    background: #33eeff;
    box-shadow: 0 0 20px rgba(0,229,255,0.4);
  }

  .btn-orange {
    background: var(--accent2);
    color: var(--bg);
  }

  .btn-orange:hover {
    background: #ff8533;
    box-shadow: 0 0 20px rgba(255,107,0,0.4);
  }

  .btn:active { transform: scale(0.98); }

  .msg {
    font-family: var(--mono);
    font-size: 12px;
    margin-top: 10px;
    padding: 8px 12px;
    border-left: 3px solid;
    display: none;
  }

  .msg.success { border-color: var(--green); color: var(--green); background: rgba(0,255,136,0.05); }
  .msg.error { border-color: var(--red); color: var(--red); background: rgba(255,61,61,0.05); }
  .msg.show { display: block; }

  /* LINHA DE PRODUÇÃO */
  .line-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 20px;
    position: relative;
    margin-bottom: 20px;
  }

  .line-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2), var(--green));
  }

  .stages-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    margin-top: 16px;
  }

  .stage-card {
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 14px 10px;
    text-align: center;
    position: relative;
    transition: border-color 0.3s, box-shadow 0.3s;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  .stage-card.occupied {
    border-color: var(--accent);
    box-shadow: 0 0 12px rgba(0,229,255,0.15);
  }

  .stage-num {
    position: absolute;
    top: 6px; left: 8px;
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
  }

  .stage-name {
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--muted);
    line-height: 1.3;
  }

  .stage-chassi {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--accent);
    font-weight: bold;
  }

  .stage-timer {
    font-family: var(--mono);
    font-size: 18px;
    color: var(--yellow);
  }

  .stage-empty {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--border);
  }

  .stage-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--muted);
    font-size: 18px;
    align-self: center;
  }

  /* FILA */
  .queue-info {
    display: flex;
    gap: 20px;
    margin-top: 14px;
    flex-wrap: wrap;
  }

  .stat-box {
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 12px 16px;
    flex: 1;
    min-width: 120px;
  }

  .stat-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
  }

  .stat-value {
    font-family: var(--mono);
    font-size: 28px;
    color: var(--accent);
    line-height: 1;
  }

  .stat-value.orange { color: var(--accent2); }
  .stat-value.green { color: var(--green); }
  .stat-value.yellow { color: var(--yellow); }

  /* LOG */
  .log-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 20px;
  }

  .log-list {
    height: 200px;
    overflow-y: auto;
    font-family: var(--mono);
    font-size: 12px;
  }

  .log-list::-webkit-scrollbar { width: 4px; }
  .log-list::-webkit-scrollbar-track { background: var(--bg); }
  .log-list::-webkit-scrollbar-thumb { background: var(--border); }

  .log-item {
    display: grid;
    grid-template-columns: 70px 120px 1fr 100px;
    gap: 12px;
    padding: 5px 0;
    border-bottom: 1px solid rgba(30,37,48,0.6);
    align-items: center;
  }

  .log-hora { color: var(--muted); }
  .log-chassi { color: var(--accent); }
  .log-etapa { color: var(--text); font-size: 11px; }
  .log-status-ini { color: var(--yellow); }
  .log-status-fin { color: var(--green); }

  /* RESPONSIVO STAGES */
  @media (max-width: 1100px) {
    .stages-grid { grid-template-columns: repeat(3, 1fr); }
    .main-grid { grid-template-columns: 1fr; }
  }

  @media (max-width: 700px) {
    .stages-grid { grid-template-columns: repeat(2, 1fr); }
  }

  .divider {
    width: 1px;
    background: var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 4px;
    writing-mode: vertical-rl;
  }

  .input-panels {
    display: grid;
    grid-template-columns: 1fr 4px 1fr;
    gap: 0;
    height: 100%;
  }

  .fila-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
    max-height: 80px;
    overflow-y: auto;
  }

  .chip {
    font-family: var(--mono);
    font-size: 10px;
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    color: var(--accent);
    padding: 3px 8px;
  }

  .scanning-line {
    position: absolute;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scan 2s linear infinite;
    pointer-events: none;
  }

  @keyframes scan {
    0% { top: 0; opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
  }
</style>
</head>
<body>
<div class="container">

  <header>
    <div class="logo">
      <div class="logo-icon">⚙</div>
      SENAI · Linha de Produção
    </div>
    <div class="status-bar">
      <div class="status-item">
        <div class="status-dot online" id="dot-mqtt"></div>
        <span id="label-mqtt">MQTT</span>
      </div>
      <div class="status-item">
        <div class="status-dot busy" id="dot-sim"></div>
        <span id="label-sim">SIMULAÇÃO</span>
      </div>
    </div>
  </header>

  <!-- INPUTS -->
  <div class="main-grid" style="grid-template-columns: 1fr 1fr; margin-bottom: 20px;">

    <div class="panel" style="padding:0; overflow:hidden; position: relative;">
      <div class="scanning-line"></div>
      <div style="padding:20px;">
        <div class="panel-title">⬡ Input Manual</div>
        <div class="input-group">
          <label>Chassi do veículo</label>
          <input type="text" id="chassi-input" placeholder="Ex: CHASSI_00001" />
        </div>
        <button class="btn btn-primary" onclick="enviarManual()">▶ Enviar para Produção</button>
        <div class="msg" id="msg-manual"></div>
      </div>
    </div>

    <div class="panel orange" style="position: relative;">
      <div class="panel-title">⬡ Input em Lote</div>
      <div class="input-group">
        <label>Quantidade de veículos</label>
        <input type="number" id="qtd-input" placeholder="Ex: 10" min="1" max="100" />
      </div>
      <button class="btn btn-orange" onclick="enviarLote()">▶ Gerar e Enviar Lote</button>
      <div class="msg" id="msg-lote"></div>
    </div>

  </div>

  <!-- LINHA DE PRODUÇÃO -->
  <div class="line-panel">
    <div class="panel-title" style="color: var(--text); font-size:12px;">
      ⬡ LINHA DE PRODUÇÃO — Estado em Tempo Real
    </div>

    <div class="queue-info">
      <div class="stat-box">
        <div class="stat-label">Na Fila</div>
        <div class="stat-value yellow" id="stat-fila">0</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Em Processo</div>
        <div class="stat-value orange" id="stat-processo">0</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Finalizados</div>
        <div class="stat-value green" id="stat-finalizados">0</div>
      </div>
    </div>

    <div class="stages-grid" id="stages-grid">
      <!-- gerado dinamicamente -->
    </div>

    <div style="margin-top:12px;">
      <div class="stat-label" style="margin-bottom:6px;">Fila de Entrada</div>
      <div class="fila-chips" id="fila-chips"></div>
    </div>
  </div>

  <!-- LOG -->
  <div class="log-panel">
    <div class="panel-title" style="color: var(--green); font-size:11px;">⬡ LOG DE EVENTOS</div>
    <div class="log-list" id="log-list"></div>
  </div>

</div>

<script>
const ETAPAS_LABELS = {{ etapas_labels | tojson }};

function showMsg(id, text, tipo) {
  const el = document.getElementById(id);
  el.className = 'msg show ' + tipo;
  el.textContent = text;
  setTimeout(() => el.classList.remove('show'), 3000);
}

async function enviarManual() {
  const chassi = document.getElementById('chassi-input').value.trim();
  if (!chassi) { showMsg('msg-manual', 'Informe o chassi.', 'error'); return; }
  const r = await fetch('/api/enviar', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({chassi})
  });
  const d = await r.json();
  showMsg('msg-manual', d.message, d.ok ? 'success' : 'error');
  if (d.ok) document.getElementById('chassi-input').value = '';
}

async function enviarLote() {
  const qtd = parseInt(document.getElementById('qtd-input').value);
  if (!qtd || qtd < 1) { showMsg('msg-lote', 'Informe uma quantidade válida.', 'error'); return; }
  const r = await fetch('/api/lote', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({qtd})
  });
  const d = await r.json();
  showMsg('msg-lote', d.message, d.ok ? 'success' : 'error');
  if (d.ok) document.getElementById('qtd-input').value = '';
}

function renderStages(estado) {
  const grid = document.getElementById('stages-grid');
  grid.innerHTML = '';
  estado.linha.forEach((chassi, i) => {
    const card = document.createElement('div');
    card.className = 'stage-card' + (chassi ? ' occupied' : '');
    const timer = estado.tempo_restante[i];
    card.innerHTML = `
      <span class="stage-num">${String(i+1).padStart(2,'0')}</span>
      <div class="stage-name">${ETAPAS_LABELS[i]}</div>
      ${chassi
        ? `<div class="stage-chassi">${chassi.replace('CHASSI_','#')}</div>
           <div class="stage-timer">${timer}s</div>`
        : `<div class="stage-empty">— vazio —</div>`}
    `;
    grid.appendChild(card);
  });
}

function renderFila(fila) {
  const el = document.getElementById('fila-chips');
  if (!fila.length) { el.innerHTML = '<span style="font-family:var(--mono);font-size:11px;color:var(--muted);">Nenhum veículo aguardando</span>'; return; }
  el.innerHTML = fila.slice(0, 20).map(c => `<div class="chip">${c.replace('CHASSI_','#')}</div>`).join('');
  if (fila.length > 20) el.innerHTML += `<div class="chip" style="color:var(--muted)">+${fila.length-20}</div>`;
}

function renderLog(historico) {
  const el = document.getElementById('log-list');
  const itens = [...historico].reverse().slice(0, 50);
  el.innerHTML = itens.map(h => `
    <div class="log-item">
      <span class="log-hora">${h.hora}</span>
      <span class="log-chassi">${h.chassi}</span>
      <span class="log-etapa">${h.etapa.replace(/_/g,' ')}</span>
      <span class="${h.status === 'Iniciado' ? 'log-status-ini' : 'log-status-fin'}">${h.status.toUpperCase()}</span>
    </div>
  `).join('');
}

async function atualizar() {
  try {
    const r = await fetch('/api/estado');
    const d = await r.json();
    renderStages(d);
    renderFila(d.fila);
    renderLog(d.historico);
    document.getElementById('stat-fila').textContent = d.fila.length;
    document.getElementById('stat-processo').textContent = d.linha.filter(Boolean).length;
    document.getElementById('stat-finalizados').textContent = d.finalizados;
    const dotSim = document.getElementById('dot-sim');
    const labSim = document.getElementById('label-sim');
    if (d.simulacao_ativa) {
      dotSim.className = 'status-dot busy';
      labSim.textContent = 'ATIVA';
    } else {
      dotSim.className = 'status-dot';
      labSim.textContent = 'PARADA';
    }
  } catch(e) {}
}

setInterval(atualizar, 1000);
atualizar();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, etapas_labels=ETAPAS_LABELS)

@app.route("/api/enviar", methods=["POST"])
def api_enviar():
    data = request.get_json()
    chassi = data.get("chassi", "").strip()
    if not chassi:
        return jsonify({"ok": False, "message": "Chassi inválido."})
    with lock:
        fila_entrada.append(chassi)
    garantir_thread()
    return jsonify({"ok": True, "message": f"{chassi} adicionado à fila de produção."})

@app.route("/api/lote", methods=["POST"])
def api_lote():
    data = request.get_json()
    qtd = int(data.get("qtd", 0))
    if qtd < 1:
        return jsonify({"ok": False, "message": "Quantidade inválida."})
    with lock:
        for _ in range(qtd):
            fila_entrada.append(gerar_chassi())
    garantir_thread()
    return jsonify({"ok": True, "message": f"{qtd} veículos adicionados à fila."})

@app.route("/api/estado")
def api_estado():
    with lock:
        return jsonify({
            "linha": list(linha),
            "tempo_restante": list(tempo_restante),
            "fila": list(fila_entrada),
            "finalizados": carros_finalizados,
            "simulacao_ativa": simulacao_ativa,
            "historico": list(historico[-50:])
        })

# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    conectar_mqtt()
    app.run(debug=False, host="0.0.0.0", port=5000)