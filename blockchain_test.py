import Blockchain
import json

#Alumnos del grupo
#Jorge Vančo San Pedro
#Pablo Tuñón Laguna

def test_blockchain_creation() -> None:
    chain = Blockchain.Blockchain()
    assert len(chain.lst) == 1
    assert chain.lst[0].hash == "1"
    assert chain.lst[0].previous_hash == "1"


def test_blockchain_add_transaction() -> None:
    chain = Blockchain.Blockchain()

    transaction_index: int = chain.new_transaction("Jorge", "Pablo", 4)
    assert transaction_index == 0
    transaction_index: int = chain.new_transaction("Pablo", "Jorge", 1000)
    assert transaction_index == 1

    block: Blockchain.Block() = chain.new_block(chain.lst[0].hash)
    while not chain.valid_test(block, block.calculate_hash()):
        hash: str = chain.test_work(block)
    block.hash = hash
    assert block.hash.startswith("0" * chain.difficulty)
    assert len(block.transactions) == 2


def test_json_to_blockchain() -> None:
    with open("not_Security_copies/respaldo-nodo192.168.56.1-5000.json") as fh:
        my_json = json.load(fh)

    Blockchain.json_to_blockchain(my_json)
