"""
Configurações centralizadas da aplicação.
Altere aqui sem precisar tocar nos serviços.
"""

# ── MQTT ──────────────────────────────────────────────
MQTT_BROKER = "mqtt"   # hostname do broker (sem autenticação)
MQTT_PORT   = 1883

TOPIC_PRODUCAO  = "senai/producao/linha"
TOPIC_LOGISTICA = "senai/logistica/entrega"

# ── Linha de Produção ─────────────────────────────────
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

# Tempos mínimo e máximo (segundos) por etapa
TEMPOS_MIN = [2, 3, 3, 4, 2, 1]
TEMPOS_MAX = [5, 7, 6, 8, 5, 3]

# ── Logística ─────────────────────────────────────────
CONCESSIONARIAS = [
    "Ramires Toyota — Sorocaba/SP",
    "Toyota Nippokar — Itu/SP",
    "Toyota Germânica — Campinas/SP",
    "Niponsul Toyota — Porto Alegre/RS",
    "Toyolex — Recife/PE",
    "Tsusho — São Paulo/SP",
    "Daihatsu Toyota — Belo Horizonte/MG",
    "Noma Motors Toyota — Maringá/PR",
    "Car House Toyota — Porto Alegre/RS",
    "Toyopar — Londrina/PR"
]

# Tempo (s) para simular chegada do item ao destino
TEMPO_TRANSITO_S = 12

# ── Histórico ─────────────────────────────────────────
MAX_HISTORICO = 400
