import requests
import json


### VARIABLES GLOBALES
IP_HOST = "127.0.0.1"
PUERTO_HOST = 5000

IP_MAQUINA_VIRTUAL = "127.0.0.1"
PUERTO_MAQUINA_VIRTUAL = 5001


# Cabecera JSON (comun a todas)
cabecera: dict[str, str] = {"Content-type": "application/json", "Accept": "text/plain"}

nombres = {
    f"{IP_HOST}:{PUERTO_HOST}": "sistema host",
    f"{IP_MAQUINA_VIRTUAL}:{PUERTO_MAQUINA_VIRTUAL}": "máquina virtual",
}


def add_transaction(ip, port, imprimir=True):
    new_transaction = {
        "origen": "nodoA",
        "destino": "nodoB",
        "cantidad": 10,
    }  # nueva transaccion en sistema host
    r: requests.Response = requests.post(
        f"http://{ip}:{port}/transacciones/nueva",
        data=json.dumps(new_transaction),
        headers=cabecera,
    )
    if imprimir:
        name = nombres[f"{ip}:{port}"]
        print(f"Crear una transacción en {name}: ")
        print(r.text)


def minar_bloque(ip, port, imprimir=True):
    r: requests.Response = requests.get(
        f"http://{ip}:{port}/minar"
    )  # minar en sistema host
    if imprimir:
        name = nombres[f"{ip}:{port}"]
        print(f"Minar el bloque en {name}: ")
        print(r.text)


def get_chain(ip, port):
    r: requests.Response = requests.get(
        f"http://{ip}:{port}/chain"
    )  # obtener la cadena en la máquina virtual
    name = nombres[f"{ip}:{port}"]
    print(f"Obtener la cadena en {name}: ")
    print(r.text)


def registrar_nodos():
    nodes_register = {
        "direccion_nodos": [
            # f"http://{IP_MAQUINA_VIRTUAL}:5001",
            f"http://{IP_MAQUINA_VIRTUAL}:{PUERTO_MAQUINA_VIRTUAL}",
        ]
    }  # registrar nodos en el sistema host
    r: requests.Response = requests.post(
        f"http://{IP_HOST}:{PUERTO_HOST}/nodos/registrar",
        data=json.dumps(nodes_register),
        headers=cabecera,
    )  # obtener los nodos registrados en el sistema host
    print("Nodos registrados:")
    print(r.text)


if __name__ == "__main__":
    # datos transaccion
    add_transaction(IP_HOST, PUERTO_HOST)
    minar_bloque(IP_HOST, PUERTO_HOST)

    print("Intentar minar en máquina virtual sin transacciones:")
    minar_bloque(IP_MAQUINA_VIRTUAL, PUERTO_MAQUINA_VIRTUAL)

    add_transaction(IP_MAQUINA_VIRTUAL, PUERTO_MAQUINA_VIRTUAL)
    minar_bloque(IP_MAQUINA_VIRTUAL, PUERTO_MAQUINA_VIRTUAL)

    get_chain(IP_HOST, PUERTO_HOST)
    get_chain(IP_MAQUINA_VIRTUAL, PUERTO_MAQUINA_VIRTUAL)

    registrar_nodos()

    add_transaction(IP_HOST, PUERTO_HOST, False)
    minar_bloque(IP_MAQUINA_VIRTUAL, PUERTO_MAQUINA_VIRTUAL, True)

    for _ in range(3):
        add_transaction(IP_HOST, PUERTO_HOST, False)

    print("Añadidas varias transacciones a host y minados varios bloques en host:")
    minar_bloque(IP_HOST, PUERTO_HOST, True)

    add_transaction(IP_MAQUINA_VIRTUAL, PUERTO_MAQUINA_VIRTUAL)

    print("DEBERÍA SURGIR UN CONFLICTO AL INTENTAR MINAR EN LA MÁQUINA VIRTUAL:")
    minar_bloque(IP_MAQUINA_VIRTUAL, PUERTO_MAQUINA_VIRTUAL)

    r: requests.Response = requests.post(
        f"http://{IP_HOST}:{PUERTO_HOST}/ping"
    )  # ping de comunicación sistema host y usuarios
    print("Ping de comunicación sistema host y usuarios: ")
    print(r.text)

    r = requests.get(f"http://{IP_HOST}:{PUERTO_HOST}/system")
    print("Información del sistema host:")
    print(r.text)
