FROM python:3.10-slim

LABEL maintainer="Nikhil"
LABEL description="Faculty Matcher - Web application for matching student resumes with faculty profiles"

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies and download SpaCy models
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download en_core_web_md && \
    python -m nltk.downloader punkt stopwords

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/resumes uploads

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports for APIs
EXPOSE 8000 5000

# Command to run the application
CMD ["python", "main.py", "start-all"]
