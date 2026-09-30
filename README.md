# Blockchain-naive

A small blockchain in Python with a Flask node, written for a distributed systems course in October 2024. The authors are Pablo Tuñón Laguna and Jorge Vančo San Pedro, who worked as a pair (both names are in the header of each source file).

The assignment skeleton (the structure of the classes, the method signatures and the Spanish docstrings that describe them) belongs to the course, so this repository has no licence file. The implementation is the authors' work.

## Files

- `Blockchain.py`: the `Block`, `Transaction` and `Blockchain` classes. Blocks are hashed with SHA-256 over their JSON form. Proof of work searches for a hash with as many leading zeros as the difficulty, which is set to 4. `json_to_blockchain` rebuilds a chain from JSON and returns `None` when a block does not link to the previous hash.
- `Blockchain_app.py`: a Flask node that holds one `Blockchain`. Endpoints:
  - `POST /transacciones/nueva`: add a transaction with `origen`, `destino` and `cantidad`.
  - `GET /minar`: mine a block from the pending transactions. A reward transaction of 1 to the node's address is added first. Before mining, the node asks every registered node for its chain and keeps the longest one.
  - `GET /chain`: the confirmed chain and its length.
  - `POST /nodos/registrar` and `POST /nodos/registro_simple`: register other nodes and take over their chain.
  - `POST /ping` and `POST /pong`: measure the answer time of the registered nodes.
  - `GET /system`: machine, operating system and version.
  
  Every 60 seconds a thread writes the chain to `security_copies/`.
- `requests_blockchain.py`: a script that calls the endpoints of two local nodes (ports 5000 and 5001) to create transactions, mine, register nodes and trigger a chain conflict.
- `blockchain_test.py`: pytest tests for the chain. They were written against an earlier version of the class (they use `chain.lst`, while the code now uses `chain`) and one of them reads a backup file that is not in the repository, so they do not pass against the current code.
- `requirements_python3.10.8.txt`: pinned dependencies (Flask 3.0.0, requests 2.31.0 and their requirements).

## Running

```
pip install -r requirements_python3.10.8.txt
python Blockchain_app.py -p 5000
python Blockchain_app.py -p 5001
python requests_blockchain.py
```

The node address is set in `Blockchain_app.py` as `mi_ip`, which is a fixed LAN address, so change it to the machine's address before running across machines.
