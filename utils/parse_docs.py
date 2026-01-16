import chromadb
import argparse
import hashlib
import os
import logging
import sys
from glob import glob
from chromadb.utils import embedding_functions
from itertools import islice
from tqdm import tqdm

# TODO leverage this lib for token counts
# https://github.com/openai/tiktoken?tab=readme-ov-file
# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
# import tiktoken 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ingestion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
BATCH_SIZE = 100
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

try:
    default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-mpnet-base-v2"
    )
except Exception as e:
    logger.error(f"Failed to initialize embedding function: {e}")
    sys.exit(1)

def batch_generator(generator, batch_size=BATCH_SIZE):
    """
    Takes a generator and yields lists of 'batch_size' elements.
    """
    while True:
        batch = list(islice(generator, batch_size))
        if not batch:
            break
        yield batch


def chunk_content(content, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Yield successive n-sized chunks with a specified overlap."""
    if size <= overlap:
        raise ValueError("Chunk size must be greater than overlap.")

    start = 0
    while start < len(content):
        # The end is just start + size
        end = start + size
        yield content[start:end]

        # Move the start pointer forward by (size - overlap)
        # This creates the "sliding" effect
        start += (size - overlap)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='RAG document ingestion script')
    parser.add_argument('--path', type=str, default='./**/*.md',
                        help='Glob pattern for markdown files to process (default: ./**/*.md)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    return parser.parse_args()

def validate_path(path_pattern):
    """Validate that the path pattern exists and contains files."""
    try:
        files = glob(path_pattern, recursive=True)
        if not files:
            logger.error(f"No files found matching pattern: {path_pattern}")
            return False
        logger.info(f"Found {len(files)} files to process")
        return True
    except Exception as e:
        logger.error(f"Invalid path pattern '{path_pattern}': {e}")
        return False

if __name__ == '__main__':
    args = parse_arguments()
    
    # Adjust logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate path
    if not validate_path(args.path):
        sys.exit(1)
    
    try:
        # this creates a local hidden folder called .chroma to persist your data
        client = chromadb.PersistentClient(path="./my_data")
        # print(client.heartbeat()) # returns a timestamp

        # create a collection
        collection = client.get_or_create_collection(
            name="markdown-documents",
            embedding_function=default_ef,
        )

        logger.info(f"Successfully connected to collection: markdown-documents")

        path = glob(args.path, recursive=True)

    except Exception as e:
        logger.error(f"Failed to initialize database connection: {e}")
        sys.exit(1)

    for f in tqdm(path, desc="Processing files"):

        filename = os.path.basename(f)
        foldername = os.path.basename(os.path.dirname(f))
        parts = f.lstrip(os.sep).split(os.sep)
        
        if any(p.startswith(".") for p in parts if p):
            continue
        
        file_hash = hashlib.sha256(f.encode()).hexdigest()[:16]

        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()
                
                # Validate content
                if not content.strip():
                    logger.warning(f"Empty file skipped: {f}")
                    continue

                # chunk content 
                chunks_gen = chunk_content(content)
                logger.info(f"Starting ingestion of chunked content for '{f}'")

                for batch_index, chunk_batch in enumerate(batch_generator(chunks_gen, batch_size=BATCH_SIZE)):
                    if args.verbose:
                        logger.info(f"Processing batch {batch_index} of '{f}'")
                    batch_ids = []
                    batch_metadatas = []

                    for i, chunk_text in enumerate(chunk_batch):
                        # Skip empty chunks
                        if not chunk_text.strip():
                            continue
                            
                        global_index = (batch_index * BATCH_SIZE) + i

                        chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                        if args.verbose:
                            logger.debug(f"Chunk hash: {chunk_hash[:8]}")
                        batch_ids.append(f"{file_hash}_{global_index}_{chunk_hash[:8]}")
                        batch_metadatas.append({"source": f, "category": foldername, "filename": f, "batch": batch_index})

                    logger.info(f"Upserting batch {batch_index} of '{f}'")
                    collection.upsert(
                        ids=batch_ids,
                        documents=chunk_batch,
                        metadatas=batch_metadatas
                    )
                    logger.info(f"Successfully upserted batch {batch_index} of '{f}' ({len(batch_ids)} chunks)")

        except FileNotFoundError:
            logger.error(f"File not found: {f}")
        except PermissionError:
            logger.error(f"Permission denied: {f}")
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error in '{filename}': {e}")
        except Exception as e:
            logger.error(f"FAILED to process '{filename}': {str(e)}")