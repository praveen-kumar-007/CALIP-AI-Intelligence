import urllib.request
import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))
import requests
from app.core.config import settings

# 1. Fetch live document from calipai.com as an AI crawler
doc_url = "https://www.calipai.com/documents/doc-Documents_1779289485_pdf"
headers_crawler = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"}
req = urllib.request.Request(doc_url, headers=headers_crawler)
resp = urllib.request.urlopen(req, timeout=15)
retrieved_markdown = resp.read().decode("utf-8")

print(f"Retrieved {len(retrieved_markdown)} bytes from {doc_url}")

# 2. Prompt LLM simulating ChatGPT / Claude / Gemini with the retrieved content
prompt = (
    "A user asked: 'What is document doc-Documents_1779289485_pdf from https://www.calipai.com about, and what are its key details?'\n\n"
    "Below is the exact Markdown text retrieved from https://www.calipai.com/documents/doc-Documents_1779289485_pdf:\n\n"
    + retrieved_markdown[:5000]
    + "\n\nAnswer the user based ONLY on the verified data retrieved from calipai.com."
)

groq_headers = {
    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
    "Content-Type": "application/json",
}
payload = {
    "model": "qwen/qwen3.8-27b",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 800,
    "temperature": 0.1,
}

res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=groq_headers, json=payload, timeout=20)
answer = res.json()["choices"][0]["message"]["content"]

with open("scripts/sample_ai_response.txt", "w", encoding="utf-8") as f:
    f.write(answer)

print("AI Response generated successfully! Length:", len(answer))
