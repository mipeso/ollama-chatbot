import chromadb
import ollama
from PyQt6.QtWidgets import QMainWindow

from chatbot.core.utils import read_file

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
        # Retrieve the most relevant document (n_results=1)
        results = COLLECTION.query(query_embeddings=query_embedding, n_results=1)

        return results["documents"][0][0]

    def retrieve_relevant_text(
        self, main_window: QMainWindow, file_path: str, question: str
    ) -> str | None:
        rag_data = read_file(main_window, file_path)
        self.embed(rag_data)
        retrieved_text = self.retrieve(question)

        # Return combined retrieved text and user input
        return "\n".join(retrieved_text) if retrieved_text else None
