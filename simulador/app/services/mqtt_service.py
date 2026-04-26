"""
Serviço MQTT.
Conecta ao broker definido em config.py sem autenticação.
Reconecta automaticamente em caso de queda.
Se o broker não estiver disponível, a aplicação continua
funcionando normalmente (apenas sem publicação real).
"""

import json
import time
import threading
from datetime import datetime

from app.config import MQTT_BROKER, MQTT_PORT, MAX_HISTORICO
import app.state as state

try:
    import paho.mqtt.client as mqtt
    _PAHO_DISPONIVEL = True
except ImportError:
    _PAHO_DISPONIVEL = False

_client:    object = None
_conectado: bool   = False


# ── Callbacks ─────────────────────────────────────────

def _on_connect(client, userdata, flags, rc):
    global _conectado
    if rc == 0:
        _conectado = True
        print(f"[MQTT] Conectado a {MQTT_BROKER}:{MQTT_PORT}")
    else:
        _conectado = False
        print(f"[MQTT] Falha na conexão (rc={rc})")


def _on_disconnect(client, userdata, rc):
    global _conectado
    _conectado = False
    if rc != 0:
        print(f"[MQTT] Desconectado inesperadamente (rc={rc}) — aguardando reconexão...")


# ── Conexão ───────────────────────────────────────────

def conectar_mqtt() -> None:
    """
    Conecta ao broker MQTT sem autenticação.
    Ativa o loop de rede em background com reconexão automática.
    """
    global _client, _conectado

    if not _PAHO_DISPONIVEL:
        print("[MQTT] paho-mqtt não instalado — publicação desativada.")
        return

    try:
        _client = mqtt.Client(client_id="senai_producao", clean_session=True)
        _client.on_connect    = _on_connect
        _client.on_disconnect = _on_disconnect

        # reconexão automática: tenta entre 5 s e 30 s
        _client.reconnect_delay_set(min_delay=5, max_delay=30)

        _client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        _client.loop_start()   # thread de rede em background

    except Exception as exc:
        _conectado = False
        print(f"[MQTT] Broker indisponível ({MQTT_BROKER}:{MQTT_PORT}): {exc}")
        # tenta reconectar em background sem travar a aplicação
        threading.Thread(target=_loop_reconexao, daemon=True).start()


def _loop_reconexao() -> None:
    """Fica tentando reconectar enquanto não conseguir."""
    while not _conectado:
        time.sleep(10)
        print(f"[MQTT] Tentando reconectar a {MQTT_BROKER}:{MQTT_PORT}...")
        try:
            _client.reconnect()
        except Exception as exc:
            print(f"[MQTT] Reconexão falhou: {exc}")


def esta_conectado() -> bool:
    return _conectado


# ── Publicação ────────────────────────────────────────

def publicar(topic: str, payload: dict) -> None:
    """
    Serializa o payload em JSON, publica no broker (se conectado)
    e registra no histórico local independentemente.
    """
    msg = json.dumps(payload, ensure_ascii=False)

    if _conectado and _client:
        try:
            result = _client.publish(topic, msg, qos=1)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] Publicação enfileirada/falhou (rc={result.rc})")
        except Exception as exc:
            print(f"[MQTT] Erro ao publicar: {exc}")

    print(f"[PUB] {topic} → {msg}")

    # registra no histórico local sempre
    entry = {
        "time":  datetime.now().strftime("%H:%M:%S"),
        "topic": topic,
        **payload,
    }
    with state.lock:
        state.historico.append(entry)
        if len(state.historico) > MAX_HISTORICO:
            state.historico.pop(0)
        state.msg_count += 1
