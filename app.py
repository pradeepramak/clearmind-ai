from PIL import Image
from flask import Flask, render_template, request
import pdfplumber
import google.generativeai as genai

# 🔐 ADD YOUR REAL API KEY HERE
genai.configure(api_key="AIzaSyDYa_6l36WKZiJg9fJhHziRZuQvLKx9peg")

model = genai.GenerativeModel("models/gemini-2.5-flash")

app = Flask(__name__)

# Global storage
document_context = ""
analysis_result = ""
chat_history = []


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():

    global document_context, analysis_result, chat_history

    document_context = ""
    chat_history = []

    if 'file' not in request.files:
        return "No file uploaded."

    file = request.files['file']

    if file.filename == '':
        return "Please select a file."

    filename = file.filename.lower()

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

        full_prompt = prompt + "\n\nDocument:\n" + document_context
        response = model.generate_content(full_prompt)

    # -------- IMAGE --------
    elif filename.endswith((".png", ".jpg", ".jpeg")):

        image = Image.open(file)

        response = model.generate_content([prompt, image])

        # Store placeholder context
        document_context = "Image document"

    else:
        return "Unsupported file type."

    # Save analysis
    analysis_result = response.text

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

    response = model.generate_content(prompt)
    answer = response.text

    # Save conversation
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