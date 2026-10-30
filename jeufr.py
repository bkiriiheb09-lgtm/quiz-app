import os
import json
import time
import urllib.parse
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_quiz_key_2026"

TESTS_FILE = "tests.json"
ACTIVE_TEST_FILE = "active_test.json"
RESULTS_FILE = "results.json"
TEACHER_CODE = "1234"

def load_json(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_val
    return default_val

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_tests():
    return load_json(TESTS_FILE, {
        "اختبار عام 1": [
            {"question": "ما عاصمة تونس؟", "options": ["سوسة", "تونس العاصمة", "صفاقس"], "answer": 1},
            {"question": "كم عدد ركعات صلاة الصبح؟", "options": ["2", "3", "4"], "answer": 0}
        ]
    })

def load_active_test():
    return load_json(ACTIVE_TEST_FILE, {"active": ""})

def load_results():
    return load_json(RESULTS_FILE, {})

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
            max-width: 600px;
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
        .timer-box {
            background: #fee2e2;
            color: #dc2626;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #fecaca;
        }
        table.ranking {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        table.ranking th, table.ranking td {
            border: 1px solid #d1d5db;
            padding: 8px;
            text-align: center;
            font-size: 14px;
        }
        table.ranking th {
            background-color: #f3f4f6;
            color: #111827;
        }
        .admin-test-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f9fafb;
            padding: 10px;
            margin: 8px 0;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
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
        {{ content | safe }}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    content = """
        <h2 style="text-align: center;">منصة الاختبارات الذكية</h2>
        <p style="text-align: center;">اختر وضع الاستخدام:</p>
        <a href="/student_entry" class="btn">👨‍🎓 وضع التلميذ (Mode Élève)</a>
        <a href="/teacher_login" class="btn" style="background: #047857;">👨‍🏫 وضع الأستاذ (Mode Enseignant)</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/student_entry', methods=['GET', 'POST'])
def student_entry():
    if request.method == 'POST':
        name = request.form.get('student_name', '').strip()
        if name:
            session['student_name'] = name
            active_data = load_active_test()
            active_test = active_data.get('active')
            if active_test:
                return redirect(url_for('quiz', test_name=active_test))
            else:
                return redirect(url_for('waiting_room'))
    
    content = """
        <h2>تسجيل دخول التلميذ</h2>
        <p>الرجاء إدخال اسمك ولقبك للبدء:</p>
        <form method="POST">
            <input type="text" name="student_name" placeholder="الاسم واللقب" required>
            <button type="submit">دخول إلى الاختبار</button>
        </form>
        <br>
        <a href="/" class="btn" style="background: #6b7280;">الرجوع للرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/waiting_room')
def waiting_room():
    active_data = load_active_test()
    active_test = active_data.get('active')
    if active_test:
        return redirect(url_for('quiz', test_name=active_test))
    
    content = """
        <h2>قاعة الانتظار</h2>
        <p>⏳ في انتظار الأستاذ حتى يختار الاختبار ويقوم بفتحه...</p>
        <script>
            setTimeout(() => { window.location.reload(); }, 3000);
        </script>
        <br>
        <a href="/" class="btn" style="background: #6b7280;">الرجوع للرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/quiz/<test_name>', methods=['GET', 'POST'])
def quiz(test_name):
    if 'student_name' not in session:
        return redirect(url_for('student_entry'))
    
    tests = load_tests()
    if test_name not in tests:
        return redirect(url_for('student_entry'))
    
    questions = tests[test_name]
    
    if request.method == 'POST':
        score = 0
        total = len(questions)
        for i, q in enumerate(questions):
            user_ans = request.form.get(f'q_{i}')
            if user_ans is not None and int(user_ans) == q['answer']:
                score += 1
        
        start_time = session.get('start_time', time.time())
        time_taken = round(time.time() - start_time, 1)
        
        results = load_results()
        if test_name not in results:
            results[test_name] = []
        
        student_name = session['student_name']
        results[test_name] = [r for r in results[test_name] if r['name'] != student_name]
        results[test_name].append({
            "name": student_name,
            "score": score,
            "total": total,
            "time": time_taken
        })
        save_json(RESULTS_FILE, results)
        
        sorted_results = sorted(results[test_name], key=lambda x: (-x['score'], x['time']))
        
        ranking_html = ""
        for rank, res in enumerate(sorted_results, 1):
            ranking_html += f"""
                <tr>
                    <td>{rank}</td>
                    <td>{res['name']}</td>
                    <td><b>{res['score']} / {res['total']}</b></td>
                    <td>{res['time']} ثانية</td>
                </tr>
            """
            
        passed = (score / total) >= 0.5
        sound_script = "playSuccessSound();" if passed else "playFailSound();"
        msg = "🎉 ممتاز جداً! تفوق باهر في الاختبار!" if passed else "💪 حاول مرة أخرى في المرة القادمة!"
        
        content = f"""
            <h2>نتيجة الاختبار: {test_name}</h2>
            <p>التلميذ: <b>{student_name}</b></p>
            <p>لقد أجبت على <b>{score}</b> من أصل <b>{total}</b> إجابة صحيحة.</p>
            <p>الوقت المستغرق: <b>{time_taken} ثانية</b></p>
            <p style="font-size: 16px; font-weight: bold; color: {'#16a34a' if passed else '#dc2626'};">{msg}</p>
            
            <h3 style="margin-top: 20px;">🏆 ترتيب التلامذة:</h3>
            <table class="ranking">
                <tr>
                    <th>المرتبة</th>
                    <th>الاسم واللقب</th>
                    <th>النقاط</th>
                    <th>الوقت</th>
                </tr>
                {ranking_html}
            </table>
            
            <script>
                setTimeout(() => {{ {sound_script} }}, 500);
            </script>
            <br>
            <a href="/" class="btn" style="background: #6b7280;">العودة للرئيسية</a>
        """
        return render_template_string(HTML_TEMPLATE, content=content)
    
    session['start_time'] = time.time()
    
    q_html = ""
    for i, q in enumerate(questions):
        opts = ""
        for j, opt in enumerate(q['options']):
            opts += f'<label><input type="radio" name="q_{i}" value="{j}" required> {opt}</label>'
        q_html += f"<div style='margin-bottom: 20px;'><p><b>السؤال {i+1}:</b> {q['question']}</p>{opts}</div>"
        
    content = f"""
        <h2>اختبار: {test_name}</h2>
        <p>التلميذ: <b>{session.get('student_name')}</b></p>
        <div class="timer-box" id="timer">⏳ الوقت المتبقي: 03:00</div>
        
        <form id="quizForm" method="POST">
            {q_html}
            <button type="submit">إرسال الإجابات (Valider)</button>
        </form>

        <script>
            let timeLeft = 180;
            const timerElement = document.getElementById("timer");
            
            const countdown = setInterval(() => {
                let minutes = Math.floor(timeLeft / 60);
                let seconds = timeLeft % 60;
                
                timerElement.innerHTML = ⏳ الوقت المتبقي: ${{minutes.toString().padStart(2, '0')}}:${seconds.toString().padStart(2, '0')}};
                
                if (timeLeft <= 0) {
                    clearInterval(countdown);
                    alert("⏰ انتهى الوقت المتبقي! سيتم إرسال إجاباتك تلقائياً.");
                    document.getElementById("quizForm").submit();
                }
                timeLeft--;
            }, 1000);
        </script>
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
    active_data = load_active_test()
    msg = ""
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'set_active':
            chosen_test = request.form.get('active_test')
            active_data['active'] = chosen_test
            save_json(ACTIVE_TEST_FILE, active_data)
            msg = f"تم تفعيل الاختبار '{chosen_test}' بنجاح ليظهر للتلامذة!"
        elif action == 'add_test':
            t_name = request.form.get('test_name').strip()
            if t_name and t_name not in tests:
                tests[t_name] = []
                save_json(TESTS_FILE, tests)
                msg = f"تم إضافة الاختبار '{t_name}' بنجاح!"
        elif action == 'delete_test':
            t_name = request.form.get('test_name')
            if t_name in tests:
                del tests[t_name]
                save_json(TESTS_FILE, tests)
                if active_data.get('active') == t_name:
                    active_data['active'] = ""
                    save_json(ACTIVE_TEST_FILE, active_data)
                msg = f"تم حذف الاختبار '{t_name}' بنجاح!"

    active_test = active_data.get('active', '')
    teacher_qr_html = ""
    if active_test:
        quiz_url = f"https://quiz-app-7wny.onrender.com/quiz/{urllib.parse.quote(active_test)}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data={quiz_url}"
        teacher_qr_html = f"""
            <div style="margin-top: 20px; padding: 15px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; text-align: center;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #1e3a8a;">📱 QR كود خاص بالاختبار النشط الحالي ({active_test}):</p>
                <img src="{qr_url}" alt="QR Code" style="width: 150px; height: 150px; border-radius: 6px;">
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #4b5563;">اعرض هذا الكود لتلامذتك لمسحه والدخول المباشر</p>
            </div>
        """
                
    test_select_options = "".join([f'<option value="{name}" {"selected" if name == active_test else ""}>{name}</option>' for name in tests.keys()])
    
    tests_management_html = ""
    for name in tests.keys():
        tests_management_html += f"""
            <div class="admin-test-row">
                <span><b>{name}</b> ({len(tests[name])} أسئلة)</span>
                <div style="display: flex; gap: 5px;">
                    <a href="/teacher/edit_test/{urllib.parse.quote(name)}" class="btn" style="padding: 6px 12px; font-size: 14px; margin: 0; background: #2563eb;">⚙️ تعديل/أسئلة</a>
                    <form method="POST" style="margin:0;" onsubmit="return confirm('هل أنت متأكد من حذف هذا الاختبار؟');">
                        <input type="hidden" name="action" value="delete_test">
                        <input type="hidden" name="test_name" value="{name}">
                        <button type="submit" style="padding: 6px 12px; font-size: 14px; margin: 0; background: #dc2626;">🗑️ حذف</button>
                    </form>
                </div>
            </div>
        """
    
    content = f"""
        <h2>لوحة تحكم الأستاذ</h2>
        <p style="color: green; font-weight: bold;">{msg}</p>
        
        <hr style="margin: 20px 0;">
        <h3>🎯 اختيار الاختبار النشط للتلامذة</h3>
        <form method="POST">
            <input type="hidden" name="action" value="set_active">
            <label>اختر الاختبار الذي سيعمل الآن:</label>
            <select name="active_test">{test_select_options}</select>
            <button type="submit" style="background: #2563eb;">تفعيل هذا الاختبار</button>
        </form>
        
        {teacher_qr_html}
        
        <hr style="margin: 20px 0;">
        <h3>📚 إدارة الاختبارات الحالية</h3>
        {tests_management_html if tests_management_html else "<p>لا توجد اختبارات حالياً.</p>"}
        
        <hr style="margin: 20px 0;">
        <h3>إضافة اختبار جديد</h3>
        <form method="POST">
            <input type="hidden" name="action" value="add_test">
            <input type="text" name="test_name" placeholder="اسم الاختبار الجديد" required>
            <button type="submit" style="background: #059669;">إضافة الاختبار</button>
        </form>
        
        <br>
        <a href="/" class="btn" style="background: #6b7280;">تسجيل الخروج / الرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/teacher/edit_test/<test_name>', methods=['GET', 'POST'])
def edit_test(test_name):
    tests = load_tests()
    if test_name not in tests:
        return redirect(url_for('teacher_dashboard'))
    
    msg = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_question':
            q_text = request.form.get('question')
            opt0 = request.form.get('opt0')
            opt1 = request.form.get('opt1')
            opt2 = request.form.get('opt2')
            ans = int(request.form.get('answer'))
            tests[test_name].append({
                "question": q_text,
                "options": [opt0, opt1, opt2],
                "answer": ans
            })
            save_json(TESTS_FILE, tests)
            msg = "تم إضافة السؤال بنجاح!"
        elif action == 'delete_question':
            q_idx = int(request.form.get('q_idx'))
            if 0 <= q_idx < len(tests[test_name]):
                tests[test_name].pop(q_idx)
                save_json(TESTS_FILE, tests)
                msg = "تم حذف السؤال بنجاح!"

    questions = tests[test_name]
    q_list_html = ""
    for idx, q in enumerate(questions):
        correct_opt = q['options'][q['answer']]
        q_list_html += f"""
            <div class="admin-test-row">
                <div style="text-align: right; flex-grow: 1;">
                    <p style="margin: 0 0 5px 0;"><b>السؤال {idx+1}:</b> {q['question']}</p>
                    <p style="margin: 0; font-size: 13px; color: #4b5563;">الإجابة الصحيحة: <b>{correct_opt}</b></p>
                </div>
                <form method="POST" style="margin: 0;" onsubmit="return confirm('هل تريد حذف هذا السؤال؟');">
                    <input type="hidden" name="action" value="delete_question">
                    <input type="hidden" name="q_idx" value="{idx}">
                    <button type="submit" style="padding: 6px 10px; font-size: 13px; margin: 0; background: #dc2626;">حذف</button>
                </form>
            </div>
        """

    content = f"""
        <h2>إدارة اختبار: {test_name}</h2>
        <p style="color: green; font-weight: bold;">{msg}</p>
        
        <h3 style="margin-top: 15px;">أسئلة الاختبار الحالية:</h3>
        {q_list_html if q_list_html else "<p>لا توجد أسئلة في هذا الاختبار بعد.</p>"}
        
        <hr style="margin: 20px 0;">
        <h3>➕ إضافة سؤال جديد لهذا الاختبار</h3>
        <form method="POST">
            <input type="hidden" name="action" value="add_question">
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
            <button type="submit" style="background: #059669;">إضافة السؤال</button>
        </form>
        
        <br>
        <a href="/teacher_dashboard" class="btn" style="background: #6b7280;">الرجوع لوحة التحكم</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)






        
     
