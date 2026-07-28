import fitz  # PyMuPDF


class PDFParser:

    def extract_text(self, pdf_path: str):

        document = fitz.open(pdf_path)

        pages = []

        for page_number in range(len(document)):

            page = document[page_number]

            text = page.get_text("text")

            pages.append(
                {
                    "page_number": page_number + 1,
                    "text": text.strip()
                }
            )

        document.close()

        return pages