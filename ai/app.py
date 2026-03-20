from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "AI OK"})

@app.route("/recommend/<int:user_id>")
def recommend(user_id):
    # Simples mock
    return jsonify({
        "userId": user_id,
        "recommendedVehicle": "SUV - Modelo X"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)