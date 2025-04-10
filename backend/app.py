from flask import Flask, render_template, request, redirect, url_for
import ollama
import os
import PyPDF2

app = Flask(__name__, template_folder='../templates', static_folder='../static')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html', summary=None)


@app.route('/summarize', methods=['POST'])
def summarize():
    if 'pdf' not in request.files:
        return render_template('index.html', error="No file part", summary=None)

    file = request.files['pdf']

    if file.filename == '':
        return render_template('index.html', error="No selected file", summary=None)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Extract Text from PDF
    pdf_reader = PyPDF2.PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()

    if not text:
        return render_template('index.html', error="Could not extract text from PDF", summary=None)

    # Generate Summary using Ollama (Llama3 locally)
    try:
        response = ollama.chat(
            model='llama3',
            messages=[{"role": "user", "content": f"Summarize this medical report:\n{text}"}]
        )

        summary = response['message']['content']

    except Exception as e:
        return render_template('index.html', error=f"Error communicating with Ollama: {e}", summary=None)

    return render_template('index.html', summary=summary)


if __name__ == "__main__":
    app.run(debug=True)
