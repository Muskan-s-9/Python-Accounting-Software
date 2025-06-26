import os
import fitz
import faiss
import shelve
import requests
from tqdm import tqdm
import json
from sentence_transformers import SentenceTransformer

    
def process_invoices_with_rag_and_cache(folder_name = "Amazon"):
    
    base_path = r'Invoices_template'
    pdf_dir = os.path.join(base_path, folder_name)
    cache_path = "invoice_processor/cache/invoice_cache"
    faiss_index_path = "invoice_processor/faiss_index/index.bin"
#     model_name =  "all-MiniLM-L6-v2"
    model_name = "all-mpnet-base-v2"
    groq_api_key = ""
#     groq_model  = "llama3-70b-8192"
#     groq_model  = "mixtral-8x7b-32768"
    groq_model = "llama3-8b-8192"
# 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

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)

    embedder = SentenceTransformer(model_name)

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
                text += page.get_text()
            return text
        except Exception as e:
            print("❌ Error extracting text:", e)
            return ""

    def build_faiss_index(text_chunks):
        embeddings = embedder.encode(text_chunks, show_progress_bar=True)
        dim = embeddings[0].shape[0]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        faiss.write_index(index, faiss_index_path)
        return index

    def load_faiss_index():
        return faiss.read_index(faiss_index_path)

    def get_top_chunks(query, all_chunks, index, k=5):
        query_vec = embedder.encode([query])
        distances, indices = index.search(query_vec, k)
        return [all_chunks[i] for i in indices[0]]

    def query_groq_llm(prompt):
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": groq_model,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]

    def query_llm_with_rag_and_cache(pdf_text, cache):
        if cache.get(pdf_text):
            print("returning from the Cache")
            return cache.get(pdf_text)

        chunks = [pdf_text[i:i+512] for i in range(0, len(pdf_text), 512)]
        if not os.path.exists(faiss_index_path):
            index = build_faiss_index(chunks)
        else:
            index = load_faiss_index()

        query = (
    "You are an expert invoice parser. Extract the following structured fields from the given invoice text. "
    "Use only the explicit information present in the text. Do not infer or fabricate data. "
    "Return the result strictly as a **valid JSON object** with only the specified keys and accurate values.\n\n"

    "Required fields:\n"
    "- Invoice Number: Unique identifier of the invoice.\n"
    "- Invoice Date: Date the invoice was issued.\n"
    "- Seller Name: Full name of the seller entity.\n"
    "- Buyer Name: Full name of the buyer entity.\n"
    "- Order Number: Purchase Order number (if present).\n"
    "- GST Number: Seller or buyer GST identification number.\n"
    "- Description: Summary or description of goods/services billed.\n"
    "- Final Amount: Total amount payable after taxes.\n"
    "- IGST Tax Rate: Total IGST rate applied \n"
    "- CGST Tax Rate: Total CGST rate applied.\n"
    "- SGST Tax Rate: Total SGST rate applied.\n"
    "- Tax Amount: Combined value of all taxes applied.\n"
    "- Tax Type: List of applicable tax types (e.g., [\"CGST\", \"SGST\"]).\n"
    "- Total CGST: Sum of  Tax CGST  amount charged .\n"
    "- Total SGST: Sum of  Tax SGST  amount charged.\n"
    "- Total IGST: Sum of  Tax IGST  amount charged.\n\n"

    "Important:\n"
    "- Only output the final result in raw JSON (no explanation, no formatting, no markdown).\n"
    "- If a field is missing, use null as its value.\n"
    "- The key names in JSON must match the ones provided above **exactly**.\n"
)

        top_chunks = get_top_chunks(query, chunks, index)

        context = "\n".join(top_chunks)
        prompt = query.format(context=context)

#         prompt = f"""
# You are an advanced invoice parser and data analyzer. Analyze the text below and extract the following fields. 
# Return the result strictly in valid **JSON format** with the keys **exactly as listed** below. 
# Do not include any explanations or introductory phrases like "Here is the extracted data".

# Required fields:

# - Invoice Number: The unique identifier of the invoice.
# - Invoice Date: The date when the invoice was issued.
# - Seller Name: The name of the seller.
# - Buyer Name: The name of the buyer.
# - Order Number: The purchase order or reference number related to this invoice.
# - GST Number: The GST identification number mentioned in the invoice.
# - Description: Brief description of the billed items or services.
# - Final Amount: The total amount payable.
# - IGST Tax Rate: The Total IGST Tax Rate (e.g., 18%).
# - CGST Tax Rate: The Total CGST Tax Rate (e.g., 9%).
# - SGST Tax Rate: The Total SGST Tax Rate (e.g., 9%).
# - Tax Amount: The total tax charged (sum of CGST, SGST, IGST).
# - Tax Type: List of tax types applied (e.g., ["CGST", "SGST"]).
# - CGST: Total CGST  amount charged .
# - SGST: Total SGST  amount charged .
# - IGST: Total IGST  amount charged .


# Text:
# {context}
# """
        result = query_groq_llm(prompt)
#         cache.set(pdf_text, result)
        return result

    results = []
    cache = CacheManager(cache_path)
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            print(pdf_path)
            text = extract_text_from_pdf(pdf_path)
            structured_data = query_llm_with_rag_and_cache(text, cache)
            print(f"\n {os.path.basename(pdf_path)}\n{structured_data}\n")
            results.append(structured_data)
            print("sssssssss",json.loads(structured_data))
        except Exception as e:
            print(f" Error with {pdf_path}: {e}")

    cache.close()
    return results
