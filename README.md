# Video Highlight Extraction and Chat

## Project Overview
This project is a Python-based tool that processes video files to extract descriptive highlights using an LLM, stores them in a PostgreSQL database with pgvector, and allows users to chat about these highlights via a web interface.

## Features
-   **Step 1: Video Processor**
    -   Accepts video files (.mp4, .mov).
    -   Extracts visual frames and audio.
    -   Transcribes audio to text using Whisper.
    -   Uses a Large Language Model (Gemini Flash) to:
        -   Identify important moments/scenes.
        -   Generate detailed descriptions for each moment.
    -   Stores highlights (timestamp, description, LLM summary, pgvector embedding) in PostgreSQL.
-   **Step 2: Interactive Chat**
    - Python FastAPI backend for chat.
    - Retrieves relevant highlights from the database based on user questions (using embeddings).
    - Responds only with content from the database.

## Prerequisites
-   Python 3.11+
-   Docker and Docker Compose
-   `git`
-   An LLM API Key for Google Gemini (refer to `.env.example`)
-   (If running outside Docker for Step 1) FFmpeg installed locally.
-   (If running outside Docker for Step 1) Whisper CLI installed locally.

## Project Structure
Briefly describe your main directories:
-   `/` (root): Docker setup, main configuration.
-   `/app` (inside Docker for Step 1): Contains the video processing application.
    -   `/database`: SQLAlchemy models, database setup, vector store logic.
    -   `/llm_module`: LLM API interaction.
    -   `/processors`: Video, audio, and text processing classes.
    -   `/scripts`: Main script for video processing (`process_video.py`).
-   `/backend_chat`: FastAPI application for the chat interface.
-   `/data/videos`: Place your sample video files here (e.g., `video.mp4`).
-   `/db_init`: SQL script for database initialization (e.g., creating extensions).
-   `/[your_frontend_directory]`: (Once you create it) Contains the frontend application.


## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-github-repository-url>
    cd <your-project-directory-name>
    ```

2.  **Set up Environment Variables:**
    Copy the example environment file and fill in your actual credentials:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file with your PostgreSQL settings and your `LLM_API_KEY`.

3.  **Place Sample Videos:**
    Ensure you have at least two sample videos (30 seconds to 1.5 minutes each, e.g., `.mp4`) in the `data/videos/` directory. The `process_video.py` script is currently hardcoded to look for `video.mp4`. Update the script or your filenames accordingly.

4.  **Build and Run with Docker Compose:**

    * **Step 1: Video Processing (Populating the Database)**
        This step processes the videos in `data/videos` and stores highlights in the database.
        ```bash
        # Ensure Docker Desktop is running
        docker-compose build # Build (or rebuild) the 'app' service image
        docker-compose up -d db # Start the database service in the background
        # Wait a few seconds for the database to initialize fully
        docker-compose run --rm app python scripts/process_video.py # Run the video processing
        ```
        Check the logs to ensure processing completes without errors.

    * **Step 2: Running the Chat Application Backend**
        This starts the FastAPI backend for the chat.

        **To run the backend locally (as you've been doing):**
        ```bash
        # Navigate to the backend_chat directory
        cd backend_chat
        # Activate your Python virtual environment
        # Example: ..\venv\Scripts\Activate.ps1 or ..\backend_chat\venv\Scripts\Activate.ps1
        # (Adjust path to your venv)
        python -m venv venv 
        .\venv\Scripts\Activate.ps1
        pip install -r requirements.txt # Assuming you'll add a requirements.txt for backend_chat
        uvicorn main:app --reload --port 8001 
        ```
        
## Usage

* After running Step 1, the database will be populated.
* Start the chat backend (and frontend).
* Open the frontend in your browser (e.g., `http://localhost:3000`).
* Ask questions about the processed videos, for example:
    * "What happened in the video?"
    * "How many people are in the video?"

## API Endpoint (Chat Backend)
-   **POST** `/chat/ask`
    -   **Request Body (JSON):**
        ```json
        {
            "question": "Your question about the video"
        }
        ```
    -   **Response Body (JSON):**
        ```json
        {
            "answer": "The answer based on video highlights."
        }
        ```

## Chat Architecture & Endpoint Flow
-   User types question in Frontend.
-   Frontend sends POST request to Backend's `/chat/ask` endpoint.
-   Backend (FastAPI):
    -   Receives the question.
    -   Generates an embedding for the question using Gemini.
    -   Fetches all highlight descriptions and their pre-computed embeddings from the PostgreSQL+pgvector database.
    -   Calculates cosine similarity between the question embedding and all highlight embeddings.
    -   Selects the top N most relevant highlights.
    -   Structures a response string using only the content of these retrieved highlights.
    -   Returns the response to the Frontend.
-   Frontend displays the answer.

## Notes
- The LLM (Gemini Flash for descriptions, Embedding model for embeddings) is used in Step 1 (video processing) and for embedding the user's question in Step 2. The final answer generation in Step 2 strictly uses data retrieved from the database.
- The project uses `pgvector` for efficient similarity searches in PostgreSQL.