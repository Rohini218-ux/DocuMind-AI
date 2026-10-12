
import json
from pathlib import Path

import faiss
import numpy as np

from app.services.embedding_service import generate_embeddings


class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunk_ids: list[int] = []
        self.document_ids: list[int] = []

    def add_chunks(
        self,
        chunks: list[str],
        chunk_ids: list[int],
        document_ids: list[int],
    ) -> None:
        if not chunks:
            return

        if not (
            len(chunks) == len(chunk_ids) == len(document_ids)
        ):
            raise ValueError("Chunks and IDs must have equal lengths")

        embeddings = generate_embeddings(chunks)
        vectors = np.asarray(embeddings, dtype="float32")

        if vectors.shape[1] != self.dimension:
            raise ValueError("Embedding dimension mismatch")

        self.index.add(vectors)
        self.chunk_ids.extend(chunk_ids)
        self.document_ids.extend(document_ids)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray(
            generate_embeddings([query]), dtype="float32"
        )

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vector, k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue

            position = int(idx)
            results.append({
                "chunk_id": self.chunk_ids[position],
                "document_id": self.document_ids[position],
                "similarity": float(score),
            })

        return results

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(directory / "documind.index"),
        )

        metadata = {
            "dimension": self.dimension,
            "chunk_ids": self.chunk_ids,
            "document_ids": self.document_ids,
        }

        with (directory / "metadata.json").open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(metadata, file)

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        index_path = directory / "documind.index"
        metadata_path = directory / "metadata.json"

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError("Saved FAISS index or metadata missing")

        with metadata_path.open(encoding="utf-8") as file:
            metadata = json.load(file)

        store = cls(dimension=metadata["dimension"])
        store.index = faiss.read_index(str(index_path))
        store.chunk_ids = metadata["chunk_ids"]
        store.document_ids = metadata["document_ids"]

        if store.index.ntotal != len(store.chunk_ids):
            raise ValueError("FAISS index and metadata are inconsistent")

        if len(store.chunk_ids) != len(store.document_ids):
            raise ValueError("Chunk and document mappings are inconsistent")

        return store
