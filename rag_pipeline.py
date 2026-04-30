import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    def __init__(self, upload_dir='uploads'):
        self.upload_dir = upload_dir
        self.texts = []
        self.filenames = []
        self.embeddings = None
        
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "x-ai/grok-beta")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
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
                        
                        processed_chunks = []
                        for chunk in chunks:
                            if len(chunk) > 800:
                                sub_chunks = [s.strip() for s in re.split(r'(?<=[.!?]) +', chunk) if s.strip()]
                                processed_chunks.extend(sub_chunks)
                            else:
                                processed_chunks.append(chunk)
                            
                        for chunk in processed_chunks:
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

    def generate_answer(self, question, contexts):
        if not self.api_key:
            return "Error: OPENROUTER_API_KEY not found in environment."
            
        if not contexts:
            return "I couldn't find any relevant information in the uploaded documents to answer that."

        context_text = "\n\n".join([f"Source: {c['filename']}\nContent: {c['text']}" for c in contexts])
        
        prompt = f"""You are a helpful assistant. Use the provided context from uploaded documents to answer the user's question. 
If the answer is not in the context, say you don't know based on the provided documents.

Context: 
{context_text}

Question: {question}

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that answers questions based on retrieved document context."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to Grok AI: {str(e)}"

if __name__ == "__main__":
    test_pipeline = RAGPipeline()
    test_query = "Who is Frodo?"
    print(f"\nTesting Retrieval: {test_query}")
    results = test_pipeline.query(test_query)
    for res in results:
        print(f"[{res['filename']} (Score: {res['score']:.4f})]: {res['text'][:100]}...")
    
    print("\nTesting Reasoning (Grok AI):")
    answer = test_pipeline.generate_answer(test_query, results)
    print(f"Answer: {answer}")
