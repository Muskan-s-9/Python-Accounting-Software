import os
import pdfplumber
import fitz
import faiss
import json
import shelve
import requests
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import pandas as pd

# CONFIG
PDF_DIR = r"C:\Users\user\Downloads\Convert_pdf_file_into_the_excel_file\Rule_Setup\Accounting_Library_v3\All_Invoices\AuraFox"
CACHE_PATH = "cache/invoice_cache"
FAISS_INDEX_PATH = "faiss_index/index.bin"
MODEL_NAME = "all-MiniLM-L6-v2"
GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-70b-8192"

# Ensure directories exist
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)

# Load embedder
embedder = SentenceTransformer(MODEL_NAME)

# LLM query function with caching
class CacheManager:
    def __init__(self, path):
        self.cache = shelve.open(path)

    def get(self, key):
        return self.cache.get(key, None)

    def set(self, key, value):
        self.cache[key] = value

    def close(self):
        self.cache.close()

def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        pdf_document = fitz.open(pdf_path)
        count = pdf_document.page_count
        for i in range(count):
            page = pdf_document[i]
            tx= page.get_text()
            text+=tx
        return text
#         with pdfplumber.open(pdf_path) as pdf:
#             print("✅ PDF opened:", pdf)
#             text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text(use_text_flow=True)])
#             print("📄 Extracted text:\n", text[:500])  # print only first 500 characters
#             return text
    except Exception as e:
        print("❌ Error extracting text:", e)
        return ""


def build_faiss_index(text_chunks):
    print("cccccccc",text_chunks)
    embeddings = embedder.encode(text_chunks, show_progress_bar=True)
    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    return index

def load_faiss_index():
    return faiss.read_index(FAISS_INDEX_PATH)

def get_top_chunks(query, all_chunks, index, k=5):
    query_vec = embedder.encode([query])
    distances, indices = index.search(query_vec, k)
    return [all_chunks[i] for i in indices[0]]

def query_groq_llm(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

def query_llm_with_rag_and_cache(pdf_text, cache):
    if cache.get(pdf_text):
        return cache.get(pdf_text)

    chunks = [pdf_text[i:i+512] for i in range(0, len(pdf_text), 512)]
#     print(chunks)
    if not os.path.exists(FAISS_INDEX_PATH):
        print("building faiss index")
        index = build_faiss_index(chunks)
    else:
        index = load_faiss_index()

    query = "Extract invoice number, date, seller name,Buyer Name, final amount,Tax Rate,Tax Amount, and Tax Type from this invoice."
    top_chunks = get_top_chunks(query, chunks, index)

    context = "\n".join(top_chunks)
    prompt = f"""
You are an advanced invoice parser and data analyzer. Analyze and extract the text below and provide the following fields in JSON format:

- Invoice Number: The unique identifier of the invoice.
- Invoice Date: The date when the invoice was issued.
- Seller Name: The name of the seller.
- Buyer Name: The name of the buyer.
- Final Amount: The total amount on the invoice.
- Tax Rate: The rate applied to calculate the tax (e.g., 18%).
- Tax Amount: The actual amount of tax.
- Tax Type: The type of tax applied (e.g., CGST, SGST, IGST).


Text:
{context}
"""
    result = query_groq_llm(prompt)
    cache.set(pdf_text, result)
    return result

# === MAIN ===
# === MAIN ===
if __name__ == "__main__":
    results = []
    cache = CacheManager(CACHE_PATH)

    pdf_files = [os.path.join(PDF_DIR, f) for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):  # Limit to 1 for test
        try:
            print(pdf_path)
            text = extract_text_from_pdf(pdf_path)
            structured_data = query_llm_with_rag_and_cache(text, cache)
            print(f"\n🧾 {os.path.basename(pdf_path)}\n{structured_data}\n")
            print("data",structured_data)
            results.append(structured_data)
        except Exception as e:
            print(f"❌ Error with {pdf_path}: {e}")

    cache.close()

