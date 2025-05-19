import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.models import Highlight
import numpy as np


def store_highlight(session: Session, video_id: uuid.UUID, timestamp: float, description: str, embedding: list[float],
                    summary: str = None):
    """Stores a highlight and its embedding in the database."""
    # Convert the list of floats to a bytes representation for pgvector
    embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()

    highlight = Highlight(
        video_id=video_id,
        timestamp=timestamp,
        description=description,
        embedding=embedding_bytes,
        summary=summary
    )
    session.add(highlight)
    session.commit()
    return highlight.id  # Return the ID of the created highlight


def find_similar_highlights(session: Session, query_embedding: list[float], video_id: uuid.UUID, top_k: int = 5):
    """
    Finds the most similar highlights to the query embedding for a specific video.

    Args:
        session: The database session.
        query_embedding: The embedding of the query.
        video_id: The ID of the video to search within.
        top_k: The number of similar highlights to retrieve.

    Returns:
        A list of Highlight objects, ordered by similarity.
    """
    # Convert the query embedding to a byte string
    query_embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()

    # Use the <-> operator for cosine distance (most common for embeddings)
    #  and filter by video_id
    query = text(
        """
        SELECT id, video_id, timestamp, description, summary,
               embedding <-> :query_embedding AS distance
        FROM highlights
        WHERE video_id = :video_id
        ORDER BY embedding <-> :query_embedding
        LIMIT :top_k
        """
    )
    result = session.execute(
        query,
        {
            "query_embedding": query_embedding_bytes,
            "video_id": video_id,
            "top_k": top_k,
        },
    )

    # Fetch the results and convert them to Highlight objects
    similar_highlights = []
    for row in result:
        highlight = Highlight(
            id=row[0],
            video_id=row[1],
            timestamp=row[2],
            description=row[3],
            embedding=row[4],  # This will be in bytes
            summary=row[5]
        )
        similar_highlights.append(highlight)
    return similar_highlights
