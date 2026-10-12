
from app.database.connection import SessionLocal
from app.database.models import User, Document
from app.services.semantic_search_service import search_documents

db = SessionLocal()

try:
    user = db.query(User).filter(User.id == 5).first()

    if user is None:
        raise RuntimeError("Register a user before testing.")

    print("Selected user ID:", user.id)

    # Check which documents belong to this user.
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user.id)
        .all()
    )

    print("Documents owned by user:", len(docs))

    for doc in docs:
        print(doc.id, doc.original_filename)

    # Perform semantic search.
    query = "What qualifications or certifications are in my PDF?"

    results = search_documents(
        db=db,
        user_id=user.id,
        query=query,
        top_k=3,
    )

    print("\nQuestion:", query)
    print("\nRelevant chunks:")

    for result in results:
        print("\nDocument ID:", result["document_id"])
        print("Similarity:", round(result["similarity"], 4))
        print("Content:", result["content"])

finally:
    db.close()
