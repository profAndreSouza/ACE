"""
Serviço de Linha de Produção.
Gerencia a simulação tick-a-tick, a fila de entrada
e os modos manual e automático.
"""

import random
import threading
import time
from datetime import datetime

from app.config import ETAPAS, TEMPOS_MIN, TEMPOS_MAX, TOPIC_PRODUCAO
import app.state as state
from app.services.mqtt_service import publicar


# ── Helpers ───────────────────────────────────────────

def _ts() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _pub(chassi: str, etapa: str, status: str, topic: str) -> None:
    """Publica evento MQTT — chamado FORA do lock para evitar deadlock."""
    publicar(topic, {
        "chassi":    chassi,
        "etapa":     etapa,
        "status":    status,
        "timestamp": _ts(),
    })


# ── Tick ──────────────────────────────────────────────

def _tick(topic: str) -> list:
    """
    Um ciclo de 1 segundo na linha.
    Retorna lista de eventos a publicar — chamado COM lock adquirido,
    mas a publicação MQTT ocorre depois, fora do lock.
    """
    eventos = []

    # percorre de trás para frente para evitar conflito de posições
    for i in reversed(range(len(ETAPAS))):
        if state.linha[i] is None:
            continue

        state.tempo_restante[i] -= 1

        if state.tempo_restante[i] > 0:
            continue

        chassi = state.linha[i]
        eventos.append((chassi, ETAPAS[i], "FINALIZADO"))

        if i == len(ETAPAS) - 1:
            # última etapa — veículo sai da linha
            state.finalizados += 1
            state.linha[i] = None

        elif state.linha[i + 1] is None:
            # avança para a próxima etapa
            state.linha[i + 1]          = chassi
            state.tempo_restante[i + 1] = random.randint(
                TEMPOS_MIN[i + 1], TEMPOS_MAX[i + 1]
            )
            eventos.append((chassi, ETAPAS[i + 1], "INICIADO"))
            state.linha[i] = None
        # próxima etapa ocupada: chassi aguarda (permanece no slot)

    # entrada de novo veículo da fila quando etapa 0 estiver livre
    if state.fila_entrada and state.linha[0] is None:
        chassi              = state.fila_entrada.pop(0)
        state.linha[0]      = chassi
        state.tempo_restante[0] = random.randint(TEMPOS_MIN[0], TEMPOS_MAX[0])
        eventos.append((chassi, ETAPAS[0], "INICIADO"))

    return eventos


# ── Loop de simulação ─────────────────────────────────

_thread_sim: threading.Thread | None = None


def _loop_simulacao(topic: str) -> None:
    state.sim_ativa = True
    while True:
        # coleta eventos dentro do lock
        with state.lock:
            tem_trabalho = (
                any(c is not None for c in state.linha)
                or bool(state.fila_entrada)
            )
            if not tem_trabalho:
                state.sim_ativa = False
                break
            eventos = _tick(topic)

        # publica MQTT fora do lock (evita deadlock)
        for chassi, etapa, status in eventos:
            _pub(chassi, etapa, status, topic)

        time.sleep(1)


def garantir_simulacao(topic: str = TOPIC_PRODUCAO) -> None:
    """Garante que a thread de simulação está rodando."""
    global _thread_sim
    if not state.sim_ativa or _thread_sim is None or not _thread_sim.is_alive():
        _thread_sim = threading.Thread(
            target=_loop_simulacao, args=(topic,), daemon=True
        )
        _thread_sim.start()


# ── Modo automático ───────────────────────────────────

_auto_ativo         = False
_thread_auto: threading.Thread | None = None


def _loop_auto(intervalo: int, topic: str) -> None:
    while _auto_ativo:
        with state.lock:
            state.fila_entrada.append(state.gerar_chassi())
        garantir_simulacao(topic)
        time.sleep(intervalo)


def iniciar_auto(intervalo: int = 8, topic: str = TOPIC_PRODUCAO) -> None:
    global _auto_ativo, _thread_auto
    _auto_ativo  = True
    _thread_auto = threading.Thread(
        target=_loop_auto, args=(intervalo, topic), daemon=True
    )
    _thread_auto.start()


def parar_auto() -> None:
    global _auto_ativo
    _auto_ativo = False


def auto_esta_ativo() -> bool:
    return _auto_ativo


# ── API pública ───────────────────────────────────────

def adicionar_chassi(chassi: str, topic: str = TOPIC_PRODUCAO) -> str:
    """Adiciona um chassi à fila e garante que a simulação está rodando."""
    chassi = chassi.strip() or state.gerar_chassi()
    with state.lock:
        state.fila_entrada.append(chassi)
    garantir_simulacao(topic)
    return chassi