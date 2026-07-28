from app.vector_store.chroma_store import ChromaVectorStore

vector_store = ChromaVectorStore()

results = vector_store.search(

    "What are the advantages of Python?"

)

print(results)