# 1. Base Image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install System Dependencies (sometimes needed for building packages)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 4. Install Python Dependencies
RUN pip install streamlit requests pandas plotly ccxt

# 5. Copy Code
COPY src/ src/

# 6. Expose Streamlit Port
EXPOSE 8501

# 7. Start Command
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0"]
