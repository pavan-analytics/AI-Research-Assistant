from app.document_processing.pdf_parser import PDFParser
from app.document_processing.chunker import DocumentChunker
from app.vector_store.chroma_store import ChromaVectorStore

parser = PDFParser()

chunker = DocumentChunker()

vector_store = ChromaVectorStore()

pages = parser.extract_text(
    "uploads/MAJOR DOCUMENT.pdf"
)

chunks = chunker.create_chunks(
    pages
)

vector_store.add_chunks(
    "MAJOR DOCUMENT.pdf",
    chunks
)

print("Embeddings stored successfully!")
print("Total Chunks:", len(chunks))