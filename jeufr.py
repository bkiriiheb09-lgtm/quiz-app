import os
import json
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

TESTS_FILE = "tests.json"
TEACHER_CODE = "1234"

def load_tests():
    if os.path.exists(TESTS_FILE):
        try:
            with open(TESTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {
        "اختبار عام 1": [
            {"question": "ما عاصمة تونس؟", "options": ["سوسة", "تونس العاصمة", "صفاقس"], "answer": 1},
            {"question": "كم عدد ركعات صلاة الصبح؟", "options": ["2", "3", "4"], "answer": 0}
        ]
    }

def save_tests(tests):
    with open(TESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(tests, f, ensure_ascii=False, indent=4)

HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>منصة الاختبارات التعليمية</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e3a8a;
            color: #000000;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .card {
            background: #ffffff;
            width: 95%;
            max-width: 500px;
            margin: 30px auto;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            box-sizing: border-box;
            text-align: right;
        }
        h2, h3, p {
            color: #000000;
        }
        button, input[type="submit"], a.btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 12px 20px;
            margin: 10px 0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            display: block;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
        }
        button:hover, a.btn:hover {
            background: #2563eb;
        }
        input[type="text"], input[type="password"], select {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 16px;
        }
        label {
            display: block;
            margin: 10px 0;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
    <script>
        function playClickSound() {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(400, ctx.currentTime);
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.08);
        }

        function playSuccessSound() {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
                let osc = ctx.createOscillator();
                let gain = ctx.createGain();
                osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.1);
                gain.gain.setValueAtTime(0.2, ctx.currentTime + i * 0.1);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(ctx.currentTime + i * 0.1);
                osc.stop(ctx.currentTime + i * 0.1 + 0.15);
            });
        }

        function playFailSound() {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            [300, 200].forEach((freq, i) => {
                let osc = ctx.createOscillator();
                let gain = ctx.createGain();
                osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.2);
                gain.gain.setValueAtTime(0.2, ctx.currentTime + i * 0.2);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(ctx.currentTime + i * 0.2);
                osc.stop(ctx.currentTime + i * 0.2 + 0.2);
            });
        }
        
        document.addEventListener("DOMContentLoaded", () => {
            document.querySelectorAll("button, input, label").forEach(el => {
                el.addEventListener("click", playClickSound);
            });
        });
    </script>
</head>
<body>
    <div class="card">
        {{content}}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    content = """
        <h2 style="text-align: center;">منصة الاختبارات الذكية</h2>
        <p style="text-align: center;">اختر وضع الاستخدام:</p>
        <a href="/student" class="btn">👨‍🎓 وضع التلميذ (Mode Élève)</a>
        <a href="/teacher_login" class="btn" style="background: #047857;">👨‍🏫 وضع الأستاذ (Mode Enseignant)</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/student')
def student():
    tests = load_tests()
    if not tests:
        content = "<h3>لا توجد اختبارات متاحة حالياً.</h3><a href='/' class='btn'>الرجوع</a>"
        return render_template_string(HTML_TEMPLATE, content=content)
    
    tests_html = ""
    for t_name in tests.keys():
        tests_html += f'<a href="/quiz/{t_name}" class="btn">📝 اختبار: {t_name}</a>'
        
    content = f"""
        <h2>قائمة الاختبارات المتاحة</h2>
        <p>اختر اختباراً لبدء الإجابة:</p>
        {tests_html}
        <br>
        <a href='/' class='btn' style='background: #6b7280;'>الرجوع للقائمة الرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/quiz/<test_name>', methods=['GET', 'POST'])
def quiz(test_name):
    tests = load_tests()
    if test_name not in tests:
        return redirect(url_for('student'))
    
    questions = tests[test_name]
    
    if request.method == 'POST':
        score = 0
        total = len(questions)
        for i, q in enumerate(questions):
            user_ans = request.form.get(f'q_{i}')
            if user_ans is not None and int(user_ans) == q['answer']:
                score += 1
        
        passed = (score / total) >= 0.5
        sound_script = "playSuccessSound();" if passed else "playFailSound();"
        msg = "🎉 ممتاز جداً! تصفيق حار لتفوقك!" if passed else "💪 حاول مرة أخرى، يمكنك تحسين مستواك!"
        
        content = f"""
            <h2>نتيجة الاختبار: {test_name}</h2>
            <p>لقد أجبت على <b>{score}</b> من أصل <b>{total}</b> إجابة صحيحة.</p>
            <p style="font-size: 18px; font-weight: bold; color: {'#16a34a' if passed else '#dc2626'};">{msg}</p>
            <script>
                setTimeout(() => {{ {sound_script} }}, 500);
            </script>
            <br>
            <a href="/quiz/{test_name}" class="btn">🔄 إعادة الاختبار</a>
            <a href="/student" class="btn" style="background: #6b7280;">اختيار اختبار آخر</a>
        """
        return render_template_string(HTML_TEMPLATE, content=content)
    
    q_html = ""
    for i, q in enumerate(questions):
        opts = ""
        for j, opt in enumerate(q['options']):
            opts += f'<label><input type="radio" name="q_{i}" value="{j}" required> {opt}</label>'
        q_html += f"<div style='margin-bottom: 20px;'><p><b>السؤال {i+1}:</b> {q['question']}</p>{opts}</div>"
        
    content = f"""
        <h2>اختبار: {test_name}</h2>
        <form method="POST">
            {q_html}
            <button type="submit">إرسال الإجابات (Valider)</button>
        </form>
        <br>
        <a href="/student" class="btn" style="background: #6b7280;">الرجوع للقائمة</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    error = ""
    if request.method == 'POST':
        code = request.form.get('code')
        if code == TEACHER_CODE:
            return redirect(url_for('teacher_dashboard'))
        else:
            error = "❌ الكود السري غير صحيح!"
            
    content = f"""
        <h2>تسجيل دخول الأستاذ</h2>
        <p>الرجاء إدخال الكود السري:</p>
        <form method="POST">
            <input type="password" name="code" placeholder="أدخل الكود (مثال: 1234)" required>
            <button type="submit">دخول</button>
        </form>
        <p style="color: red;">{error}</p>
        <br>
        <a href="/" class="btn" style="background: #6b7280;">الرجوع</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/teacher_dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    tests = load_tests()
    msg = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_test':
            t_name = request.form.get('test_name').strip()
            if t_name and t_name not in tests:
                tests[t_name] = []
                save_tests(tests)
                msg = f"تم إضافة الاختبار '{t_name}' بنجاح!"
        elif action == 'add_question':
            t_name = request.form.get('test_name')
            q_text = request.form.get('question')
            opt0 = request.form.get('opt0')
            opt1 = request.form.get('opt1')
            opt2 = request.form.get('opt2')
            ans = int(request.form.get('answer'))
            if t_name in tests:
                tests[t_name].append({
                    "question": q_text,
                    "options": [opt0, opt1, opt2],
                    "answer": ans
                })
                save_tests(tests)
                msg = "تم إضافة السؤال بنجاح!"
                
    test_options = "".join([f'<option value="{name}">{name}</option>' for name in tests.keys()])
    
    content = f"""
        <h2>لوحة تحكم الأستاذ</h2>
        <p style="color: green;">{msg}</p>
        
        <hr style="margin: 20px 0;">
        <h3>إضافة اختبار جديد</h3>
        <form method="POST">
            <input type="hidden" name="action" value="add_test">
            <input type="text" name="test_name" placeholder="اسم الاختبار الجديد" required>
            <button type="submit">إضافة الاختبار</button>
        </form>
        
        <hr style="margin: 20px 0;">
        <h3>إضافة سؤال لاختبار</h3>
        <form method="POST">
            <input type="hidden" name="action" value="add_question">
            <label>اختر الاختبار:</label>
            <select name="test_name">{test_options}</select>
            <input type="text" name="question" placeholder="نص السؤال" required>
            <input type="text" name="opt0" placeholder="الخيار الأول" required>
            <input type="text" name="opt1" placeholder="الخيار الثاني" required>
            <input type="text" name="opt2" placeholder="الخيار الثالث" required>
            <label>رقم الإجابة الصحيحة:</label>
            <select name="answer">
                <option value="0">الخيار الأول</option>
                <option value="1">الخيار الثاني</option>
                <option value="2">الخيار الثالث</option>
            </select>
            <button type="submit" style="background: #047857;">إضافة السؤال</button>
        </form>
        
        <br>
        <a href="/" class="btn" style="background: #6b7280;">تسجيل الخروج / الرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

        
     
