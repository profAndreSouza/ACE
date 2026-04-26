"""
Rotas de view (HTML) e estado global.
"""

from flask import Blueprint, render_template, jsonify
from app.config import ETAPAS_LABELS
import app.state as state
from app.services.mqtt_service import esta_conectado

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    return render_template("index.html", etapas_labels=ETAPAS_LABELS)


@views_bp.route("/api/estado")
def api_estado():
    with state.lock:
        return jsonify({
            "linha":           list(state.linha),
            "tempo_restante":  list(state.tempo_restante),
            "fila":            list(state.fila_entrada),
            "finalizados":     state.finalizados,
            "simulacao_ativa": state.sim_ativa,
            "historico":       list(state.historico[-100:]),
            "msg_count":       state.msg_count,
            "ls_veic":         state.ls_veic,
            "ls_peca":         state.ls_peca,
            "ls_transit":      state.ls_transit,
            "mqtt_connected":  esta_conectado(),
        })


@views_bp.route("/api/limpar_log", methods=["POST"])
def api_limpar_log():
    with state.lock:
        state.historico.clear()
    return jsonify({"ok": True})
