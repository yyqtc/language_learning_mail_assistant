import chromadb
import json

config = json.load(open("./config.json", encoding="utf-8"))

def init_client():
    return chromadb.PersistentClient(path=config["CHROMA_DB_PATH"])

client = init_client()
