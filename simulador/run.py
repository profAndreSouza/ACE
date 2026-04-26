"""
Entrypoint da aplicação SENAI · Linha de Produção.
Execute: python run.py
"""

from app import create_app
from app.services.mqtt_service import conectar_mqtt

app = create_app()

if __name__ == "__main__":
    conectar_mqtt()
    print("=" * 50)
    print("  SENAI · Linha de Produção")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=5000)
