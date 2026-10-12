
from uuid import uuid4

from app.database.connection import SessionLocal
from app.database.models import User, Document, DocumentChunk
from app.services.chunk_storage_service import save_document_chunks


def test_save_document_chunks():
    db = SessionLocal()
    user = None
    document = None

    try:
        # Create a separate test user.
        unique_id = uuid4().hex

        user = User(
            name="Chunk Storage Test",
            email=f"chunk-test-{unique_id}@example.com",
            password_hash="test-only-hash",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create a document owned by the test user.
        document = Document(
            owner_id=user.id,
            original_filename="test_chunk_storage.pdf",
            stored_filename=f"{unique_id}.pdf",
            file_size=100,
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        test_chunks = [
            "This is a test database chunk.",
            "This is a second test chunk.",
        ]

        saved_count = save_document_chunks(
            db=db,
            document_id=document.id,
            chunks=test_chunks,
        )

        saved_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        assert saved_count == 2
        assert len(saved_chunks) == 2
        assert saved_chunks[0].chunk_index == 0
        assert saved_chunks[0].content == test_chunks[0]
        assert saved_chunks[1].chunk_index == 1
        assert saved_chunks[1].content == test_chunks[1]

    finally:
        if document is not None:
            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).delete(synchronize_session=False)

            db.query(Document).filter(
                Document.id == document.id
            ).delete(synchronize_session=False)

        if user is not None:
            db.query(User).filter(
                User.id == user.id
            ).delete(synchronize_session=False)

        db.commit()
        db.close()
