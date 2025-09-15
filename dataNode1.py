from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Carpeta donde se guardan los bloques
BLOCKS_DIR = "/opt/dfs/datanode/blocks"
os.makedirs(BLOCKS_DIR, exist_ok=True)

# ==== Guardar bloque ====
@app.route("/store_block", methods=["POST"])
def store_block():
    block_id = request.form["block_id"]
    file = request.files["file"]
    
    path = os.path.join(BLOCKS_DIR, block_id)
    file.save(path)

    return jsonify({"status": "ok", "message": f"Bloque {block_id} almacenado"})

# ==== Recuperar bloque ====
@app.route("/get_block/<block_id>", methods=["GET"])
def get_block(block_id):
    path = os.path.join(BLOCKS_DIR, block_id)
    if os.path.exists(path):
        return open(path, "rb").read()
    return jsonify({"status": "error", "message": "Bloque no encontrado"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9001)
