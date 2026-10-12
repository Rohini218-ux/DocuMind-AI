
from sqlalchemy.orm import Session

from app.database.models import Document, DocumentChunk
from app.services.semantic_search_service import search_documents
from app.services.llm_service import generate_answer


def answer_document_question(
    db: Session,
    user_id: int,
    question: str,
    top_k: int = 3,
) -> dict:
    cleaned_question = question.strip()
    normalized = cleaned_question.lower().strip(" .,!?" )

    if not cleaned_question:
        raise ValueError("Question cannot be empty")

    # 1. Handle greetings without searching documents.
    greetings = {
        "hi", "hello", "hey", "hii", "hiii",
        "good morning", "good afternoon", "good evening",
    }

    if normalized in greetings:
        return {
            "question": cleaned_question,
            "answer": (
                "Hello! 👋 I'm DocuMind AI. How can I help you today? "
                "I can answer questions about your PDFs, summarize "
                "documents, and extract important information."
            ),
            "sources": [],
        }

    # 2. Explain capabilities without searching documents.
    if normalized in {
        "help",
        "what can you do",
        "what can you do?",
        "who are you",
        "what is documind ai",
    }:
        return {
            "question": cleaned_question,
            "answer": (
                "I'm DocuMind AI, your document assistant! I can:\n\n"
                "- Answer questions about your uploaded PDFs.\n"
                "- Summarize a document and explain its main idea.\n"
                "- Extract important points, skills, and key facts.\n"
                "- Help you find specific information in your documents.\n\n"
                "Upload a PDF and tell me what you'd like to know."
            ),
            "sources": [],
        }

    # 3. Retrieve relevant document chunks for document questions.
    results = search_documents(
        db=db,
        user_id=user_id,
        query=cleaned_question,
        top_k=top_k,
    )

    if not results:
        return {
            "question": cleaned_question,
            "answer": (
                "I couldn't find relevant information in your uploaded "
                "documents. Try rephrasing your question or check that "
                "the correct PDF has been uploaded and indexed."
            ),
            "sources": [],
        }

    context = "\n\n".join(
        f"[Source {i + 1}]\n{result['content']}"
        for i, result in enumerate(results)
    )

    answer = generate_answer(
        question=cleaned_question,
        context=context,
    )

    sources = [
        {
            "document_id": result["document_id"],
            "document_name": result["document_name"],
            "chunk_id": result["chunk_id"],
            "similarity": result["similarity"],
        }
        for result in results
    ]

    return {
        "question": cleaned_question,
        "answer": answer,
        "sources": sources,
    }
