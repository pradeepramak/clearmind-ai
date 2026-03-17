from PIL import Image
from flask import Flask, render_template, request
import pdfplumber
import google.generativeai as genai
import os

# 🔐 Load API key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set in environment variables")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")

app = Flask(__name__)

# Global storage
document_context = ""
analysis_result = ""
chat_history = []


# ✅ Safe AI call (no crash)
def safe_generate(content):
    try:
        response = model.generate_content(content)
        return response.text if response and response.text else "⚠️ No response from AI."
    except Exception as e:
        print("ERROR:", e)  # Shows in Render logs
        return "⚠️ AI service temporarily unavailable. Please try again."


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():

    global document_context, analysis_result, chat_history

    document_context = ""
    analysis_result = ""
    chat_history = []

    if 'file' not in request.files:
        return "No file uploaded."

    file = request.files['file']

    if file.filename == '':
        return "Please select a file."

    filename = file.filename.lower()
    print("File received:", filename)

    prompt = """
You are a document analysis assistant.

Analyze the following document and return:

Document Type:
Summary:
Key Details:
Important Notes:

Explain everything clearly in simple English.
"""

    # -------- PDF --------
    if filename.endswith(".pdf"):

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    document_context += text

        # Handle empty PDF
        if not document_context:
            return render_template(
                "result.html",
                result="No readable text found in this PDF.",
                chat=[]
            )

        full_prompt = prompt + "\n\nDocument:\n" + document_context
        analysis_result = safe_generate(full_prompt)

    # -------- IMAGE --------
    elif filename.endswith((".png", ".jpg", ".jpeg")):

        try:
            image = Image.open(file)
            analysis_result = safe_generate([prompt, image])
            document_context = "Image document"
        except Exception as e:
            print("Image Error:", e)
            return "Error processing image."

    else:
        return "Unsupported file type."

    return render_template(
        "result.html",
        result=analysis_result,
        chat=chat_history
    )


@app.route('/ask', methods=['POST'])
def ask():

    global chat_history

    question = request.form['question']

    prompt = f"""
You are a document assistant.

Document:
{document_context}

Conversation:
{chat_history}

Question:
{question}

Answer clearly using only the document.
"""

    answer = safe_generate(prompt)

    chat_history.append({
        "q": question,
        "a": answer
    })

    return render_template(
        "result.html",
        result=analysis_result,
        chat=chat_history
    )


if __name__ == "__main__":
    app.run(debug=True)