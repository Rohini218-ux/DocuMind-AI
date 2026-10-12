from types import SimpleNamespace

from app.services import llm_service


def test_generate_answer(monkeypatch):
    def fake_generate_content(**kwargs):
        return SimpleNamespace(
            text="The programming languages mentioned are Python and Java."
        )

    monkeypatch.setattr(
        llm_service.client.models,
        "generate_content",
        fake_generate_content,
    )

    answer = llm_service.generate_answer(
        question="Which programming languages are mentioned?",
        context="The candidate has experience with Python and Java.",
    )

    assert isinstance(answer, str)
    assert "Python" in answer
    assert "Java" in answer