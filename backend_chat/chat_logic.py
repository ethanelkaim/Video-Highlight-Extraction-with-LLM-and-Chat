import numpy as np
from llm_module.llm_api import get_embedding  # To generate embeddings for the question
from typing import List, Dict
import logging

def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculates the cosine similarity between two embeddings."""
    if not embedding1 or not embedding2:
        return 0.0
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    dot_product = np.dot(embedding1, embedding2)
    norm_embedding1 = np.linalg.norm(embedding1)
    norm_embedding2 = np.linalg.norm(embedding2)
    if norm_embedding1 == 0 or norm_embedding2 == 0:
        return 0.0
    return dot_product / (norm_embedding1 * norm_embedding2)


async def find_relevant_highlights(question: str, highlights: List[Dict], top_n: int = 3) -> List[Dict]:
    """
    Finds the most relevant highlights from the database based on the question.

    Args:
        question: The user's question.
        highlights: A list of dictionaries, where each dictionary represents a highlight
                    and contains 'description' and 'embedding'.
        top_n: The number of top relevant highlights to retrieve.

    Returns:
        A list of the top N most relevant highlights, sorted by similarity.
    """
    # For querying/searching, use "RETRIEVAL_QUERY"
    question_embedding = get_embedding(question,
                                       task_type="RETRIEVAL_QUERY")  # Note: get_embedding is synchronous, consider making it async or running in thread pool
    if not question_embedding:
        logging.warning(f"Could not generate embedding for question: {question}")
        return []

    similarity_scores = []
    for highlight in highlights:
        similarity = calculate_similarity(question_embedding, highlight.get('embedding', []))
        similarity_scores.append((highlight, similarity))

    # Sort by similarity score in descending order
    sorted_highlights = sorted(similarity_scores, key=lambda item: item[1], reverse=True)
    return [highlight for highlight, score in sorted_highlights[:top_n]]


def structure_response(relevant_highlights: List[Dict]) -> str:
    """
    Structures a coherent response based on the retrieved relevant highlights.

    Args:
        relevant_highlights: A list of relevant highlights.

    Returns:
        A string containing the structured response.
    """
    if not relevant_highlights:
        return "No relevant information found in the video highlights."

    response = "Based on the video highlights:\n"
    for i, highlight in enumerate(relevant_highlights):
        response += f"{i + 1}. At timestamp {highlight['timestamp']}: {highlight['description']}\n"

    return response


if __name__ == "__main__":
    import asyncio


    # Example usage (requires you to have fetched highlights first)
    async def main():
        # Placeholder for fetched highlights (replace with actual data)
        fetched_highlights = [
            {"timestamp": 5, "description": "A person gets out of a blue car.", "embedding": [0.1, 0.2, 0.3]},
            {"timestamp": 12, "description": "The person walks towards a building.", "embedding": [0.4, 0.5, 0.6]},
            {"timestamp": 20, "description": "The building has a large glass door.", "embedding": [0.7, 0.8, 0.9]},
            {"timestamp": 25, "description": "Another person exits the same blue car.",
             "embedding": [0.15, 0.25, 0.35]},
        ]
        question = "What happened after someone exited the vehicle?"
        relevant_highlights = await find_relevant_highlights(question, fetched_highlights)
        print("Relevant Highlights:")
        for highlight in relevant_highlights:
            print(f"Timestamp: {highlight['timestamp']}, Description: {highlight['description']}")
        response = structure_response(relevant_highlights)
        print("\nStructured Response:")
        print(response)


    asyncio.run(main())
