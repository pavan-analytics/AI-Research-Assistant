import chromadb
from sentence_transformers import SentenceTransformer


class ChromaVectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="data/vector_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="research_documents"
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def add_chunks(self, document_name, chunks):

        texts = []
        embeddings = []
        ids = []
        metadatas = []

        for chunk in chunks:

            texts.append(chunk["text"])

            embeddings.append(
                self.embedding_model.encode(
                    chunk["text"]
                ).tolist()
            )

            ids.append(
                f"{document_name}_{chunk['chunk_id']}"
            )

            metadatas.append(
                {
                    "document": document_name,
                    "page": chunk["page_number"]
                }
            )

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query, top_k=5):

        query_embedding = self.embedding_model.encode(
            query
        ).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results

    def get_document_chunks(self, document_name):

        results = self.collection.get(
            where={"document": document_name}
        )

        return results["documents"]