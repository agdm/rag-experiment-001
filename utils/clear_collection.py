import chromadb

try:
    client = chromadb.PersistentClient(path="./my_data")
    print("Connected to ChromaDB")
    
    # Check if collection exists before deleting
    try:
        existing_collection = client.get_collection("markdown-documents")
        count = existing_collection.count()
        print(f"Collection 'markdown-documents' exists with {count} documents")
        
        # Confirm deletion
        response = input("Are you sure you want to delete this collection? (y/N): ")
        if response.lower() in ['y', 'yes']:
            client.delete_collection("markdown-documents")
            print("Collection 'markdown-documents' deleted successfully")
        else:
            print("Deletion cancelled")
            
    except Exception as e:
        print(f"Collection 'markdown-documents' does not exist: {e}")
        
except Exception as e:
    print(f"Error accessing ChromaDB: {e}")