import chromadb
import ollama

CLIENT = chromadb.Client()
COLLECTION = CLIENT.create_collection(name="docs")


class EmbeddingsManager:
    def __init__(self):
        super().__init__()
        self.model = "embeddinggemma:latest"

    def embed(self, documents: list[str]):
        for i, doc in enumerate(documents):
            response = ollama.embed(model=self.model, input=doc)
            embedding = response["embeddings"]
            COLLECTION.add(ids=[str(i)], embeddings=embedding, documents=[doc])

    def retrieve(self, input_message: str) -> str:
        # Embed the input
        response = ollama.embed(model=self.model, input=input_message)

        query_embedding = response["embeddings"]
        # Retrieve the most relevant document
        results = COLLECTION.query(query_embeddings=query_embedding, n_results=1)

        return results["documents"][0][0]
