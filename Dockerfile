# Use a Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
# Add ffmpeg here
RUN apt-get update && apt-get install -y libgl1-mesa-dev libglib2.0-0 ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/* # Clean up apt cache

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

# Install dependencies, including pgvector
RUN pip install --no-cache-dir -r requirements.txt
# psycopg2-binary is already in requirements.txt, so this explicit install might be redundant
# if it is, but having libpq-dev is good.
RUN apt-get update && \
    apt-get install -y postgresql-client libpq-dev && \
    pip install psycopg2-binary && \
    apt-get clean && rm -rf /var/lib/apt/lists/* # Clean up apt cache

# Copy the entire project
COPY . /app

# Set the entrypoint for the container.
WORKDIR /app/scripts
ENV PYTHONPATH=/app
CMD ["python", "process_video.py"]