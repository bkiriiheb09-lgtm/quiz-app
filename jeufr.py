from flask import Flask, render_template_string, request, redirect, url_for
import json
import os

app = Flask(__name__)
FILENAME = "questions.json"

def load_questions():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_questions(questions):
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)

# قالب HTML بسيط وعصري للواجهة
HTML_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Quiz Éducatif</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f7f6; text-align: center; padding: 50px; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); display: inline-block; width: 400px; text-align: left; }
        h2 { color: #333; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; }
        button:hover { background: #45a049; }
        label { display: block; margin: 10px 0; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎓 Quiz Éducatif</h2>
        {% if question %}
            <form method="POST">
                <p><b>Question {{ q_index + 1 }} :</b> {{ question.question }}</p>
                {% for i, opt in enumerate(question.options) %}
                    <label>
                        <input type="radio" name="answer" value="{{ i }}" required> {{ opt }}
                    </label>
                {% endfor %}
                <button type="submit">Valider</button>
            </form>
        {% else %}
            <h3>🎉 Quiz Terminé !</h3>
            <p>Score final : <b>{{ score }}</b> / {{ total }}</p>
            <a href="/"><button recommencer</button></a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def quiz():
    questions = load_questions()
    if not questions:
        return "<h3>⚠️ Aucune question enregistrée dans questions.json !</h3>"
    
    # سنبسط العرض ليكون تجربة ويب أولية
    q = questions[0] # مثال للسؤال الأول للاختبار
    return render_template_string(HTML_TEMPLATE, question=q, q_index=0, enumerate=enumerate)

if __name__ == '__main__':
    app.run(debug=True)


