# RAG Document Starter Project

A production-ready Retrieval-Augmented Generation (RAG) starter application for ingesting and querying markdown documents using vector similarity search.

This starter project provides a solid foundation for building production RAG applications with robust error handling, configurable processing, and efficient vector search capabilities.

## Overview

This project provides a complete pipeline for processing markdown documents, converting them into searchable vector embeddings, and enabling semantic queries. It uses ChromaDB for vector storage and Sentence Transformers for embeddings.

## Features

- **Document Ingestion**: Process markdown files with configurable chunking and overlap
- **Vector Storage**: Persistent storage using ChromaDB with local SQLite backend
- **Semantic Search**: Query documents using natural language with metadata filtering
- **Robust Error Handling**: Comprehensive error handling for file operations and database access
- **Configurable**: Command-line arguments for paths and verbose logging
- **Production Ready**: Proper logging, UTF-8 encoding, and input validation

## Architecture

### Core Components

- **`utils/parse_docs.py`**: Document ingestion pipeline with chunking, embedding, and batch processing
- **`utils/clear_collection.py`**: Utility for managing the document collection
- **`main.py`**: Query interface for retrieving relevant document chunks

### Technical Stack

- **ChromaDB**: Vector database for storing and retrieving embeddings
- **Sentence Transformers**: `all-mpnet-base-v2` model for high-quality embeddings
- **Python**: Standard data processing and file handling

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd rag-starter

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### 1. Ingest Documents

```bash
# Process all markdown files in current directory and subdirectories
python utils/parse_docs.py

# Process specific path
python utils/parse_docs.py --path "/path/to/documents/**/*.md"

# Enable verbose logging
python utils/parse_docs.py --path "/path/to/documents/**/*.md" --verbose
```

#### 2. Query Documents

```bash
# Run semantic queries (edit main.py to modify query text and filters)
python main.py
```

#### 3. Manage Collection

```bash
# Clear the document collection (with confirmation)
python utils/clear_collection.py
```

## Configuration

### Document Processing Parameters

- **Chunk Size**: 1000 characters (configurable via `CHUNK_SIZE` constant)
- **Overlap**: 100 characters between chunks (configurable via `CHUNK_OVERLAP`)
- **Batch Size**: 100 chunks per database operation (configurable via `BATCH_SIZE`)

### Command Line Arguments

- `--path`: Glob pattern for markdown files (default: `./**/*.md`)
- `--verbose`: Enable debug-level logging

## Data Storage

- **Vector Database**: Stored in `./my_data/` directory
- **Collection Name**: `markdown-documents`
- **Logging**: Detailed logs saved to `ingestion.log`

## Document Metadata

Each document chunk is stored with rich metadata:
- **source**: Original file path
- **category**: Parent directory name
- **filename**: Original filename
- **batch**: Processing batch index

## Query Features

- **Semantic Search**: Find documents based on meaning, not just keywords
- **Metadata Filtering**: Filter results by category, source, or other metadata
- **Configurable Results**: Specify number of results to return

## Error Handling

The system includes comprehensive error handling for:
- File access permissions and encoding issues
- Database connection failures
- Invalid path patterns
- Empty or malformed documents
- Collection not found errors

## Performance Features

- **Batch Processing**: Efficient database operations with configurable batch sizes
- **Sliding Window Chunks**: Overlapping chunks maintain context
- **Progress Tracking**: Real-time progress bars with tqdm
- **Efficient Embeddings**: Cached sentence transformer model

## Use Cases

- **Knowledge Base Search**: Query personal or organizational documentation
- **Research Assistant**: Find relevant information across academic papers
- **Documentation Search**: Search technical documentation or API docs
- **Content Discovery**: Discover related content across markdown files

## Development

### Project Structure
```
rag-starter/
├── utils/
│   ├── parse_docs.py      # Document ingestion pipeline
│   └── clear_collection.py # Collection management
├── main.py                # Query interface
├── requirements.txt       # Python dependencies
├── my_data/              # ChromaDB storage
└── ingestion.log         # Processing logs
```

### Extending the Project

- **Custom Embeddings**: Replace `SentenceTransformerEmbeddingFunction` with custom models
- **Additional File Types**: Extend `parse_docs.py` to support PDF, TXT, or other formats
- **Web Interface**: Add Flask/FastAPI frontend for querying
- **Advanced Filtering**: Implement more sophisticated metadata queries

## Improvement path

1. Unified CLI Interface

- [Click](https://click.palletsprojects.com/en/stable/) Framework for professional CLI with auto-help and validation
- Subcommands: rag ingest, rag query, rag clear, rag config
- Consistent argument parsing and error handling
- Rich output formatting with colors and tables
