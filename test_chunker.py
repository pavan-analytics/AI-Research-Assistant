from app.document_processing.pdf_parser import PDFParser
from app.document_processing.chunker import DocumentChunker

parser = PDFParser()

chunker = DocumentChunker()

pages = parser.extract_text(
    "uploads/Python Interview Questions.pdf"
)

chunks = chunker.create_chunks(
    pages
)

print(f"Total Pages : {len(pages)}")

print(f"Total Chunks : {len(chunks)}")

print("="*50)

print(chunks[0])