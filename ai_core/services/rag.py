"""Lightweight RAG service using Gemini Embedding API.

Provides semantic search over document chunks stored in the database.
Uses cosine similarity with NumPy for fast, CPU-only retrieval — no
external vector database required.
"""

import logging
from typing import Optional

import numpy as np
from decouple import config
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from ai_core.models import DocumentChunk
from ai_core.services.document_parser import chunk_text, extract_text
from course.models import Upload

logger = logging.getLogger("ai_core")

# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

_embeddings_model: Optional[GoogleGenerativeAIEmbeddings] = None


def _get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    """Return a cached instance of the Gemini embeddings model."""
    global _embeddings_model
    if _embeddings_model is None:
        _embeddings_model = GoogleGenerativeAIEmbeddings(
            google_api_key=config("GOOGLE_API_KEY"),
            model="models/gemini-embedding-001",
        )
        logger.info("Initialized Gemini gemini-embedding-001")
    return _embeddings_model


def embed_text(text: str) -> list[float]:
    """Generate an embedding vector for a single text string.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    model = _get_embeddings_model()
    return model.embed_query(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for multiple texts in a single batch.

    Args:
        texts: List of text strings to embed.

    Returns:
        A list of embedding vectors, one per input text.
    """
    model = _get_embeddings_model()
    return model.embed_documents(texts)


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------


def embed_and_store_chunks(upload_id: int) -> int:
    """Parse a document, chunk it, embed the chunks, and store in the database.

    This function is idempotent — if chunks already exist for the given
    upload, it skips processing entirely (lazy indexing).

    Args:
        upload_id: Primary key of the Upload record to process.

    Returns:
        The number of chunks created (0 if already indexed).
    """
    if DocumentChunk.objects.filter(upload_id=upload_id).exists():
        logger.info("Upload %d already indexed, skipping", upload_id)
        return 0

    upload = Upload.objects.get(pk=upload_id)
    file_path = upload.file.path

    # Extract and chunk text
    raw_text = extract_text(file_path)
    if not raw_text:
        logger.warning("No text extracted from upload %d (%s)", upload_id, file_path)
        return 0

    chunks = chunk_text(raw_text)
    if not chunks:
        logger.warning("No chunks generated from upload %d", upload_id)
        return 0

    # Batch embed all chunks in one API call
    logger.info("Embedding %d chunks for upload %d", len(chunks), upload_id)
    vectors = embed_texts(chunks)

    # Bulk create chunk records
    chunk_objects = [
        DocumentChunk(
            upload_id=upload_id,
            chunk_index=i,
            content=content,
            embedding=vector,
        )
        for i, (content, vector) in enumerate(zip(chunks, vectors))
    ]
    DocumentChunk.objects.bulk_create(chunk_objects)
    logger.info("Stored %d chunks for upload %d", len(chunk_objects), upload_id)

    return len(chunk_objects)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot = np.dot(vec_a, vec_b)
    norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if norm == 0:
        return 0.0
    return float(dot / norm)


def search_chunks(
    query: str,
    upload_ids: list[int],
    top_k: int = 3,
) -> str:
    """Find the most relevant document chunks for a given query.

    Searches only within the specified uploads (documents selected by the
    user). Returns the top-K chunks concatenated as a single context string.

    Args:
        query: The search query (typically the lesson topic).
        upload_ids: List of Upload IDs to restrict the search to.
        top_k: Number of top-matching chunks to return.

    Returns:
        A concatenated string of the most relevant chunks, or empty
        string if no relevant chunks are found.
    """
    # Retrieve chunks belonging to the selected documents
    chunks = DocumentChunk.objects.filter(
        upload_id__in=upload_ids,
        embedding__isnull=False,
    ).values_list("content", "embedding")

    if not chunks:
        logger.info("No indexed chunks found for uploads %s", upload_ids)
        return ""

    # Embed the query
    query_vector = np.array(embed_text(query))

    # Score each chunk by cosine similarity
    scored: list[tuple[float, str]] = []
    for content, embedding in chunks:
        chunk_vector = np.array(embedding)
        score = _cosine_similarity(query_vector, chunk_vector)
        scored.append((score, content))

    # Sort by similarity (descending) and take top-K
    scored.sort(key=lambda x: x[0], reverse=True)
    top_chunks = [content for _, content in scored[:top_k]]

    logger.info(
        "RAG search for '%s' across %d uploads: found %d chunks, returning top %d",
        query[:50],
        len(upload_ids),
        len(scored),
        len(top_chunks),
    )

    return "\n\n---\n\n".join(top_chunks)
