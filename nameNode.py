from flask import Flask, request, jsonify
import hashlib

app = Flask(__name__)

# ==== Usuarios (con hash simple sha256) ====
USERS = {
    "shakira": hashlib.sha256("1234".encode()).hexdigest(),
    "petro": hashlib.sha256("5678".encode()).hexdigest()
}

# ==== Metadatos de archivos ====
# { "usuario": { "archivo": [ { "bloque": "id1", "datanode": "ip:puerto" }, ... ] } }
METADATA = {}

# ==== Login ====
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in USERS:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if hashed == USERS[username]:
            return jsonify({"status": "ok", "message": f"Bienvenido {username}"})
    
    return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401

# ==== Listar archivos ====
@app.route("/ls", methods=["GET"])
def list_files():
    username = request.args.get("username")
    if username not in METADATA:
        return jsonify({"files": []})
    return jsonify({"files": list(METADATA[username].keys())})

# ==== Registrar archivo ====
@app.route("/put", methods=["POST"])
def put_file():
    data = request.json
    username = data["username"]
    filename = data["filename"]
    blocks = data["blocks"]

    if username not in METADATA:
        METADATA[username] = {}

    METADATA[username][filename] = blocks

    return jsonify({"status": "ok", "message": f"Archivo {filename} registrado"})

# ==== Obtener bloques ====
@app.route("/get", methods=["GET"])
def get_file():
    username = request.args.get("username")
    filename = request.args.get("filename")

    if username in METADATA and filename in METADATA[username]:
        return jsonify({"blocks": METADATA[username][filename]})

    return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404

# ==== Eliminar archivo ====
@app.route("/rm", methods=["DELETE"])
def delete_file():
    data = request.json
    username = data["username"]
    filename = data["filename"]

    if username in METADATA and filename in METADATA[username]:
        del METADATA[username][filename]
        return jsonify({"status": "ok", "message": f"{filename} eliminado"})
    
    return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404

# ==== Arranque ====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
