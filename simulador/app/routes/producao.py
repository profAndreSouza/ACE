"""
Rotas da Linha de Produção.
Prefixo: /api/producao
"""

from flask import Blueprint, request, jsonify
from app.config import TOPIC_PRODUCAO
from app.services import producao_service as svc

producao_bp = Blueprint("producao", __name__)


@producao_bp.route("/enviar", methods=["POST"])
def enviar():
    """Adiciona um único veículo à fila de produção."""
    data   = request.get_json(silent=True) or {}
    chassi = svc.adicionar_chassi(
        chassi=data.get("chassi", ""),
        topic=data.get("topic", TOPIC_PRODUCAO),
    )
    return jsonify({"ok": True, "message": f"{chassi} adicionado à linha de produção."})


@producao_bp.route("/auto", methods=["POST"])
def auto():
    """Liga / desliga envio automático de veículos."""
    data      = request.get_json(silent=True) or {}
    ativo     = bool(data.get("ativo", False))
    intervalo = int(data.get("intervalo", 8))
    topic     = data.get("topic", TOPIC_PRODUCAO)

    if ativo:
        svc.iniciar_auto(intervalo, topic)
        return jsonify({"ok": True, "ativo": True,
                        "message": f"Automático iniciado (intervalo: {intervalo}s)."})
    else:
        svc.parar_auto()
        return jsonify({"ok": True, "ativo": False, "message": "Automático parado."})