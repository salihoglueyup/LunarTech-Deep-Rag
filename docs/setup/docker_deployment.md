# Docker Deployment Guide

For enterprise environments or cloud hosting (AWS, DigitalOcean, Heroku), we strongly recommend running LunarTech Deep RAG inside a Docker container to ensure isolated environment variables and dependency locking.

## 1. The Dockerfile

Create a `Dockerfile` in the root of the project with the following structure:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for certain PDF parsers or ML libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Healthcheck to verify Streamlit is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to run the application
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 2. `.dockerignore`

Ensure you prevent pushing large graph databases or local caches into your Docker image. Create a `.dockerignore` file:

```text
.venv/
__pycache__/
.env
data/
*.db
*.graphml
```

## 3. Building and Running

To build your image:

```bash
docker build -t lunartech-ai .
```

To run the container (ensuring you pass you API keys securely):

```bash
docker run -p 8501:8501 \
  -e OPENROUTER_API_KEY="your-key-here" \
  -e SUPABASE_URL="your-supabase-url" \
  -e SUPABASE_KEY="your-supabase-key" \
  -v $(pwd)/data:/app/data \
  lunartech-ai
```

*Note: The `-v $(pwd)/data:/app/data` flag ensures that your SQLite database, LightRAG knowledge graphs, and LLM caches persist on your host machine even if the Docker container is destroyed.*
