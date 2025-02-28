import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

CDP_DOCS = {
    "segment": "https://segment.com/docs/?ref=nav",
    "mparticle": "https://docs.mparticle.com/",
    "lytics": "https://docs.lytics.com/",
    "zeotap": "https://docs.zeotap.com/home/en-us/"
}

def fetch_documentation(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            print("\n✅ DOCUMENTATION FETCHED:")
            print(text[:2000])  
            print("\n✅ END OF FETCHED DATA PREVIEW\n")

            return text
        else:
            print(f"\n❌ Failed to fetch {url} - Status Code: {response.status_code}\n")
            return ""
    except Exception as e:
        print(f"\n❌ Error fetching {url}: {e}\n")
        return ""

def extract_relevant_info(doc_text, query):
    query_lower = query.lower()
    lines = doc_text.split("\n") 

    best_match = ""

    for i, line in enumerate(lines):
        if query_lower in line.lower():  
            best_match = f"🔹 {line.strip()}\n" 
            best_match += "\n".join(lines[i+1:i+6])  
            break

    if not best_match:
        query_words = query_lower.split()
        scored_lines = []
        for line in lines:
            match_count = sum(1 for word in query_words if word in line.lower())
            if match_count > 0:
                scored_lines.append((match_count, line))

        scored_lines.sort(reverse=True, key=lambda x: x[0])
        best_match = "\n".join(line for _, line in scored_lines[:5])

    return best_match if best_match else "❌ No relevant information found in the documentation."

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    user_question = data.get("question", "").strip().lower()

    if not user_question:
        return jsonify({"answer": "❌ Please provide a valid question."})

    matched_cdp = None
    for cdp in CDP_DOCS.keys():
        if cdp in user_question:
            matched_cdp = cdp
            break

    if not matched_cdp:
        return jsonify({"answer": "❌ No relevant CDP identified in the question."})

    doc_text = fetch_documentation(CDP_DOCS[matched_cdp])

    if not doc_text:
        return jsonify({"answer": f"❌ Unable to fetch {matched_cdp} documentation."})

    answer = extract_relevant_info(doc_text, user_question)

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
