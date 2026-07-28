from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(

            chunk_size=1000,

            chunk_overlap=150,

            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def create_chunks(self, pages):

        chunks = []

        chunk_id = 1

        for page in pages:

            texts = self.text_splitter.split_text(
                page["text"]
            )

            for text in texts:

                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "page_number": page["page_number"],
                        "text": text
                    }
                )

                chunk_id += 1

        return chunks