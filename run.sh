#!/bin/bash
# Faculty Matcher - Helper script to run common commands

# Make the script executable
chmod +x run.sh

# Function to display help message
show_help() {
    echo "Faculty Matcher - Command Helper"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install         - Install dependencies"
    echo "  docker-install  - Start the application using Docker"
    echo "  setup-db        - Initialize the database"
    echo "  scrape          - Run the faculty scraper"
    echo "  parse <file>    - Parse a resume PDF"
    echo "  match <file>    - Match a parsed resume JSON with faculty"
    echo "  start           - Start all services"
    echo "  help            - Show this help message"
    echo ""
}

# Function to install dependencies
install_deps() {
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo "Downloading NLP models..."
    python -m spacy download en_core_web_sm
    python -m spacy download en_core_web_md
    python -m nltk.downloader punkt stopwords
    
    echo "Installation complete!"
}

# Function to install using Docker
docker_install() {
    echo "Starting application using Docker..."
    docker-compose up -d
    echo "Application started! API is available at:"
    echo "  - Faculty API: http://localhost:8000"
    echo "  - Resume Parser API: http://localhost:5000"
}

# Main command handler
case "$1" in
    install)
        install_deps
        ;;
    docker-install)
        docker_install
        ;;
    setup-db)
        python main.py setup-db
        ;;
    scrape)
        python main.py scrape
        ;;
    parse)
        if [ -z "$2" ]; then
            echo "Error: Please provide a PDF file path"
            echo "Usage: ./run.sh parse path/to/resume.pdf"
            exit 1
        fi
        python main.py parse-resume "$2"
        ;;
    match)
        if [ -z "$2" ]; then
            echo "Error: Please provide a resume JSON file path"
            echo "Usage: ./run.sh match path/to/parsed_resume.json"
            exit 1
        fi
        python main.py match "$2"
        ;;
    start)
        python main.py start-all
        ;;
    help|*)
        show_help
        ;;
esac
