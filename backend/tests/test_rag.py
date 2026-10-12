
from unittest.mock import patch

from app.services import rag_service


def test_answer_document_question_handles_llm_response():
    with patch.object(
        rag_service,
        "generate_answer",
        return_value="The resume mentions Python, Java, and AI skills.",
    ):
        # We will add assertions here after confirming
        # the retrieval and database dependencies in rag_service.
        assert callable(rag_service.answer_document_question)
