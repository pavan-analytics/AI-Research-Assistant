from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.document_processing.pdf_parser import PDFParser
from app.document_processing.chunker import DocumentChunker
from app.vector_store.chroma_store import ChromaVectorStore
from app.rag.llm_service import LLMService
from app.ml.classifier import DocumentClassifier
from app.memory.conversation_memory import ConversationMemory

import shutil
import os

from app.database.database import get_db
from app.database.models import Document

memory = ConversationMemory()

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF files are allowed."
        }

    existing_document = (
        db.query(Document)
        .filter(Document.document_name == file.filename)
        .first()
    )

    if existing_document:
        return {
            "success": False,
            "message": "Document already exists."
        }

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parser = PDFParser()

    pages = parser.extract_text(file_path)
    print("=" * 50)
    print("Pages extracted:", len(pages))
    
    if pages:
        print("First page preview:")
        print(pages[0]["text"][:200])

    print("=" * 50)

    total_pages = len(pages)

    chunker = DocumentChunker()

    chunks = chunker.create_chunks(pages)

    total_chunks = len(chunks)

    full_text = "\n".join(
    page["text"] for page in pages)

    classifier = DocumentClassifier()

    category = classifier.predict_category(full_text)
    print("=" * 50)
    print("Predicted Category:", category)
    print("=" * 50)

    vector_store = ChromaVectorStore()
    
    vector_store.add_chunks(file.filename, chunks)

    new_document = Document(
        document_name=file.filename,
        category=category,
        total_pages=total_pages,
        total_chunks=total_chunks,
        status="Processed"
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {
        "success": True,
        "document_id": new_document.id,
        "filename": new_document.document_name,
        "category": new_document.category,
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "status": new_document.status
    }

@router.get("/")
def get_documents(db: Session = Depends(get_db)):

    documents = db.query(Document).all()

    return documents


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        return {
            "success": False,
            "message": "Document not found."
        }

    # Delete PDF file
    file_path = os.path.join(
        UPLOAD_FOLDER,
        document.document_name
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete database record
    db.delete(document)
    db.commit()

    return {
        "success": True,
        "message": "Document deleted successfully."
    }

@router.get("/search")
def semantic_search(query: str):

    vector_store = ChromaVectorStore()

    results = vector_store.search(query)

    return {
        "query": query,
        "results": results["documents"][0],
        "metadata": results["metadatas"][0],
        "distances": results["distances"][0]
    }

@router.get("/ask")
def ask_question(question: str):

    vector_store = ChromaVectorStore()

    # Search relevant chunks
    results = vector_store.search(question)

    context = "\n\n".join(results["documents"][0])

    # Add current user question to memory
    memory.add_message("user", question)

    # Build conversation history
    history = ""

    for message in memory.get_history():
        history += f"{message['role']}: {message['content']}\n"

    # Generate answer
    llm = LLMService()

    answer = llm.generate_answer(
        question=question,
        context=context + "\n\nConversation History:\n" + history
    )

    # Save assistant response
    memory.add_message("assistant", answer)

    # Remove duplicate sources
    unique_sources = []
    seen = set()

    for source in results["metadatas"][0]:
        key = (source["document"], source["page"])

        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    return {
        "question": question,
        "answer": answer,
        "sources": unique_sources,
        "conversation_history": memory.get_history()
    }

@router.delete("/memory")
def clear_memory():

    memory.clear()

    return {
        "success": True,
        "message": "Conversation memory cleared."
    }

from sqlalchemy import func

@router.get("/analytics")
def system_analytics(db: Session = Depends(get_db)):

    total_documents = db.query(Document).count()

    total_pages = db.query(
        func.sum(Document.total_pages)
    ).scalar() or 0

    total_chunks = db.query(
        func.sum(Document.total_chunks)
    ).scalar() or 0

    processed_documents = db.query(Document).filter(
        Document.status == "Processed"
    ).count()

    categories = db.query(
        Document.category,
        func.count(Document.id)
    ).group_by(
        Document.category
    ).all()

    category_stats = {
        category: count
        for category, count in categories
    }

    return {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "categories": category_stats
    }

@router.get("/compare")
def compare_documents(
    doc1: int,
    doc2: int,
    db: Session = Depends(get_db)
):

    document1 = db.query(Document).filter(
        Document.id == doc1
    ).first()

    document2 = db.query(Document).filter(
        Document.id == doc2
    ).first()

    if not document1 or not document2:
        return {
            "success": False,
            "message": "One or both documents not found."
        }

    vector_store = ChromaVectorStore()

    chunks1 = vector_store.get_document_chunks(
        document1.document_name
    )

    chunks2 = vector_store.get_document_chunks(
        document2.document_name
    )

    text1 = "\n".join(chunks1[:20])
    text2 = "\n".join(chunks2[:20])

    prompt = f"""
Compare these two documents.

Document 1:
{text1}

Document 2:
{text2}

Provide:
1. Summary of Document 1
2. Summary of Document 2
3. Similarities
4. Differences
5. Overall Conclusion
"""

    llm = LLMService()

    comparison = llm.generate_answer(
        question="Compare these documents.",
        context=prompt
    )

    return {
        "document_1": document1.document_name,
        "document_2": document2.document_name,
        "comparison": comparison
    }