# Guía de Configuración del Sistema de Archivos Distribuido

Esta guía proporciona instrucciones paso a paso para configurar un Sistema de Archivos Distribuido (DFS) utilizando instancias EC2 de AWS con Ubuntu 22.04. La configuración incluye un NameNode, tres DataNodes y una instancia Cliente, todas configuradas con un Security Group compartido para la comunicación.

## Tabla de Contenidos
1. [Crear Instancias EC2](#paso-1-crear-instancias-ec2)
2. [Preparación Base (Todas las Instancias)](#paso-2-preparación-base-todas-las-instancias)
3. [Configurar NameNode](#paso-3-configurar-namenode)
4. [Configurar DataNodes](#paso-4-configurar-datanodes)
5. [Configurar Cliente](#paso-5-configurar-cliente)
6. [Flujo de Uso del DFS](#paso-6-flujo-de-uso-del-dfs)
7. [Nota Importante sobre IPs](#nota-importante-sobre-ips)

---

## Paso 1: Crear Instancias EC2

1. **Crear un Security Group** con las siguientes reglas:
   - **Reglas de Entrada**:
     - SSH (puerto 22): `0.0.0.0/0` (Anywhere IPv4)
     - TCP Personalizado (puerto 8080): `0.0.0.0/0`
     - TCP Personalizado (puerto 9001): `0.0.0.0/0`
     - TCP Personalizado (puerto 9002): `0.0.0.0/0`
     - TCP Personalizado (puerto 9003): `0.0.0.0/0`
   - **Reglas de Salida**:
     - Todo el tráfico: `0.0.0.0/0`

2. **Lanzar 5 Instancias EC2**:
   - Usa **Ubuntu 22.04** como AMI.
   - Nombra las instancias de la siguiente manera:
     - `dfs-namenode`
     - `dfs-datanode-1`
     - `dfs-datanode-2`
     - `dfs-datanode-3`
     - `dfs-client`
   - Asigna el mismo Security Group creado anteriormente a todas las instancias para permitir la comunicación interna.

---

## Paso 2: Preparación Base (Todas las Instancias)

Ejecuta los siguientes comandos en **todas las instancias** (`dfs-namenode`, `dfs-datanode-1`, `dfs-datanode-2`, `dfs-datanode-3`, `dfs-client`):

```bash
# Actualizar paquetes
sudo apt update && sudo apt -y upgrade

# Instalar Python y herramientas
sudo apt -y install python3-pip python3-venv

# (Opcional) Instalar Git si vas a clonar el repositorio
sudo apt -y install git
```

---

## Paso 3: Configurar NameNode

En la instancia `dfs-namenode`:

1. **Crear directorio del proyecto**:
   ```bash
   sudo mkdir -p /opt/dfs/namenode
   sudo chown -R ubuntu:ubuntu /opt/dfs/namenode
   ```

2. **Crear entorno virtual**:
   ```bash
   python3 -m venv /opt/dfs/namenode/venv
   source /opt/dfs/namenode/venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install flask
   ```

4. **Crear y poblar `app.py`**:
   - Crea el archivo `/opt/dfs/namenode/app.py`.
   - Copia el contenido de `NameNode.py` del repositorio en `/opt/dfs/namenode/app.py`.

5. **Ejecutar el servidor NameNode**:
   ```bash
   source /opt/dfs/namenode/venv/bin/activate
   python /opt/dfs/namenode/app.py
   ```

---

## Paso 4: Configurar DataNodes

En cada instancia DataNode (`dfs-datanode-1`, `dfs-datanode-2`, `dfs-datanode-3`):

1. **Crear directorio del proyecto**:
   ```bash
   sudo mkdir -p /opt/dfs/datanode/blocks
   sudo chown -R ubuntu:ubuntu /opt/dfs/datanode
   ```

2. **Crear entorno virtual**:
   ```bash
   python3 -m venv /opt/dfs/datanode/venv
   source /opt/dfs/datanode/venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install flask
   ```

4. **Crear y poblar `app.py`**:
   - Crea el archivo `/opt/dfs/datanode/app.py`.
   - Copia el contenido de `dataNode1.py`/`dataNode2.py`/`dataNode3.py` del repositorio en `/opt/dfs/datanode/app.py`, para su respectivo DataNode.

5. **Ejecutar el servidor DataNode**:
   ```bash
   source /opt/dfs/datanode/venv/bin/activate
   python /opt/dfs/datanode/app.py
   ```

---

## Paso 5: Configurar Cliente

En la instancia `dfs-client`:

1. **Crear directorio del proyecto**:
   ```bash
   sudo mkdir -p /opt/dfs/client
   sudo chown -R ubuntu:ubuntu /opt/dfs/client
   ```

2. **Crear entorno virtual**:
   ```bash
   python3 -m venv /opt/dfs/client/venv
   source /opt/dfs/client/venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install requests
   ```

4. **Crear y poblar `cli.py`**:
   - Crea el archivo `/opt/dfs/client/cli.py`.
   - Copia el contenido de `Client.py` del repositorio en `/opt/dfs/client/cli.py`.

5. **Actualizar direcciones IP en `cli.py`**:
   - Edita `cli.py` para incluir las direcciones IP públicas de:
     - NameNode (puerto `8080`)
     - DataNode-1 (puerto `9001`)
     - DataNode-2 (puerto `9002`)
     - DataNode-3 (puerto `9003`)

6. **Ejecutar el cliente**:
   ```bash
   source /opt/dfs/client/venv/bin/activate
   python /opt/dfs/client/cli.py
   ```

---

## Paso 6: Flujo de Uso del DFS

En la instancia `dfs-client`, interactúa con el DFS usando los siguientes comandos en la CLI:

```bash
DFS> login shakira 1234        # Autenticar usuario
DFS> put archivo.txt           # Subir archivo y distribuir bloques
DFS> ls                        # Listar archivos del usuario
DFS> get archivo.txt salida.txt # Recuperar archivo
DFS> rm archivo.txt            # Eliminar archivo
DFS> logout                    # Cerrar sesión
DFS> exit                      # Salir de la CLI
```

---

## Nota Importante sobre IPs

- **IPs Dinámicas**: Cada vez que reinicies las instancias EC2, las direcciones IP públicas pueden cambiar, a menos que uses Elastic IPs.
- **Actualizar IPs**: Después de un reinicio, actualiza las direcciones IP públicas en `/opt/dfs/client/cli.py` antes de ejecutar el cliente nuevamente.
