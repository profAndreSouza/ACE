"""
Rotas de Logística.
Prefixo: /api/logistica
"""

from flask import Blueprint, request, jsonify
from app.config import TOPIC_LOGISTICA
from app.services import logistica_service as svc

logistica_bp = Blueprint("logistica", __name__)


@logistica_bp.route("/despachar", methods=["POST"])
def despachar():
    """Registra um despacho de veículo ou peça."""
    data = request.get_json(silent=True) or {}

    resultado = svc.despachar(
        tipo=data.get("tipo", "veiculo"),
        id_item=data.get("id_item", ""),
        destino=data.get("destino", ""),
        topic=data.get("topic", TOPIC_LOGISTICA),
    )
    return jsonify({
        "ok":      True,
        "message": f"Despacho registrado: {resultado['id']} → {resultado['destino']}",
    })


@logistica_bp.route("/auto", methods=["POST"])
def auto():
    """Liga / desliga despacho automático."""
    data      = request.get_json(silent=True) or {}
    ativo     = bool(data.get("ativo", False))
    intervalo = int(data.get("intervalo", 6))
    topic     = data.get("topic", TOPIC_LOGISTICA)

    if ativo:
        svc.iniciar_auto(intervalo, topic)
        return jsonify({"ok": True, "ativo": True,
                        "message": f"Automático logística iniciado (intervalo: {intervalo}s)."})
    else:
        svc.parar_auto()
        return jsonify({"ok": True, "ativo": False, "message": "Automático logística parado."})
