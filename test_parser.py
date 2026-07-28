from app.document_processing.pdf_parser import PDFParser

# Create parser object
parser = PDFParser()

# Give the path of any PDF in uploads folder
pdf_path = "uploads/Python Interview Questions.pdf"

# Extract text
pages = parser.extract_text(pdf_path)

print(f"Total Pages: {len(pages)}")

for page in pages:
    print("=" * 50)
    print(f"Page Number: {page['page_number']}")
    print(page["text"][:300])   # Print first 300 characters