import time
import json
import random
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

# -------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------

BROKER = "localhost"
PORT   = 1883

TOPIC_PRODUCAO  = "senai/producao/linha"
TOPIC_LOGISTICA = "senai/logistica/entrega"

ETAPAS = [
    "MONTAGEM_ESTRUTURAL",
    "PINTURA",
    "INSTALACAO_MOTOR",
    "ACABAMENTO_INTERNO",
    "INSPECAO_FINAL",
    "LIBERACAO_TRANSPORTE",
]

ETAPAS_LABELS = [
    "Montagem Est.",
    "Pintura",
    "Motor",
    "Acabamento",
    "Inspeção",
    "Liberação",
]

TEMPOS_MIN = [2, 3, 3, 4, 2, 1]
TEMPOS_MAX = [5, 7, 6, 8, 5, 3]

CONCESSIONARIAS = [
    "Concessionária Norte — SP",
    "Concessionária Sul — RS",
    "Concessionária Centro-Oeste — GO",
    "Concessionária Leste — RJ",
    "Concessionária Nordeste — BA",
]

# -------------------------------------------------------
# ESTADO GLOBAL
# -------------------------------------------------------

linha          = [None] * len(ETAPAS)
tempo_restante = [0]    * len(ETAPAS)
fila_entrada   = []

historico        = []
carros_finalizados = 0
simulacao_ativa  = False
lock             = threading.Lock()

ls_veic    = 0
ls_peca    = 0
ls_transit = 0
msg_count  = 0

chassi_counter = 1
sku_counter    = 1

# -------------------------------------------------------
# MQTT
# -------------------------------------------------------

mqtt_client    = None
mqtt_connected = False

def conectar_mqtt():
    global mqtt_client, mqtt_connected
    if not MQTT_AVAILABLE:
        print("[MQTT] paho-mqtt não instalado — publicação desativada.")
        return
    try:
        mqtt_client = mqtt.Client()
        mqtt_client.connect(BROKER, PORT, 60)
        mqtt_client.loop_start()
        mqtt_connected = True
        print(f"[MQTT] Conectado a {BROKER}:{PORT}")
    except Exception as e:
        print(f"[MQTT] Não disponível: {e}")
        mqtt_connected = False

def _publicar_mqtt(topic: str, payload: dict):
    msg = json.dumps(payload, ensure_ascii=False)
    if mqtt_connected and mqtt_client:
        try:
            mqtt_client.publish(topic, msg)
        except Exception as e:
            print(f"[MQTT] Erro ao publicar: {e}")
    print(f"[PUB] {topic} → {msg}")

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------

def ts():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def now_str():
    return datetime.now().strftime("%H:%M:%S")

def gerar_chassi():
    global chassi_counter
    c = f"VW-2024-{str(chassi_counter).zfill(3)}"
    chassi_counter += 1
    return c

def gerar_sku():
    global sku_counter
    s = f"SKU-{str(sku_counter).zfill(4)}"
    sku_counter += 1
    return s

def registrar_evento(topic: str, dados: dict):
    """Salva evento no histórico e publica no MQTT."""
    global msg_count
    msg_count += 1
    entry = {"time": now_str(), "topic": topic, **dados}
    with lock:
        historico.append(entry)
        if len(historico) > 400:
            historico.pop(0)
    _publicar_mqtt(topic, dados)

# -------------------------------------------------------
# SIMULAÇÃO — LINHA DE PRODUÇÃO
# -------------------------------------------------------

def tick():
    """Um ciclo de 1 segundo na linha de produção."""
    global carros_finalizados

    # percorre de trás para frente para evitar conflito de posições
    for i in reversed(range(len(ETAPAS))):
        if linha[i] is not None:
            tempo_restante[i] -= 1
            if tempo_restante[i] <= 0:
                chassi = linha[i]
                topic  = TOPIC_PRODUCAO

                registrar_evento(topic, {
                    "chassi":    chassi,
                    "etapa":     ETAPAS[i],
                    "status":    "FINALIZADO",
                    "timestamp": ts(),
                })

                if i == len(ETAPAS) - 1:
                    # última etapa — veículo sai da linha
                    carros_finalizados += 1
                    linha[i] = None
                else:
                    # avança para a próxima etapa se estiver livre
                    if linha[i + 1] is None:
                        linha[i + 1]      = chassi
                        tempo_restante[i + 1] = random.randint(
                            TEMPOS_MIN[i + 1], TEMPOS_MAX[i + 1]
                        )
                        registrar_evento(topic, {
                            "chassi":    chassi,
                            "etapa":     ETAPAS[i + 1],
                            "status":    "INICIADO",
                            "timestamp": ts(),
                        })
                        linha[i] = None
                    # se próxima etapa ocupada, aguarda (chassi permanece)

    # entra novo veículo da fila se a 1ª etapa estiver livre
    if fila_entrada and linha[0] is None:
        chassi       = fila_entrada.pop(0)
        linha[0]     = chassi
        tempo_restante[0] = random.randint(TEMPOS_MIN[0], TEMPOS_MAX[0])
        registrar_evento(TOPIC_PRODUCAO, {
            "chassi":    chassi,
            "etapa":     ETAPAS[0],
            "status":    "INICIADO",
            "timestamp": ts(),
        })

def loop_simulacao():
    global simulacao_ativa
    simulacao_ativa = True
    while True:
        with lock:
            tem_trabalho = any(c is not None for c in linha) or len(fila_entrada) > 0
        if not tem_trabalho:
            simulacao_ativa = False
            break
        with lock:
            tick()
        time.sleep(1)

thread_simulacao = None

def garantir_thread():
    global thread_simulacao, simulacao_ativa
    if not simulacao_ativa or thread_simulacao is None or not thread_simulacao.is_alive():
        thread_simulacao = threading.Thread(target=loop_simulacao, daemon=True)
        thread_simulacao.start()

# -------------------------------------------------------
# AUTO-SEND — PRODUÇÃO
# -------------------------------------------------------

auto_producao_ativo   = False
auto_producao_thread  = None

def loop_auto_producao(intervalo: int):
    while auto_producao_ativo:
        with lock:
            fila_entrada.append(gerar_chassi())
        garantir_thread()
        time.sleep(intervalo)

def iniciar_auto_producao(intervalo: int = 8):
    global auto_producao_ativo, auto_producao_thread
    auto_producao_ativo = True
    auto_producao_thread = threading.Thread(
        target=loop_auto_producao, args=(intervalo,), daemon=True
    )
    auto_producao_thread.start()

def parar_auto_producao():
    global auto_producao_ativo
    auto_producao_ativo = False

# -------------------------------------------------------
# AUTO-SEND — LOGÍSTICA
# -------------------------------------------------------

auto_logistica_ativo  = False
auto_logistica_thread = None

def loop_auto_logistica(intervalo: int):
    global ls_veic, ls_peca, ls_transit
    while auto_logistica_ativo:
        tipo    = random.choice(["veiculo", "peca"])
        id_item = gerar_chassi() if tipo == "veiculo" else gerar_sku()
        destino = random.choice(CONCESSIONARIAS)
        _registrar_logistica(tipo, id_item, destino, TOPIC_LOGISTICA)
        time.sleep(intervalo)

def _registrar_logistica(tipo: str, id_item: str, destino: str, topic: str):
    global ls_veic, ls_peca, ls_transit
    registrar_evento(topic, {
        "id":        id_item,
        "tipo":      tipo,
        "destino":   destino,
        "status":    "DESPACHADO",
        "timestamp": ts(),
    })
    with lock:
        if tipo == "veiculo":
            ls_veic += 1
        else:
            ls_peca += 1
        ls_transit += 1

    # simula chegada após 12 s
    def chegada():
        global ls_transit
        time.sleep(12)
        with lock:
            ls_transit = max(0, ls_transit - 1)
    threading.Thread(target=chegada, daemon=True).start()

def iniciar_auto_logistica(intervalo: int = 6):
    global auto_logistica_ativo, auto_logistica_thread
    auto_logistica_ativo = True
    auto_logistica_thread = threading.Thread(
        target=loop_auto_logistica, args=(intervalo,), daemon=True
    )
    auto_logistica_thread.start()

def parar_auto_logistica():
    global auto_logistica_ativo
    auto_logistica_ativo = False

# -------------------------------------------------------
# FLASK — HTML
# -------------------------------------------------------

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SENAI · Linha de Produção</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --marsala:       #8B2E2E;
    --marsala-l:     #B85C5C;
    --marsala-xl:    #F5E8E8;
    --marsala-mid:   #D4908A;
    --cream:         #FBF7F4;
    --surface:       #FFFFFF;
    --surface2:      #FDF4F2;
    --border:        #E8D5D0;
    --border-s:      #C9A9A2;
    --text:          #2A1818;
    --text-m:        #7A5555;
    --text-h:        #B89090;
    --green:         #2E7D4F;
    --green-bg:      #EAF5EE;
    --amber:         #A05C00;
    --amber-bg:      #FFF4E0;
    --mono: 'DM Mono', monospace;
    --sans: 'DM Sans', sans-serif;
    --r: 8px;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:var(--sans); background:var(--cream); color:var(--text); font-size:14px; line-height:1.5; }
  .app { max-width:1360px; margin:0 auto; padding:18px 20px; }

  /* HEADER */
  .hdr { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; padding-bottom:14px; border-bottom:1.5px solid var(--border); }
  .brand { display:flex; align-items:center; gap:10px; }
  .brand-icon { width:36px; height:36px; background:var(--marsala); border-radius:var(--r); display:flex; align-items:center; justify-content:center; color:#fff; font-size:17px; }
  .brand-text { font-size:15px; font-weight:600; color:var(--marsala); letter-spacing:.5px; }
  .brand-sub  { font-size:11px; color:var(--text-m); }
  .pills { display:flex; gap:8px; }
  .pill { display:flex; align-items:center; gap:6px; background:var(--surface); border:1px solid var(--border); border-radius:20px; padding:4px 12px; font-size:11px; font-family:var(--mono); color:var(--text-m); }
  .dot { width:7px; height:7px; border-radius:50%; background:var(--text-h); }
  .dot.ok  { background:var(--green); }
  .dot.run { background:var(--marsala); animation:blink 1.2s infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

  /* TABS */
  .tabs { display:flex; gap:2px; background:var(--surface2); border:1px solid var(--border); border-radius:var(--r); padding:3px; margin-bottom:14px; }
  .tab  { flex:1; padding:7px 12px; border:none; background:transparent; border-radius:6px; font-family:var(--sans); font-size:12px; font-weight:500; color:var(--text-m); cursor:pointer; transition:.15s; }
  .tab.active { background:var(--marsala); color:#fff; }

  /* PANELS */
  .panel { background:var(--surface); border:1px solid var(--border); border-radius:var(--r); padding:14px; margin-bottom:12px; }
  .plbl  { font-size:10px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; color:var(--marsala); margin-bottom:12px; display:flex; align-items:center; gap:8px; }
  .plbl::after { content:''; flex:1; height:1px; background:var(--border); }

  /* FORM */
  .row { display:flex; gap:10px; margin-bottom:10px; }
  .col { flex:1; }
  .lbl { display:block; font-size:11px; font-weight:500; color:var(--text-m); margin-bottom:4px; }
  input[type=text], input[type=number], select {
    width:100%; background:var(--cream); border:1px solid var(--border-s); border-radius:6px;
    padding:7px 10px; font-family:var(--mono); font-size:12px; color:var(--text); outline:none; transition:.15s;
  }
  input:focus, select:focus { border-color:var(--marsala); }
  .btn { padding:8px 16px; border:none; border-radius:6px; font-family:var(--sans); font-size:12px; font-weight:600; cursor:pointer; transition:.15s; }
  .btn-p { background:var(--marsala); color:#fff; }
  .btn-p:hover { background:#6E2222; }
  .btn-g { background:var(--green); color:#fff; }
  .btn-g:hover { background:#1e5c38; }
  .btn-o { background:transparent; border:1px solid var(--marsala); color:var(--marsala); }
  .btn-o:hover { background:var(--marsala-xl); }
  .btn-a { background:var(--amber-bg); border:1px solid var(--amber); color:var(--amber); }
  .btn:active { transform:scale(.97); }
  .btn-sm { padding:5px 12px; font-size:11px; }
  .btn-row { display:flex; gap:8px; flex-wrap:wrap; }

  /* STATS */
  .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:12px; }
  .scard { background:var(--surface); border:1px solid var(--border); border-radius:var(--r); padding:10px 12px; }
  .slbl { font-size:10px; color:var(--text-m); text-transform:uppercase; letter-spacing:.8px; margin-bottom:2px; }
  .sval { font-family:var(--mono); font-size:22px; font-weight:500; color:var(--marsala); }
  .sval.g { color:var(--green); }
  .sval.a { color:var(--amber); }
  .sval.m { color:var(--text-m); }

  /* STAGES */
  .stages { display:grid; grid-template-columns:repeat(6,1fr); gap:8px; margin-bottom:12px; }
  @media(max-width:900px){ .stages{grid-template-columns:repeat(3,1fr);} .stats{grid-template-columns:repeat(2,1fr);} }
  .stage { background:var(--surface2); border:1.5px solid var(--border); border-radius:var(--r); padding:10px 8px; text-align:center; min-height:92px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:5px; transition:.3s; position:relative; }
  .stage.occ { background:var(--marsala-xl); border-color:var(--marsala-mid); }
  .snum { position:absolute; top:5px; left:7px; font-family:var(--mono); font-size:9px; color:var(--text-h); }
  .sname { font-size:9px; font-weight:600; letter-spacing:.5px; text-transform:uppercase; color:var(--text-m); line-height:1.2; }
  .schassi { font-family:var(--mono); font-size:10px; color:var(--marsala); font-weight:500; }
  .stimer  { font-family:var(--mono); font-size:17px; font-weight:500; color:var(--amber); }
  .sempty  { font-size:10px; color:var(--border-s); font-family:var(--mono); }

  /* QUEUE */
  .chips { display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }
  .chip  { font-family:var(--mono); font-size:10px; background:var(--surface2); border:1px solid var(--border-s); border-radius:4px; padding:2px 7px; color:var(--text-m); }

  /* LOG */
  .log { background:var(--cream); border:1px solid var(--border); border-radius:6px; height:220px; overflow-y:auto; font-family:var(--mono); font-size:11px; padding:8px; }
  .log-lg { height:340px; }
  .log::-webkit-scrollbar { width:3px; }
  .log::-webkit-scrollbar-thumb { background:var(--border-s); border-radius:2px; }
  .lentry { display:grid; grid-template-columns:55px 130px 1fr 100px 85px; gap:8px; padding:3px 0; border-bottom:1px solid var(--border); align-items:center; }
  .lt  { color:var(--text-h); }
  .ltp { color:var(--text-m); font-size:9px; }
  .lch { color:var(--marsala); }
  .ls  { color:var(--text); font-size:10px; }
  .lin { color:var(--amber); font-weight:500; }
  .lfn { color:var(--green); font-weight:500; }
  .badge { font-size:9px; font-weight:600; padding:2px 6px; border-radius:3px; text-transform:uppercase; }
  .bv  { background:var(--marsala-xl); color:var(--marsala); }
  .bp  { background:var(--amber-bg);   color:var(--amber); }
  .bok { background:var(--green-bg);   color:var(--green); }

  /* SECTION */
  .sec { display:none; }
  .sec.active { display:block; }

  /* TOAST */
  #toast { position:fixed; bottom:20px; right:20px; background:var(--marsala); color:#fff; padding:10px 16px; border-radius:var(--r); font-size:12px; font-weight:500; display:none; z-index:999; animation:sin .2s ease; }
  @keyframes sin { from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1} }
</style>
</head>
<body>
<div class="app">

  <div class="hdr">
    <div class="brand">
      <div class="brand-icon">⚙</div>
      <div>
        <div class="brand-text">SENAI · Linha de Produção</div>
        <div class="brand-sub">Simulador MQTT Industrial</div>
      </div>
    </div>
    <div class="pills">
      <div class="pill"><div class="dot ok" id="dot-mqtt"></div><span id="lbl-mqtt">MQTT</span></div>
      <div class="pill"><div class="dot" id="dot-sim"></div><span id="lbl-sim">SIMULAÇÃO</span></div>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('producao')">Linha de Produção</button>
    <button class="tab" onclick="switchTab('logistica')">Logística &amp; Entrega</button>
    <button class="tab" onclick="switchTab('log')">Log de Eventos</button>
  </div>

  <!-- ===== PRODUÇÃO ===== -->
  <div id="sec-producao" class="sec active">

    <div class="panel">
      <div class="plbl">Entrada de Veículos</div>
      <div class="row">
        <div class="col">
          <label class="lbl">Chassi (manual)</label>
          <input type="text" id="inp-chassi" placeholder="Ex: VW-2024-001" />
        </div>
        <div class="col">
          <label class="lbl">Tópico MQTT</label>
          <input type="text" id="inp-topic-prod" value="senai/producao/linha" />
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label class="lbl">Lote automático (qtd)</label>
          <input type="number" id="inp-lote" placeholder="Ex: 5" min="1" max="50" />
        </div>
        <div class="col">
          <label class="lbl">Intervalo automático (seg)</label>
          <input type="number" id="inp-intervalo" value="8" min="3" max="60" />
        </div>
      </div>
      <div class="btn-row">
        <button class="btn btn-p btn-sm" onclick="enviarManual()">▶ Enviar Manual</button>
        <button class="btn btn-o btn-sm" onclick="enviarLote()">▶ Enviar Lote</button>
        <button class="btn btn-a btn-sm" id="btn-auto" onclick="toggleAuto()">⟳ Iniciar Automático</button>
      </div>
    </div>

    <div class="stats">
      <div class="scard"><div class="slbl">Na Fila</div><div class="sval a" id="s-fila">0</div></div>
      <div class="scard"><div class="slbl">Em Processo</div><div class="sval"     id="s-proc">0</div></div>
      <div class="scard"><div class="slbl">Finalizados</div><div class="sval g"   id="s-fin">0</div></div>
      <div class="scard"><div class="slbl">Msgs Pub.</div><div class="sval m"     id="s-msgs">0</div></div>
    </div>

    <div class="panel">
      <div class="plbl">Estado da Linha — Tempo Real</div>
      <div class="stages" id="stages"></div>
      <div>
        <span style="font-size:10px;color:var(--text-m);text-transform:uppercase;letter-spacing:.8px;font-weight:600;">Fila de Entrada</span>
        <div class="chips" id="queue-chips">
          <span style="font-size:10px;color:var(--text-h);font-family:var(--mono);">Nenhum veículo aguardando</span>
        </div>
      </div>
    </div>

  </div>

  <!-- ===== LOGÍSTICA ===== -->
  <div id="sec-logistica" class="sec">

    <div class="panel">
      <div class="plbl">Envio para Concessionária</div>
      <div class="row">
        <div class="col">
          <label class="lbl">Tipo</label>
          <select id="log-tipo">
            <option value="veiculo">Veículo</option>
            <option value="peca">Peça / Componente</option>
          </select>
        </div>
        <div class="col">
          <label class="lbl">ID / Chassi / Pedido</label>
          <input type="text" id="log-id" placeholder="Ex: VW-2024-001 ou SKU-0042" />
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label class="lbl">Concessionária destino</label>
          <input type="text" id="log-destino" placeholder="Ex: Concessionária Norte — SP" />
        </div>
        <div class="col">
          <label class="lbl">Tópico MQTT</label>
          <input type="text" id="log-topic" value="senai/logistica/entrega" />
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label class="lbl">Intervalo automático (seg)</label>
          <input type="number" id="log-intervalo" value="6" min="3" max="60" />
        </div>
      </div>
      <div class="btn-row">
        <button class="btn btn-p btn-sm" onclick="enviarLogManual()">▶ Enviar Despacho</button>
        <button class="btn btn-a btn-sm" id="btn-auto-log" onclick="toggleAutoLog()">⟳ Automático</button>
      </div>
    </div>

    <div class="stats">
      <div class="scard"><div class="slbl">Veículos Enviados</div><div class="sval g" id="ls-veic">0</div></div>
      <div class="scard"><div class="slbl">Peças Enviadas</div>   <div class="sval"   id="ls-peca">0</div></div>
      <div class="scard"><div class="slbl">Total Despachado</div> <div class="sval m" id="ls-total">0</div></div>
      <div class="scard"><div class="slbl">Em Trânsito</div>      <div class="sval a" id="ls-transit">0</div></div>
    </div>

    <div class="panel">
      <div class="plbl">Log de Despachos</div>
      <div class="log" id="log-logistica">
        <div style="font-family:var(--mono);font-size:11px;color:var(--text-h);text-align:center;margin-top:60px;">Nenhum despacho realizado</div>
      </div>
    </div>

  </div>

  <!-- ===== LOG GERAL ===== -->
  <div id="sec-log" class="sec">
    <div class="panel">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <div class="plbl" style="margin-bottom:0;">Log Completo de Eventos MQTT</div>
        <div style="display:flex;gap:8px;align-items:center;">
          <select id="log-filter" style="width:auto;padding:4px 8px;font-size:11px;">
            <option value="todos">Todos os tópicos</option>
            <option value="producao">Produção</option>
            <option value="logistica">Logística</option>
          </select>
          <button class="btn btn-sm btn-o" onclick="limparLog()">Limpar</button>
        </div>
      </div>
      <div class="log log-lg" id="log-full"></div>
    </div>
  </div>

</div>
<div id="toast"></div>

<script>
const ETAPAS_LABELS = {{ etapas_labels | tojson }};

// ── utilidades ──
function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  clearTimeout(t._t);
  t._t = setTimeout(() => t.style.display='none', 2500);
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.sec').forEach(s => s.classList.remove('active'));
  const tabs = ['producao','logistica','log'];
  document.querySelectorAll('.tab')[tabs.indexOf(name)].classList.add('active');
  document.getElementById('sec-'+name).classList.add('active');
}

// ── produção ──
async function enviarManual() {
  const chassi = document.getElementById('inp-chassi').value.trim();
  const topic  = document.getElementById('inp-topic-prod').value.trim();
  const r = await fetch('/api/enviar', {
    method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({chassi, topic})
  });
  const d = await r.json();
  toast(d.message);
  if (d.ok) document.getElementById('inp-chassi').value = '';
}

async function enviarLote() {
  const qtd   = parseInt(document.getElementById('inp-lote').value) || 0;
  const topic = document.getElementById('inp-topic-prod').value.trim();
  if (qtd < 1) { toast('Informe uma quantidade válida'); return; }
  const r = await fetch('/api/lote', {
    method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({qtd, topic})
  });
  const d = await r.json();
  toast(d.message);
  if (d.ok) document.getElementById('inp-lote').value = '';
}

let autoAtivo = false;
async function toggleAuto() {
  const intervalo = parseInt(document.getElementById('inp-intervalo').value) || 8;
  const r = await fetch('/api/auto_producao', {
    method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ativo: !autoAtivo, intervalo})
  });
  const d = await r.json();
  autoAtivo = d.ativo;
  const btn = document.getElementById('btn-auto');
  if (autoAtivo) {
    btn.textContent = '⏹ Parar Automático';
    btn.className = 'btn btn-sm';
    btn.style.cssText = 'background:var(--marsala-xl);border:1px solid var(--marsala);color:var(--marsala);';
  } else {
    btn.textContent = '⟳ Iniciar Automático';
    btn.className = 'btn btn-a btn-sm';
    btn.style.cssText = '';
  }
  toast(d.message);
}

// ── logística ──
async function enviarLogManual() {
  const tipo    = document.getElementById('log-tipo').value;
  const id_item = document.getElementById('log-id').value.trim();
  const destino = document.getElementById('log-destino').value.trim();
  const topic   = document.getElementById('log-topic').value.trim();
  const r = await fetch('/api/logistica', {
    method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({tipo, id_item, destino, topic})
  });
  const d = await r.json();
  toast(d.message);
  if (d.ok) {
    document.getElementById('log-id').value = '';
    document.getElementById('log-destino').value = '';
  }
}

let autoLogAtivo = false;
async function toggleAutoLog() {
  const intervalo = parseInt(document.getElementById('log-intervalo').value) || 6;
  const r = await fetch('/api/auto_logistica', {
    method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ativo: !autoLogAtivo, intervalo})
  });
  const d = await r.json();
  autoLogAtivo = d.ativo;
  const btn = document.getElementById('btn-auto-log');
  if (autoLogAtivo) {
    btn.textContent = '⏹ Parar Auto';
    btn.style.cssText = 'background:var(--marsala-xl);border:1px solid var(--marsala);color:var(--marsala);';
  } else {
    btn.textContent = '⟳ Automático';
    btn.style.cssText = '';
    btn.className = 'btn btn-a btn-sm';
  }
  toast(d.message);
}

// ── log ──
function limparLog() {
  fetch('/api/limpar_log', {method:'POST'});
}

// ── render ──
function renderStages(estado) {
  const g = document.getElementById('stages');
  g.innerHTML = '';
  estado.linha.forEach((chassi, i) => {
    const d = document.createElement('div');
    d.className = 'stage' + (chassi ? ' occ' : '');
    d.innerHTML = `<span class="snum">${String(i+1).padStart(2,'0')}</span>
      <div class="sname">${ETAPAS_LABELS[i]}</div>
      ${chassi
        ? `<div class="schassi">${chassi}</div><div class="stimer">${estado.tempo_restante[i]}s</div>`
        : `<div class="sempty">— vazio —</div>`}`;
    g.appendChild(d);
  });
}

function renderQueue(fila) {
  const el = document.getElementById('queue-chips');
  if (!fila.length) {
    el.innerHTML = '<span style="font-size:10px;color:var(--text-h);font-family:var(--mono);">Nenhum veículo aguardando</span>';
    return;
  }
  el.innerHTML = fila.slice(0,15).map(c => `<div class="chip">${c}</div>`).join('');
  if (fila.length > 15) el.innerHTML += `<div class="chip">+${fila.length-15}</div>`;
}

function entryProd(e) {
  return `<div class="lentry">
    <span class="lt">${e.time}</span>
    <span class="ltp">${e.topic}</span>
    <span class="lch">${e.chassi||''}</span>
    <span class="ls">${(e.etapa||'').replace(/_/g,' ')}</span>
    <span class="${e.status==='INICIADO'?'lin':'lfn'}">${e.status||''}</span>
  </div>`;
}

function entryLog(e) {
  return `<div class="lentry" style="grid-template-columns:55px 130px 1fr 65px 70px;">
    <span class="lt">${e.time}</span>
    <span class="ltp">${e.topic}</span>
    <span style="font-size:10px;color:var(--text);">${e.id||''} → ${e.destino||''}</span>
    <span class="badge ${e.tipo==='veiculo'?'bv':'bp'}">${e.tipo||''}</span>
    <span class="badge bok">DESPACHADO</span>
  </div>`;
}

async function atualizar() {
  try {
    const r  = await fetch('/api/estado');
    const d  = await r.json();

    // stages e fila
    renderStages(d);
    renderQueue(d.fila);

    // stats produção
    document.getElementById('s-fila').textContent = d.fila.length;
    document.getElementById('s-proc').textContent = d.linha.filter(Boolean).length;
    document.getElementById('s-fin').textContent  = d.finalizados;
    document.getElementById('s-msgs').textContent = d.msg_count;

    // stats logística
    document.getElementById('ls-veic').textContent    = d.ls_veic;
    document.getElementById('ls-peca').textContent    = d.ls_peca;
    document.getElementById('ls-total').textContent   = d.ls_veic + d.ls_peca;
    document.getElementById('ls-transit').textContent = d.ls_transit;

    // status dots
    const dotSim = document.getElementById('dot-sim');
    const lblSim = document.getElementById('lbl-sim');
    if (d.simulacao_ativa) { dotSim.className='dot run'; lblSim.textContent='ATIVA'; }
    else                   { dotSim.className='dot';     lblSim.textContent='PARADA'; }

    document.getElementById('dot-mqtt').className = d.mqtt_connected ? 'dot ok' : 'dot';
    document.getElementById('lbl-mqtt').textContent = d.mqtt_connected ? 'MQTT' : 'MQTT (off)';

    // log logística
    const logList = d.historico.filter(e => (e.topic||'').includes('logistica')).reverse();
    const elLog   = document.getElementById('log-logistica');
    elLog.innerHTML = logList.length
      ? logList.slice(0,50).map(entryLog).join('')
      : '<div style="font-family:var(--mono);font-size:11px;color:var(--text-h);text-align:center;margin-top:60px;">Nenhum despacho realizado</div>';

    // log completo
    const filter = document.getElementById('log-filter').value;
    const all    = [...d.historico].reverse();
    const filt   = filter==='todos' ? all
      : filter==='producao'  ? all.filter(e=>(e.topic||'').includes('producao'))
      : all.filter(e=>(e.topic||'').includes('logistica'));
    const elFull = document.getElementById('log-full');
    elFull.innerHTML = filt.length
      ? filt.slice(0,100).map(e => (e.topic||'').includes('logistica') ? entryLog(e) : entryProd(e)).join('')
      : '<div style="font-family:var(--mono);font-size:11px;color:var(--text-h);text-align:center;margin-top:60px;">Sem eventos</div>';

  } catch(e) {}
}

setInterval(atualizar, 1000);
atualizar();
</script>
</body>
</html>
"""

# -------------------------------------------------------
# FLASK — ROTAS
# -------------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML, etapas_labels=ETAPAS_LABELS)


@app.route("/api/estado")
def api_estado():
    with lock:
        return jsonify({
            "linha":           list(linha),
            "tempo_restante":  list(tempo_restante),
            "fila":            list(fila_entrada),
            "finalizados":     carros_finalizados,
            "simulacao_ativa": simulacao_ativa,
            "historico":       list(historico[-100:]),
            "msg_count":       msg_count,
            "ls_veic":         ls_veic,
            "ls_peca":         ls_peca,
            "ls_transit":      ls_transit,
            "mqtt_connected":  mqtt_connected,
        })


@app.route("/api/enviar", methods=["POST"])
def api_enviar():
    data   = request.get_json()
    chassi = (data.get("chassi") or "").strip() or gerar_chassi()
    with lock:
        fila_entrada.append(chassi)
    garantir_thread()
    return jsonify({"ok": True, "message": f"{chassi} adicionado à fila de produção."})


@app.route("/api/lote", methods=["POST"])
def api_lote():
    data = request.get_json()
    qtd  = int(data.get("qtd", 0))
    if qtd < 1:
        return jsonify({"ok": False, "message": "Quantidade inválida."})
    with lock:
        for _ in range(qtd):
            fila_entrada.append(gerar_chassi())
    garantir_thread()
    return jsonify({"ok": True, "message": f"{qtd} veículos adicionados à fila."})


@app.route("/api/auto_producao", methods=["POST"])
def api_auto_producao():
    data      = request.get_json()
    ativo     = bool(data.get("ativo", False))
    intervalo = int(data.get("intervalo", 8))
    if ativo:
        iniciar_auto_producao(intervalo)
        return jsonify({"ok": True, "ativo": True,  "message": f"Automático iniciado ({intervalo}s)."})
    else:
        parar_auto_producao()
        return jsonify({"ok": True, "ativo": False, "message": "Automático parado."})


@app.route("/api/logistica", methods=["POST"])
def api_logistica():
    global ls_veic, ls_peca
    data    = request.get_json()
    tipo    = data.get("tipo", "veiculo")
    id_item = (data.get("id_item") or "").strip() or (gerar_chassi() if tipo == "veiculo" else gerar_sku())
    destino = (data.get("destino") or "").strip() or random.choice(CONCESSIONARIAS)
    topic   = (data.get("topic") or TOPIC_LOGISTICA).strip()
    _registrar_logistica(tipo, id_item, destino, topic)
    return jsonify({"ok": True, "message": f"Despacho registrado: {id_item} → {destino}"})


@app.route("/api/auto_logistica", methods=["POST"])
def api_auto_logistica():
    data      = request.get_json()
    ativo     = bool(data.get("ativo", False))
    intervalo = int(data.get("intervalo", 6))
    if ativo:
        iniciar_auto_logistica(intervalo)
        return jsonify({"ok": True, "ativo": True,  "message": f"Automático logística iniciado ({intervalo}s)."})
    else:
        parar_auto_logistica()
        return jsonify({"ok": True, "ativo": False, "message": "Automático logística parado."})


@app.route("/api/limpar_log", methods=["POST"])
def api_limpar_log():
    with lock:
        historico.clear()
    return jsonify({"ok": True})


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

if __name__ == "__main__":
    conectar_mqtt()
    print("Acesse: http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)