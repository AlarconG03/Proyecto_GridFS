import requests
import os
import sys

# 🚨 ACTUALIZA ESTAS IPS CADA VEZ QUE CAMBIEN
NAMENODE = "http://3.95.216.105:8080"
DATANODES = [
    "http://44.223.28.235:9001",
    "http://54.91.84.222:9002",
    "http://44.220.163.122:9003"
]

# Alias para mostrar mensajes más claros
NODE_NAMES = {
    "http://44.223.28.235:9001": "DataNode-1",
    "http://54.91.84.222:9002": "DataNode-2",
    "http://44.220.163.122:9003": "DataNode-3"
}

username = None

def login(user, password):
    global username
    r = requests.post(f"{NAMENODE}/login", json={"username": user, "password": password})
    data = r.json()
    if data["status"] == "ok":
        username = user
        print("✅ Login correcto:", data["message"])
    else:
        print("❌ Error:", data["message"])

def logout():
    global username
    username = None
    print("👋 Sesión cerrada")

def ls():
    r = requests.get(f"{NAMENODE}/ls", params={"username": username})
    print("Archivos:", r.json()["files"])

def put(filename):
    if not os.path.exists(filename):
        print("Archivo no encontrado")
        return

    block_size = 5  # bytes (ejemplo pequeño)
    blocks = []
    with open(filename, "rb") as f:
        i = 0
        while chunk := f.read(block_size):
            block_id = f"{filename}_block{i}"
            datanode_url = DATANODES[i % len(DATANODES)]
            
            try:
                r = requests.post(f"{datanode_url}/store_block",
                                  files={"file": (block_id, chunk)},
                                  data={"block_id": block_id})
                print(f"📦 Enviado {block_id} → {NODE_NAMES.get(datanode_url, datanode_url)}: {r.json()['status']}")
                blocks.append({"bloque": block_id, "datanode": datanode_url})
            except Exception as e:
                print(f"⚠️ Error al enviar bloque {block_id} → {datanode_url}: {e}")
            i += 1

    requests.post(f"{NAMENODE}/put", json={"username": username, "filename": filename, "blocks": blocks})
    print("✅ Archivo registrado en el NameNode")

def get(filename, destino=None):
    r = requests.get(f"{NAMENODE}/get", params={"username": username, "filename": filename})
    data = r.json()

    if "status" in data and data["status"] == "error":
        print("❌", data["message"])
        return

    if not destino:
        destino = filename + ".out"

    ok_nodes = []
    failed_nodes = []

    print("📌 Mapa de bloques:")
    for block in data["blocks"]:
        print(f" - {block['bloque']} → {NODE_NAMES.get(block['datanode'], block['datanode'])}")

    with open(destino, "wb") as f:
        for block in data["blocks"]:
            url = f"{block['datanode']}/get_block/{block['bloque']}"
            try:
                content = requests.get(url, timeout=5).content
                f.write(content)
                ok_nodes.append(NODE_NAMES.get(block['datanode'], block['datanode']))
            except Exception:
                failed_nodes.append(NODE_NAMES.get(block['datanode'], block['datanode']))
                print(f"⚠️ Bloque {block['bloque']} falló en {NODE_NAMES.get(block['datanode'], block['datanode'])}")

    if failed_nodes:
        print(f"❌ Archivo incompleto.\n   ✔ Funcionaron: {set(ok_nodes)}\n   ❌ Fallaron: {set(failed_nodes)}")
    else:
        print(f"✅ Archivo reconstruido en {destino}")

def rm(filename):
    r = requests.delete(f"{NAMENODE}/rm", json={"username": username, "filename": filename})
    print(r.json())

# === CLI simple ===
if __name__ == "__main__":
    while True:
        cmd = input("DFS> ").split()
        if not cmd:
            continue
        if cmd[0] == "login":
            login(cmd[1], cmd[2])
        elif cmd[0] == "logout":
            logout()
        elif cmd[0] == "ls":
            ls()
        elif cmd[0] == "put":
            put(cmd[1])
        elif cmd[0] == "get":
            if len(cmd) == 2:
                get(cmd[1])
            else:
                get(cmd[1], cmd[2])
        elif cmd[0] == "rm":
            rm(cmd[1])
        elif cmd[0] == "exit":
            sys.exit()
