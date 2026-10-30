from flask import Flask, request, render_template_string
import json
import os

app = Flask(__name__)
FILENAME = "questions.json"

def load_questions():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    questions = load_questions()
    if not questions:
        return "<h3>⚠️ Aucune question trouvée dans questions.json !</h3>"
    
    q = questions[0] # عرض السؤال الأول للاختبار
    options_html = "".join([f'<label><input type="radio" name="q"> {opt}</label><br>' for opt in q["options"]])
    
    return f"""
    <!doctype html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Quiz Éducatif</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f7f6; text-align: center; padding: 50px; }}
            .card { background: white; width: 95%; max-width: 400px; margin: 20px auto; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); box-sizing: border-box; }
            h2 {{ color: #333; }}
            button {{ background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 15px; }}
            label {{ display: block; margin: 10px 0; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎓 Quiz Éducatif</h2>
            <p><b>Question :</b> {q['question']}</p>
            <form>
                {options_html}
                <button type="submit">Valider</button>
            </form>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
