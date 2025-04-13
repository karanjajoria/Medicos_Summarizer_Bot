from flask import Flask, render_template, request
from markupsafe import Markup
import ollama
import os
import PyPDF2
import markdown2
import re

app = Flask(__name__, template_folder='../templates', static_folder='../static')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def markdown_with_underline(text):
    text = markdown2.markdown(text)
    text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)
    return text

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", Patient_info=None, Diagnosis_Overview=None, error=None)

@app.route("/summarize", methods=["POST"])
def summarize():
    if 'pdf' not in request.files:
        return render_template("index.html", Patient_info=None, Diagnosis_Overview=None, error="No file uploaded.")

    file = request.files['pdf']
    language = request.form.get('language', 'english')

    if file.filename == '':
        return render_template("index.html", Patient_info=None, Diagnosis_Overview=None, error="No file selected.")

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        pdf_reader = PyPDF2.PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        if not text.strip():
            return render_template("index.html", Patient_info=None, Diagnosis_Overview=None, Medical_History = None , Prescription_Summary = None , Treatment_Plan = None , Lifestyle_Recommendation = None , Overall_summary = None , error="No text found in PDF.")
        
        #Patient Info
        Patient_info = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Basic Information of the patient such as Name, age, sex, date of report and Doctor:\n{text}"}]
        )['message']['content']

        #Diagnosis Overview
        Diagnosis_Overview = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"An overview of Patient primary diagnosis, secondary conditions and key points regarding diagnosis:\n{text}"}]
        )['message']['content']

        #Medical History
        Medical_History = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Medical history of the patient such as past records, family history and current medication:\n{text}"}]
        )['message']['content']

        #Precription Summary
        Prescription_Summary = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"What medication should he/she take, Duration and instructions for the medication:\n{text}"}]
        )['message']['content']

        #Treatment_Plan
        Treatment_Plan = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Recommended Treatement:\n{text}"}]
        )['message']['content']
    
        #Lifestyle Recommendation
        Lifestyle_Recommendation = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Lifestyle recommendation:\n{text}"}]
        )['message']['content']

        #Overall Summary
        Overall_summary = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": f"Summarize this medical report:\n{text}"}]
        )['message']['content']



        if language.lower() != "english":
            Patient_info = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": f"Translate this to {language}:\n{Patient_info}"}]
            )['message']['content']

            Diagnosis_Overview = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": f"Translate this to {language}:\n{Diagnosis_Overview}"}]
            )['message']['content']

            #Medical History
            Medical_History = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": f"Translate this to {language}:\n{Medical_History}:\n{text}"}]
            )['message']['content']

            #Precription Summary
            Prescription_Summary = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": f"Translate this to {language}:\n{Prescription_Summary}:\n{text}"}]
            )['message']['content']

            #Treatment_Plan
            Treatment_Plan = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": f"Translate this to {language}:\n{Treatment_Plan}:\n{text}"}]
            )['message']['content']
        
            #Lifestyle Recommendation
            Lifestyle_Recommendation = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": f"Translate this to {language}:\n{Lifestyle_Recommendation}:\n{text}"}])['message']['content']

            #Overall Summary
            Overall_summary = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": f"Translate this to {language}:\n{Overall_summary}:\n{text}"}])
            ['message']['content']


        return render_template(
            "index.html",
            Patient_info=Markup(markdown_with_underline(Patient_info)),
            Diagnosis_Overview=Markup(markdown_with_underline(Diagnosis_Overview)),
            Medical_History = Markup(markdown_with_underline(Medical_History)),
            Prescription_Summary = Markup(markdown_with_underline(Prescription_Summary)),
            Treatment_Plan = Markup(markdown_with_underline(Treatment_Plan)),
            Lifestyle_Recommendation = Markup(markdown_with_underline(Lifestyle_Recommendation)),
            Overall_summary = Markup(markdown_with_underline(Overall_summary)),
            error=None
        )

    except Exception as e:
        return render_template("index.html", Patient_info=None, Diagnosis_Overview=None, Medical_History = None , Prescription_Summary = None , Treatment_Plan = None , Lifestyle_Recommendation = None, Overall_summary = None ,error=str(e))

if __name__ == "__main__":
    app.run(debug=True)
