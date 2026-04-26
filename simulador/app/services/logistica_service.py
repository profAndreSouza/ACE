"""
Serviço de Logística.
Gerencia despachos de veículos e peças para concessionárias,
simulando o tempo em trânsito.
"""

import random
import threading
import time
from datetime import datetime

from app.config import CONCESSIONARIAS, TEMPO_TRANSITO_S, TOPIC_LOGISTICA
import app.state as state
from app.services.mqtt_service import publicar


# ── Helpers ───────────────────────────────────────────

def _ts() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


# ── Despacho ──────────────────────────────────────────

def despachar(
    tipo:    str,
    id_item: str = "",
    destino: str = "",
    topic:   str = TOPIC_LOGISTICA,
) -> dict:
    """
    Registra um despacho (veículo ou peça) e simula a chegada ao destino.
    Retorna um dict com os dados do despacho.
    """
    tipo    = tipo if tipo in ("veiculo", "peca") else "veiculo"
    id_item = id_item.strip() or (state.gerar_chassi() if tipo == "veiculo" else state.gerar_sku())
    destino = destino.strip() or random.choice(CONCESSIONARIAS)

    publicar(topic, {
        "id":        id_item,
        "tipo":      tipo,
        "destino":   destino,
        "status":    "DESPACHADO",
        "timestamp": _ts(),
    })

    with state.lock:
        if tipo == "veiculo":
            state.ls_veic += 1
        else:
            state.ls_peca += 1
        state.ls_transit += 1

    # simula chegada após TEMPO_TRANSITO_S segundos
    threading.Thread(target=_simular_chegada, daemon=True).start()

    return {"id": id_item, "tipo": tipo, "destino": destino}


def _simular_chegada() -> None:
    time.sleep(TEMPO_TRANSITO_S)
    with state.lock:
        state.ls_transit = max(0, state.ls_transit - 1)


# ── Modo automático ───────────────────────────────────

_auto_ativo          = False
_thread_auto: threading.Thread | None = None


def _loop_auto(intervalo: int, topic: str) -> None:
    while _auto_ativo:
        tipo    = random.choice(["veiculo", "peca"])
        id_item = state.gerar_chassi() if tipo == "veiculo" else state.gerar_sku()
        destino = random.choice(CONCESSIONARIAS)
        despachar(tipo, id_item, destino, topic)
        time.sleep(intervalo)


def iniciar_auto(intervalo: int = 6, topic: str = TOPIC_LOGISTICA) -> None:
    global _auto_ativo, _thread_auto
    _auto_ativo  = True
    _thread_auto = threading.Thread(target=_loop_auto, args=(intervalo, topic), daemon=True)
    _thread_auto.start()


def parar_auto() -> None:
    global _auto_ativo
    _auto_ativo = False


def auto_esta_ativo() -> bool:
    return _auto_ativo
