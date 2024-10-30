import Blockchain
from typing import Literal, Any
from flask import Flask, jsonify, request
from argparse import ArgumentParser
import requests
from requests import Response
import time
import os
from threading import Thread, Semaphore
import json
import re
import platform

# Alumnos del grupo
# Jorge Vančo San Pedro
# Pablo Tuñón Laguna

# Semaphores
mutex: Semaphore = Semaphore(1)


# Instancia del nodo
app = Flask(__name__)
# Instanciacion de la aplicacion
blockchain = Blockchain.Blockchain()

# Set that stores all nodes connected to de blockchain in the formal http://<ip>:<puerto>
read_nodes = set()
node_format_regex = re.compile(r"http://([0-9]{1,3}(\.[0-9]{1,3}){3}|localhost):[0-9]+")


# Para saber mi ip
mi_ip = "192.168.34.222"  # 192.168.56.1   # 192.168.56.1
puerto = 5000


@app.route("/system", methods=["GET"])
def get_system_info() -> tuple[Response, Literal[200]]:
    response = {
        "machine": platform.machine(),
        "system_name": platform.system(),
        "version": platform.version(),
    }
    return jsonify(response), 200


@app.route("/transacciones/nueva", methods=["POST"])
def new_transaction() -> (
    tuple[Literal["Faltan valores"], Literal[400]] | tuple[Response, Literal[201]]
):
    """Creacion de una nueva transaccion"""

    values = request.get_json()

    # Comprobamos que todos los datos de la transaccion estan
    required: list[str] = ["origen", "destino", "cantidad"]
    if not all(k in values for k in required):
        return "Faltan valores", 400

    # Creamos una nueva transaccion
    indice: int = blockchain.new_transaction(
        values["origen"], values["destino"], values["cantidad"]
    )
    response: dict[str, str] = {
        "mensaje": f"La transaccion se incluira en el bloque con indice {indice}"
    }

    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def complete_blockchain() -> tuple[Response, Literal[200]]:
    """Obtener la cadena de bloques completa"""

    response: dict[str, Any] = {
        "chain": [b.toDict() for b in blockchain.chain if b.hash is not None],
        "longitud": len(blockchain.chain),
    }  # Solamente permitimos la cadena de aquellos bloques finales que tienen hash

    return jsonify(response), 200


@app.route("/minar", methods=["GET"])
def mine() -> tuple[Response, Literal[200]]:
    """Minado de un nuevo bloque"""

    # No hay transacciones
    if len(blockchain.not_confirmed_transactions) == 0:
        response: dict[str, str] = {
            "mensaje": "No es posible crear un nuevo bloque. No hay transacciones"
        }
    else:
        # Hay transaccion, por lo tanto ademas de minar el bloque, recibimos recompensa
        if conflict_manager():
            previous_hash: str = blockchain.last_block.hash
            # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
            # Dejamos como origen el 0
            # Destino nuestra ip
            # Cantidad = 1
            blockchain.new_transaction("0", mi_ip, 1)
            new_block: Blockchain.Block() = blockchain.new_block(previous_hash)

            new_hash: str = blockchain.test_work(new_block)

            mutex.acquire()
            is_valid_block: bool = blockchain.add_block(new_block, new_hash)
            mutex.release()
            response = {"message": "New block mined", **new_block.toDict()}
            print(blockchain.not_confirmed_transactions)

        else:
            response = {
                "message": "Ha habido un conflicto. Esta cadena se ha actualizado con una version mas larga"
            }

    return jsonify(response), 200


def check_node_register_format(node: str) -> bool:
    match: re.Match[str] | None = node_format_regex.fullmatch(node)

    return match is not None


@app.route("/nodos/registrar", methods=["POST"])
def register_nodes_complete() -> (
    tuple[Literal["Error: No se ha proporcionado una lista de nodos"], Literal[400]]
    | tuple[Response, Literal[201]]
):
    """Creacion de un nuevo nodo en la red y actualizacion de la blockchain"""

    global blockchain
    global read_nodes

    values = request.get_json()

    nodos_nuevos: list = values.get("direccion_nodos")
    if nodos_nuevos is None:
        return "Error: No se ha proporcionado una lista de nodos", 400

    all_correct: bool = True
    all_correct: bool = all([check_node_register_format(node) for node in nodos_nuevos])

    mutex.acquire()

    i = 0
    while all_correct and i < len(nodos_nuevos):
        node = nodos_nuevos[i]
        all_correct = check_node_register_format(node)
        if all_correct:
            read_nodes.add(node)
            nodes_list = list((read_nodes | {f"http://{mi_ip}:{puerto}"}) - set(node))
            data: dict[str, list] = {
                "nodos_direcciones": nodes_list,
                "blockchain": [block.toDict() for block in blockchain.chain],
            }
            response = requests.post(
                node + "/nodos/registro_simple",
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )
            all_correct = response.status_code == 200
            i += 1

    mutex.release()

    if all_correct:
        response = {
            "mensaje": "Se han incluido nuevos nodos en la red",
            "nodos_totales": list(read_nodes),
        }

    else:
        response: dict[str, str] = {"mensaje": "Error notificando el nodo estipulado"}

    return jsonify(response), 201


@app.route("/nodos/registro_simple", methods=["POST"])
def registrar_nodo_actualiza_blockchain() -> (
    tuple[Literal["El blockchain de la red esta corrupto"], Literal[400]]
    | tuple[str, Literal[200]]
):
    """Registro de nodo en la red"""

    global blockchain
    global read_nodes

    read_json = request.get_json()
    nodes_addreses: set = set(read_json.get("nodos_direcciones"))
    read_nodes = read_nodes | nodes_addreses
    blockchain_leida: list = read_json.get("blockchain")

    if blockchain_leida is None:
        return "El blockchain de la red esta corrupto", 400

    else:
        blockchain = Blockchain.json_to_blockchain(blockchain_leida)
        if blockchain is None:
            return "El blockchain de la red esta corrupto", 400

    return (
        "La blockchain del nodo"
        + str(mi_ip)
        + ":"
        + str(puerto)
        + "ha sido correctamente actualizada",
        200,
    )


def security_copy() -> None:
    """Crea un fichero de copia de seguridad cada 60 segundos"""

    os.makedirs("./security_copies", exist_ok=True)
    active_copies = True

    while active_copies:
        time.sleep(60)

        mutex.acquire()

        actual_copy: dict = {}
        actual_copy["chain"] = [block.toDict() for block in blockchain.chain]
        actual_copy["length"] = len(blockchain.chain)
        actual_copy["date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        mutex.release()

        security_copy_name: str = f"security_copies/respaldo-nodo{mi_ip}-{puerto}.json"

        with open(security_copy_name, "w") as file:
            json.dump(actual_copy, file)


def conflict_manager():
    """
    Mecanismo para establecer el consenso y resolver los conflictos. 
    En caso de que una cadena de bloques sea mayor que la que se está
    comprobando, la cadena larga pasa a ser la nueva cadena.
    """

    global blockchain
    global read_nodes

    len_0 = len(blockchain.chain)
    actual_len = len(blockchain.chain)
    chains = []
    max_len_index = 0

    for node in read_nodes:
        veryfying_node = requests.get(node + "/chain")
        veryfying_node = veryfying_node.json()
        chains.append(veryfying_node)

        if veryfying_node["longitud"] > actual_len:
            max_len_index = chains.index(veryfying_node)
            actual_len = veryfying_node["longitud"]

    if len_0 != actual_len:
        blockchain = Blockchain.json_to_blockchain(chains[max_len_index]["chain"])

        return False

    return True


@app.route("/ping", methods=["POST"])
def ping() -> dict[str, Any]:
    """Envia un ping a todos los nodos de la red y recibe un pong con el tiempo que ha tardado en responder y su ip:port"""

    global read_nodes

    responses = []
    conncection_times = []

    for node in read_nodes:
        t0 = time.time()
        response = requests.post(
            node + "/pong",
            json={"ip:port": f"{mi_ip}:{puerto}", "message": "PING", "time": t0},
        )

        if response.status_code == 200:
            responses.append(response.json()["ip:port"])
            conncection_times.append(response.json()["time"])

    answer = {
        "host_node": f"{mi_ip}:{puerto}",
        "connected_nodes": responses,
        "Connection time for each node": conncection_times,
        "response": "All the nodes are connected"
        if len(responses) == len(read_nodes)
        else "Not all the nodes are connected",
    }

    return answer


@app.route("/pong", methods=["POST"])
def pong() -> tuple[dict, Literal[200]]:
    """Recibe un ping y responde con un pong, con el tiempo que ha tardado en responder y su ip:port"""

    host_request = request.get_json()
    answer = {
        "ip:port": f"{mi_ip}:{puerto}",
        "message": "PONG",
        "time": abs(time.time() - host_request["time"]),
    }

    return answer, 200


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--puerto", default=5000, type=int, help="puerto para escuchar"
    )

    args = parser.parse_args()
    puerto = args.puerto

    copy_maker = Thread(target=security_copy, args=())
    copy_maker.start()

    app.run(host="0.0.0.0", port=puerto)
    copy_maker.join()
