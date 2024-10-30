import json
import hashlib
from typing import List, Any
import time

# Alumnos del grupo
# Jorge Vančo San Pedro
# Pablo Tuñón Laguna


class Block:
    def __init__(
        self,
        index: int,
        transactions: List,
        timestamp: float,
        previous_hash: str,
        test: int = 0,
    ) -> None:
        """
        Constructor de la clase `Bloque`.
        :param indice: ID unico del bloque.
        :param transacciones: Lista de transacciones.
        :param timestamp: Momento en que el bloque fue generado.
        :param hash_previo hash previo
        :param prueba: prueba de trabajo
        """

        self.index: int = index
        self.transactions: List = transactions
        self.timestamp: float = timestamp
        self.previous_hash: str = previous_hash
        self.test: int = test
        self.hash = None

    def calculate_hash(self) -> str:
        """
        Metodo que devuelve el hash de un bloque
        """
        block_string: str = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def toDict(self) -> dict[str, Any]:
        return self.__dict__

    def __repr__(self) -> str:
        return str(self.__dict__)


class Blockchain(object):
    def __init__(self) -> None:
        self.difficulty: int = 4
        self.chain = list()  # list that contains all blocks
        self.not_confirmed_transactions = list()
        # Initialize first block
        self.first_block()
        self.last_block: Block = self.chain[-1]

    def first_block(self) -> None:
        first = Block(1, None, time.time(), "1")
        first.hash = "1"
        self.chain.append(first)

    def new_block(self, previous_hash: str) -> Block:
        """
        Crea un nuevo bloque a partir de las transacciones que no estan
        confirmadas
        :param previous_hash: el hash del bloque anterior de la cadena
        :return: el nuevo bloque
        """

        block = Block(
            len(self.chain) + 1,
            self.not_confirmed_transactions.copy(),
            time.time(),
            previous_hash,
        )

        return block

    def new_transaction(self, origin: str, destiny: str, amount: int) -> int:
        """
        Crea una nueva transaccion a partir de un origen, un destino y una
        cantidad y la incluye en las
        listas de transacciones
        :param origen: <str> el que envia la transaccion
        :param destino: <str> el que recibe la transaccion
        :param cantidad: <int> la candidad
        :return: <int> el indice del bloque que va a almacenar la transaccion
        """

        transaction: dict[str, Any] = Transaction(
            origin, destiny, amount, time.time()
        ).__dict__
        self.not_confirmed_transactions.append(transaction)

        return self.not_confirmed_transactions.index(transaction)

    def test_work(self, block: Block) -> str:
        """
        Algoritmo simple de prueba de trabajo:
        - Calculara el hash del bloque hasta que encuentre un hash que empiece
        por tantos ceros como dificultad
        .
        - Cada vez que el bloque obtenga un hash que no sea adecuado,
        incrementara en uno el campo de
        ``prueba'' del bloque
        :param bloque: objeto de tipo bloque
        :return: el hash del nuevo bloque (dejara el campo de hash del bloque sin
        modificar)
        """

        while not self.valid_test(block, block.calculate_hash()):
            block.test += 1

        return block.calculate_hash()

    def valid_test(self, block: Block, block_hash: str) -> bool:
        """
        Metodo que comprueba si el block_hash comienza con tantos ceros como la
        dificultad estipulada en el
        blockchain
        Ademas comprobara que block_hash coincide con el valor devuelvo del
        metodo de calcular hash del bloque.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en caso
        contrario, verdarero
        :param block:
        :param block_hash:
        :return:
        """

        return (
            block_hash.startswith("0" * self.difficulty)
            and block.calculate_hash() == block_hash
        )

    def add_block(self, new_block: Block, test_hash: str) -> bool:
        """
        Metodo para integrar correctamente un bloque a la cadena de bloques.
        Debe comprobar que test_hash es valida y que el hash del bloque ultimo
        de la cadena coincida con el hash_previo del bloque que se va a integrar.
        Si pasa las comprobaciones, actualiza el hash del bloque nuevo a integrar
        con test_hash, lo inserta en la cadena y hace un reset de las transacciones
        no confirmadas (vuelve a dejar la lista de transacciones no confirmadas a una lista vacia)
        :param new_block: el nuevo bloque que se va a integrar
        :param test_hash: la prueba de hash
        :return: True si se ha podido ejecutar bien y False en caso contrario (si
        no ha pasado alguna prueba)
        """

        is_valid_block: bool = (
            self.valid_test(new_block, test_hash)
            and self.chain[-1].hash == new_block.previous_hash
        )

        if is_valid_block:
            new_block.hash = test_hash
            self.chain.append(new_block)
            self.not_confirmed_transactions: list = []
            self.last_block: Block = new_block

        return is_valid_block


class Transaction(object):
    def __init__(self, origin: str, destiny: str, amount: int, time: float) -> None:
        self.origin: str = origin
        self.destiny: str = destiny
        self.amount: int = amount
        self.time: float = time

    def __repr__(self) -> str:
        return str(self.__dict__)


def json_to_blockchain(block_chain) -> Blockchain:
    """
    Convierte un json que representa cadena en un objeto Blockchain

    :param block_chain: json de la cadena

    :return: objeto blockchain cuya chain es la del objeto json pasado
    """
    new_block_chain = Blockchain()
    chain = []
    for block in block_chain:
        new_block = Block(
            block["index"],
            block["transactions"],
            block["timestamp"],
            block["previous_hash"],
            test=block["test"],
        )
        if chain and chain[-1].hash != block["previous_hash"]:
            return
        new_block.hash = block["hash"]
        chain.append(new_block)
    new_block_chain.chain = chain
    new_block_chain.last_block: Block = chain[-1]
    return new_block_chain
