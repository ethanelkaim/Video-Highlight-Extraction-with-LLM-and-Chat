# llm_module/llm_api.py
import google.generativeai as genai
from config import LLM_API_KEY, LLM_MODEL_NAME, LLM_EMBEDDING_MODEL
import logging

# Initialize the Gemini client.
genai.configure(api_key=LLM_API_KEY)

def generate_highlight_description(video_clip_description: str) -> str:
    """
    Generates a detailed description for a video highlight using an LLM.
    """
    try:
        # For text generation, using GenerativeModel is correct
        model = genai.GenerativeModel(model_name=LLM_MODEL_NAME) # e.g., "gemini-1.5-flash" or your chosen generation model
        response = model.generate_content(video_clip_description)
        # Ensure response.text exists and is not empty
        if response and response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        elif response and hasattr(response, 'text') and response.text: # Fallback for older response structures or simpler responses
            return response.text
        logging.warning(f"LLM response was empty or malformed for description: {video_clip_description}")
        return "The model's response was empty or malformed."
    except Exception as e:
        logging.error(f"Error generating highlight description: {e}")
        # It's better to return a string indicating error than None if subsequent code expects a string.
        return "Error generating LLM description."


def get_embedding(text: str, task_type: str = "SEMANTIC_SIMILARITY") -> list[float]: # Added task_type, RETRIEVAL_DOCUMENT or RETRIEVAL_QUERY often used
    """
    Generates an embedding for the given text using a Gemini embedding model.
    """
    try:
        # Use the model name from config or a default if it's not set
        embedding_model_to_use = LLM_EMBEDDING_MODEL if LLM_EMBEDDING_MODEL else "models/embedding-001"
        response = genai.embed_content(
            model=embedding_model_to_use,
            content=text,
            task_type=task_type
        )
        return response.get('embedding', [])  # More robust access
    except Exception as e:
        logging.error(f"Error generating embedding for text '{text[:50]}...': {e}")
        return []