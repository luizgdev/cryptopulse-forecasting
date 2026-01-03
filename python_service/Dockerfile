# Base Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for compiling some python packages)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 1. Install Poetry
RUN pip install poetry

# 2. Copy dependency files FIRST (for Docker caching)
COPY pyproject.toml poetry.lock* ./

# 3. Install dependencies
# We disable virtualenvs creation to install directly into the system python inside the container
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# 4. Copy Source Code
COPY src/ src/

# Expose Streamlit Port
EXPOSE 8501

# Start Command
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0"]
