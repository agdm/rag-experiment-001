import chromadb

try:
    client = chromadb.PersistentClient(path="./my_data")
    collection = client.get_collection("markdown-documents")
except Exception as e:
    print(f"Error accessing collection: {e}")
    exit(1)

query_text = "What do i say about certifications?"

try:
    results = collection.query(
        query_texts=[query_text],
        n_results=3,
        where={"category": "The Field of Medicine"}
    )
except Exception as e:
    print(f"Error executing query: {e}")
    exit(1)

if not results or not results.get('ids') or not results['ids'][0]:
    print("No results found")
    exit(0)

print(f"\n--- Results for: '{query_text}' ---")

for i in range(len(results['ids'][0])):
    print(f"\n[Match {i+1}]")
    print(f"ID: {results['ids'][0][i]}")
    print(f"Source: {results['metadatas'][0][i]['source']}")
    print(f"Content snippet: {results['documents'][0][i][:200]}...")
    print("-" * 30)

print("\n--- QUERY RESULTS ---")
for i, doc in enumerate(results['documents'][0]):
    print(f"\nMatch {i+1} (Source: {results['metadatas'][0][i]['source']}):")
    print(doc[:200] + "...") # Print first 200 chars