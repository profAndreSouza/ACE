"""
Estado global da aplicação.
Centralizado aqui para que todos os serviços compartilhem
o mesmo objeto sem importações circulares.
"""

import threading
from app.config import ETAPAS

# ── Sincronização ─────────────────────────────────────
lock = threading.Lock()

# ── Linha de Produção ─────────────────────────────────
linha:          list = [None] * len(ETAPAS)   # chassi em cada etapa
tempo_restante: list = [0]    * len(ETAPAS)   # segundos restantes
fila_entrada:   list = []                     # fila aguardando entrada

finalizados: int = 0
sim_ativa:   bool = False

# ── Logística ─────────────────────────────────────────
ls_veic:    int = 0
ls_peca:    int = 0
ls_transit: int = 0

# ── Geral ─────────────────────────────────────────────
historico:  list = []
msg_count:  int  = 0

# ── Contadores de ID ──────────────────────────────────
chassi_counter: int = 1
sku_counter:    int = 1


# ── Helpers de geração de IDs ─────────────────────────

def gerar_chassi() -> str:
    global chassi_counter
    c = f"TOY2026{str(chassi_counter).zfill(3)}"
    chassi_counter += 1
    return c


def gerar_sku() -> str:
    global sku_counter
    s = f"PD{str(sku_counter).zfill(4)}"
    sku_counter += 1
    return s
