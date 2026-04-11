import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class RAGPipeline:
    def __init__(self, upload_dir='uploads'):
        self.upload_dir = upload_dir
        self.texts = []
        self.filenames = []
        self.embeddings = None
        print("Loading SentenceTransformer model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.reload_documents()

    def reload_documents(self):

        print("Indexing documents in uploads/ directory...")
        new_texts = []
        new_filenames = []
        
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
            
        for filename in os.listdir(self.upload_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.upload_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
                        
                        if len(chunks) == 1 and len(chunks[0]) > 500:
                            chunks = [c.strip() for c in re.split(r'(?<=[.!?]) +', chunks[0])]
                            
                        for chunk in chunks:
                            new_texts.append(chunk)
                            new_filenames.append(filename)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        if new_texts:
            self.texts = new_texts
            self.filenames = new_filenames
            print(f"Generating embeddings for {len(self.texts)} chunks...")
            self.embeddings = self.embedder.encode(self.texts, convert_to_tensor=False)
            print(f"Successfully indexed {len(self.texts)} chunks from {len(set(self.filenames))} files.")
        else:
            self.texts = []
            self.filenames = []
            self.embeddings = None
            print("No documents found to index.")

    def query(self, question, top_k=5):
        if self.embeddings is None or len(self.embeddings) == 0:
            return []
            
        question_embedding = self.embedder.encode([question])
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for i in top_indices:
            results.append({
                "text": self.texts[i],
                "filename": self.filenames[i],
                "score": float(similarities[i])
            })
            
        return results

if __name__ == "__main__":
    test_pipeline = RAGPipeline()
    query = "Information about Frodo"
    print(f"\nTesting Query: {query}")
    results = test_pipeline.query(query)
    for res in results:
        print(f"[{res['filename']} (Score: {res['score']:.4f})]: {res['text'][:100]}...")
