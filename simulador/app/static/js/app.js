/* ─────────────────────────────────────────────────────
   SENAI · Linha de Produção — frontend
   ───────────────────────────────────────────────────── */

// injetado pelo template (ver index.html)
// const ETAPAS_LABELS = [...];

// ── Estado local ──────────────────────────────────────
let autoProducaoAtivo  = false;
let autoLogisticaAtivo = false;

// ── Utilidades ────────────────────────────────────────

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => (t.style.display = 'none'), 2500);
}

function switchTab(name) {
  const tabs = ['producao', 'logistica', 'log'];
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.sec').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab')[tabs.indexOf(name)].classList.add('active');
  document.getElementById('sec-' + name).classList.add('active');
}

async function postJSON(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return r.json();
}

// ── Produção — ações ──────────────────────────────────

async function enviarManual() {
  const chassi = document.getElementById('inp-chassi').value.trim();
  const topic  = document.getElementById('inp-topic-prod').value.trim();
  const d = await postJSON('/api/producao/enviar', { chassi, topic });
  toast(d.message);
  if (d.ok) document.getElementById('inp-chassi').value = '';
}


async function toggleAuto() {
  const intervalo = parseInt(document.getElementById('inp-intervalo').value) || 8;
  const topic     = document.getElementById('inp-topic-prod').value.trim();
  const d = await postJSON('/api/producao/auto', {
    ativo: !autoProducaoAtivo, intervalo, topic,
  });
  autoProducaoAtivo = d.ativo;
  const btn = document.getElementById('btn-auto');
  if (autoProducaoAtivo) {
    btn.textContent = '⏹ Parar Automático';
    btn.style.cssText = 'background:var(--marsala-xl);border:1px solid var(--marsala);color:var(--marsala);';
  } else {
    btn.textContent  = '⟳ Iniciar Automático';
    btn.className    = 'btn btn-a btn-sm';
    btn.style.cssText = '';
  }
  toast(d.message);
}

// ── Logística — ações ─────────────────────────────────

async function enviarDespacho() {
  const tipo    = document.getElementById('log-tipo').value;
  const id_item = document.getElementById('log-id').value.trim();
  const destino = document.getElementById('log-destino').value.trim();
  const topic   = document.getElementById('log-topic').value.trim();
  const d = await postJSON('/api/logistica/despachar', { tipo, id_item, destino, topic });
  toast(d.message);
  if (d.ok) {
    document.getElementById('log-id').value      = '';
    document.getElementById('log-destino').value = '';
  }
}

async function toggleAutoLog() {
  const intervalo = parseInt(document.getElementById('log-intervalo').value) || 6;
  const topic     = document.getElementById('log-topic').value.trim();
  const d = await postJSON('/api/logistica/auto', {
    ativo: !autoLogisticaAtivo, intervalo, topic,
  });
  autoLogisticaAtivo = d.ativo;
  const btn = document.getElementById('btn-auto-log');
  if (autoLogisticaAtivo) {
    btn.textContent  = '⏹ Parar Auto';
    btn.style.cssText = 'background:var(--marsala-xl);border:1px solid var(--marsala);color:var(--marsala);';
  } else {
    btn.textContent  = '⟳ Automático';
    btn.className    = 'btn btn-a btn-sm';
    btn.style.cssText = '';
  }
  toast(d.message);
}

// ── Log ───────────────────────────────────────────────

async function limparLog() {
  await fetch('/api/limpar_log', { method: 'POST' });
}

// ── Render ────────────────────────────────────────────

function renderStages(estado) {
  const g = document.getElementById('stages');
  g.innerHTML = '';
  estado.linha.forEach((chassi, i) => {
    const div = document.createElement('div');
    div.className = 'stage' + (chassi ? ' occ' : '');
    div.innerHTML = `
      <span class="snum">${String(i + 1).padStart(2, '0')}</span>
      <div class="sname">${ETAPAS_LABELS[i]}</div>
      ${chassi
        ? `<div class="schassi">${chassi}</div><div class="stimer">${estado.tempo_restante[i]}s</div>`
        : `<div class="sempty">— vazio —</div>`}`;
    g.appendChild(div);
  });
}

function renderQueue(fila) {
  const el = document.getElementById('queue-chips');
  if (!fila.length) {
    el.innerHTML = '<span style="font-size:10px;color:var(--text-h);font-family:var(--mono);">Nenhum veículo aguardando</span>';
    return;
  }
  el.innerHTML = fila.slice(0, 15).map(c => `<div class="chip">${c}</div>`).join('');
  if (fila.length > 15) el.innerHTML += `<div class="chip">+${fila.length - 15}</div>`;
}

function entryProd(e) {
  return `<div class="lentry">
    <span class="lt">${e.time}</span>
    <span class="ltp">${e.topic}</span>
    <span class="lch">${e.chassi || ''}</span>
    <span class="ls">${(e.etapa || '').replace(/_/g, ' ')}</span>
    <span class="${e.status === 'INICIADO' ? 'lin' : 'lfn'}">${e.status || ''}</span>
  </div>`;
}

function entryLog(e) {
  return `<div class="lentry" style="grid-template-columns:55px 130px 1fr 65px 70px;">
    <span class="lt">${e.time}</span>
    <span class="ltp">${e.topic}</span>
    <span style="font-size:10px;color:var(--text);">${e.id || ''} → ${e.destino || ''}</span>
    <span class="badge ${e.tipo === 'veiculo' ? 'bv' : 'bp'}">${e.tipo || ''}</span>
    <span class="badge bok">DESPACHADO</span>
  </div>`;
}

function isLogistica(e) {
  return (e.topic || '').includes('logistica');
}

// ── Loop de atualização ───────────────────────────────

async function atualizar() {
  try {
    const r = await fetch('/api/estado');
    const d = await r.json();

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

    // dots de status
    const dotSim = document.getElementById('dot-sim');
    const lblSim = document.getElementById('lbl-sim');
    if (d.simulacao_ativa) { dotSim.className = 'dot run'; lblSim.textContent = 'ATIVA';  }
    else                   { dotSim.className = 'dot';     lblSim.textContent = 'PARADA'; }

    document.getElementById('dot-mqtt').className   = d.mqtt_connected ? 'dot ok' : 'dot';
    document.getElementById('lbl-mqtt').textContent = d.mqtt_connected ? 'MQTT' : 'MQTT (off)';

    // log logística
    const logList = [...d.historico].reverse().filter(isLogistica);
    const elLog   = document.getElementById('log-logistica');
    elLog.innerHTML = logList.length
      ? logList.slice(0, 50).map(entryLog).join('')
      : '<div style="font-family:var(--mono);font-size:11px;color:var(--text-h);text-align:center;margin-top:60px;">Nenhum despacho realizado</div>';

    // log completo
    const filtro = document.getElementById('log-filter').value;
    const all    = [...d.historico].reverse();
    const filt   = filtro === 'todos'     ? all
      : filtro === 'producao'             ? all.filter(e => !isLogistica(e))
      : all.filter(isLogistica);

    const elFull = document.getElementById('log-full');
    elFull.innerHTML = filt.length
      ? filt.slice(0, 100).map(e => isLogistica(e) ? entryLog(e) : entryProd(e)).join('')
      : '<div style="font-family:var(--mono);font-size:11px;color:var(--text-h);text-align:center;margin-top:60px;">Sem eventos</div>';

  } catch (_) { /* servidor indisponível momentaneamente */ }
}

setInterval(atualizar, 1000);
atualizar();