import numpy as np

try:
    from config import DATABASE_URL
except ImportError:
    from .config import DATABASE_URL

import asyncpg
import logging

logger = logging.getLogger(__name__)


async def fetch_all_highlights_async():
    """Asynchronously fetches all video highlights from the database."""
    conn = None
    try:
        logger.info("Attempting to connect to the database...")
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Successfully connected to the database.")
        logger.info("Attempting to fetch all highlights...")
        # Make sure your table is named 'highlights' and column is 'embedding'
        rows = await conn.fetch("SELECT id, timestamp, description, embedding FROM highlights")

        highlights = []
        for row in rows:
            embedding_bytes = row['embedding']
            embedding_list = []  # Default to empty list if conversion fails
            if embedding_bytes:
                try:
                    # Convert bytes back to NumPy array of float32, then to list
                    embedding_list = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()
                except Exception as e:
                    logger.error(f"Error converting embedding bytes for highlight ID {row['id']}: {e}")

            highlights.append({
                "id": row['id'],
                "timestamp": row['timestamp'],
                "description": row['description'],
                "embedding": embedding_list  # <<<<<<<<<< USE THE CONVERTED LIST
            })

        logger.info(f"Fetched {len(highlights)} highlights (after potential embedding conversion).")
        return highlights
    except Exception as e:
        logger.error(f"Error fetching highlights: {e}")
        return []  # Return empty list on error
    finally:
        if conn:
            logger.info("Closing database connection.")
            await conn.close()


# If using psycopg2-binary (synchronous):
"""
def fetch_all_highlights_sync():
    \"""Synchronously fetches all video highlights from the database.\"\"\"
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp, description, embedding FROM highlights")
    rows = cur.fetchall()
    highlights = [
        {"id": row[0], "timestamp": row[1], "description": row[2], "embedding": row[3]}
        for row in rows
    ]
    cur.close()
    return highlights
except Exception as e:
    print(f"Error fetching highlights: {e}")
    return []
finally:
    if conn:
        conn.close()
"""

if __name__ == "__main__":
    import asyncio
    import numpy as np

    highlights = asyncio.run(fetch_all_highlights_async())
    print(f"Fetched {len(highlights)} highlights.")
    # You can print the first highlight to see the structure
    if highlights:
        print(highlights[0])
