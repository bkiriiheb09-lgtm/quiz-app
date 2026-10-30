import os
import json
import time
import uuid
import urllib.parse
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_quiz_key_device_isolated_2026"

def get_device_id():
    """الحصول على معرف فريد ومستقل لكل جهاز/متصفح"""
    if 'device_id' not in session:
        session['device_id'] = str(uuid.uuid4())
    return session['device_id']

def get_device_file():
    """تحديد اسم ملف البيانات الخاص بهذا الجهاز فقط"""
    d_id = get_device_id()
    safe_id = "".join(c for c in d_id if c.isalnum() or c in ('_', '-'))
    return f"device_{safe_id}.json"

def load_device_data():
    """تحميل بيانات الجهاز الحالي من ملفه الخاص"""
    filename = get_device_file()
    default_data = {
        "tests": {},
        "active_test": {"active": "", "status": "waiting"},
        "results": {}
    }
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_device_data(data):
    """حفظ بيانات الجهاز الحالي في ملفه الخاص"""
    filename = get_device_file()
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Error saving device data:", e)

HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>منصة الاختبارات التعليمية</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background-color: #1e3a8a; color: #000; margin: 0; padding: 20px; text-align: center; }
        .card { background: #fff; width: 95%; max-width: 600px; margin: 30px auto; padding: 25px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); text-align: right; box-sizing: border-box; }
        h2, h3, p { color: #000; }
        button, input[type="submit"], a.btn { background: #3b82f6; color: white; border: none; padding: 12px 20px; margin: 10px 0; border-radius: 8px; cursor: pointer; font-size: 16px; text-decoration: none; display: block; width: 100%; box-sizing: border-box; text-align: center; }
        button:hover, a.btn:hover { background: #2563eb; }
        input[type="text"], input[type="password"], select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
        label { display: block; margin: 10px 0; font-size: 16px; cursor: pointer; }
        .timer-box { background: #fee2e2; color: #dc2626; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 18px; margin-bottom: 20px; text-align: center; border: 1px solid #fecaca; }
        table.ranking { width: 100%; border-collapse: collapse; margin-top: 15px; }
        table.ranking th, table.ranking td { border: 1px solid #d1d5db; padding: 8px; text-align: center; font-size: 14px; }
        table.ranking th { background-color: #f3f4f6; color: #111827; }
        .admin-test-row { display: flex; justify-content: space-between; align-items: center; background: #f9fafb; padding: 10px; margin: 8px 0; border-radius: 6px; border: 1px solid #e5e7eb; }
    </style>
    <script>
        function playClickSound() {
            try {
                var ctx = new (window.AudioContext || window.webkitAudioContext)();
                var osc = ctx.createOscillator();
                var gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(400, ctx.currentTime);
                gain.gain.setValueAtTime(0.1, ctx.currentTime);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.08);
            } catch(e) {}
        }
        document.addEventListener("DOMContentLoaded", function() {
            document.querySelectorAll("button, input, label").forEach(function(el) {
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
        <a href="/teacher_dashboard" class="btn" style="background: #047857;">👨‍🏫 وضع الأستاذ (Mode Enseignant)</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/student_entry', methods=['GET', 'POST'])
def student_entry():
    if request.method == 'GET':
        session.pop('student_name', None)
        session.pop('start_time', None)

    dev_data = load_device_data()
    active_data = dev_data["active_test"]
    test_name = active_data.get('active')
    
    if not test_name:
        content = """
            <h2>تنبيه</h2>
            <p>⏳ لم يقم الأستاذ بتفعيل أي اختبار على هذا الجهاز حتى الآن. الرجاء الانتظار قليلاً...</p>
            <script>
                setTimeout(function() {
                    var activeEl = document.activeElement;
                    if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'SELECT' || activeEl.tagName === 'TEXTAREA')) {
                        return;
                    }
                    window.location.reload();
                }, 3000);
            </script>
            <br>
            <a href="/" class="btn" style="background: #6b7280;">الرجوع للرئيسية</a>
        """
        return render_template_string(HTML_TEMPLATE, content=content)

    if request.method == 'POST':
        name = request.form.get('student_name', '').strip()
        if name:
            session['student_name'] = name
            results = dev_data["results"]
            
            if test_name not in results:
                results[test_name] = {"participants": [], "scores": [], "status": active_data.get('status', 'waiting')}
            
            existing_names = [p['name'] for p in results[test_name].get("participants", [])]
            if name not in existing_names:
                results[test_name]["participants"].append({"name": name, "joined_at": time.time()})
                save_device_data(dev_data)
            
            return redirect(url_for('waiting_room'))
    
    content = """
        <h2>تسجيل دخول التلميذ</h2>
        <p>الاختبار الحالي: <b>""" + test_name + """</b></p>
        <p>الرجاء إدخال اسمك ولقبك للالتحاق بقاعة الانتظار:</p>
        <form method="POST">
            <input type="text" name="student_name" placeholder="الاسم واللقب" required>
            <button type="submit">دخول قاعة الانتظار</button>
        </form>
        <br>
        <a href="/" class="btn" style="background: #6b7280;">الرجوع للرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/waiting_room')
def waiting_room():
    if 'student_name' not in session:
        return redirect(url_for('student_entry'))
    
    dev_data = load_device_data()
    active_data = dev_data["active_test"]
    test_name = active_data.get('active')
    status = active_data.get('status', 'waiting')
    
    if test_name and status == 'started':
        return redirect(url_for('quiz', test_name=test_name))
        
    content = """
        <h2>قاعة الانتظار</h2>
        <p>مرحباً <b>""" + session.get('student_name', '') + """</b></p>
        <p>⏳ في انتظار إعارة إشارة الانطلاق من الأستاذ للاختبار (<b>""" + str(test_name) + """</b>)...</p>
        <script>
            setTimeout(function() {
                var activeEl = document.activeElement;
                if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'SELECT' || activeEl.tagName === 'TEXTAREA')) {
                    return;
                }
                window.location.reload();
            }, 3000);
        </script>
        <br>
        <a href="/" class="btn" style="background: #6b7280;">الرجوع للرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/quiz/<test_name>', methods=['GET', 'POST'])
def quiz(test_name):
    if 'student_name' not in session:
        return redirect(url_for('student_entry'))
    
    dev_data = load_device_data()
    active_data = dev_data["active_test"]
    if active_data.get('status') == 'finished':
        return redirect(url_for('show_final_results', test_name=test_name))

    tests = dev_data["tests"]
    if test_name not in tests:
        return redirect(url_for('student_entry'))
    
    questions = tests[test_name]
    results = dev_data["results"]
    
    if test_name not in results:
        results[test_name] = {"participants": [], "scores": [], "status": "started"}
        
    student_name = session['student_name']
    
    if request.method == 'POST':
        score = 0
        total = len(questions)
        for i, q in enumerate(questions):
            user_ans = request.form.get('q_' + str(i))
            if user_ans is not None and int(user_ans) == q['answer']:
                score += 1
        
        start_time = session.get('start_time', time.time())
        time_taken = round(time.time() - start_time, 1)
        
        results[test_name]["scores"] = [r for r in results[test_name]["scores"] if r['name'] != student_name]
        results[test_name]["scores"].append({
            "name": student_name,
            "score": score,
            "total": total,
            "time": time_taken
        })
        
        total_participants = len(results[test_name].get("participants", []))
        total_finished = len(results[test_name].get("scores", []))
        if total_participants > 0 and total_finished >= total_participants:
            active_data['status'] = 'finished'
            results[test_name]['status'] = 'finished'
            
        save_device_data(dev_data)
        return redirect(url_for('student_waiting_results', test_name=test_name))
    
    session['start_time'] = time.time()
    q_html = ""
    for i, q in enumerate(questions):
        opts = ""
        for j, opt in enumerate(q['options']):
            opts += '<label><input type="radio" name="q_' + str(i) + '" value="' + str(j) + '" required> ' + opt + '</label>'
        q_html += "<div style='margin-bottom: 20px;'><p><b>السؤال " + str(i+1) + ":</b> " + q['question'] + "</p>" + opts + "</div>"
        
    content = """
        <h2>اختبار: """ + test_name + """</h2>
        <p>التلميذ: <b>""" + student_name + """</b></p>
        <div class="timer-box" id="timer">⏳ الوقت المتبقي: 03:00</div>
        <form id="quizForm" method="POST">
            """ + q_html + """
            <button type="submit">إرسال الإجابات (Valider)</button>
        </form>
        <script>
            var timeLeft = 180;
            var timerElement = document.getElementById("timer");
            var countdown = setInterval(function() {
                var minutes = Math.floor(timeLeft / 60);
                var seconds = timeLeft % 60;
                var minStr = minutes < 10 ? '0' + minutes : minutes;
                var secStr = seconds < 10 ? '0' + seconds : seconds;
                timerElement.innerHTML = '⏳ الوقت المتبقي: ' + minStr + ':' + secStr;
                
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

@app.route('/student_waiting_results/<test_name>')
def student_waiting_results(test_name):
    if 'student_name' not in session:
        return redirect(url_for('student_entry'))
        
    active_data = load_device_data()
    active_data = load_device_data()["active_test"]
    status = active_data.get('status', 'waiting')
    
    if status != 'finished':
        content = """
            <h2>في انتظار النتائج</h2>
            <p>✅ تم إرسال إجاباتك بنجاح يا <b>""" + session['student_name'] + """</b>!</p>
            <p>⏳ يرجى الانتظار حتى ينهي بقية الزملاء أو ينتهي الوقت لإعلان النتائج...</p>
            <script>
                setTimeout(function() {
                    var activeEl = document.activeElement;
                    if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'SELECT' || activeEl.tagName === 'TEXTAREA')) {
                        return;
                    }
                    window.location.reload();
                }, 3000);
            </script>
        """
        return render_template_string(HTML_TEMPLATE, content=content)
    else:
        return redirect(url_for('show_final_results', test_name=test_name))

@app.route('/results/<test_name>')
def show_final_results(test_name):
    dev_data = load_device_data()
    tests = dev_data["tests"]
    questions = tests.get(test_name, [])
    results = dev_data["results"]
    test_res = results.get(test_name, {"scores": []})
    sorted_scores = sorted(test_res.get("scores", []), key=lambda x: (-x['score'], x['time']))
    
    ranking_html = ""
    for rank, res in enumerate(sorted_scores, 1):
        ranking_html += "<tr><td>" + str(rank) + "</td><td>" + res['name'] + "</td><td><b>" + str(res['score']) + " / " + str(res['total']) + "</b></td><td>" + str(res['time']) + " ثانية</td></tr>"
        
    correction_html = ""
    for idx, q in enumerate(questions):
        correct_opt = q['options'][q['answer']]
        correction_html += f"""
            <div style="background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 6px; text-align: right;">
                <p style="margin: 0 0 5px 0;"><b>السؤال {idx+1}:</b> {q['question']}</p>
                <p style="margin: 0; color: #16a34a; font-size: 14px;">الإجابة الصحيحة: <b>{correct_opt}</b></p>
            </div>
        """
        
    content = """
        <h2>🏆 النتائج النهائية والإصلاح: """ + test_name + """</h2>
        <table class="ranking">
            <tr><th>المرتبة</th><th>الاسم واللقب</th><th>النقاط</th><th>الوقت المستغرق</th></tr>
            """ + (ranking_html if ranking_html else "<tr><td colspan='4'>لا توجد نتائج مسجلة.</td></tr>") + """
        </table>
        
        <h3 style="margin-top: 30px;">📖 إصلاح الاختبار (Correction):</h3>
        """ + correction_html + """
        
        <br>
        <a href="/" class="btn" style="background: #6b7280;">العودة للرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/teacher_dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    dev_data = load_device_data()
    tests = dev_data["tests"]
    active_data = dev_data["active_test"]
    results = dev_data["results"]
    msg = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'set_active':
            chosen_test = request.form.get('active_test')
            active_data['active'] = chosen_test
            active_data['status'] = 'waiting'
            
            if chosen_test not in results:
                results[chosen_test] = {"participants": [], "scores": [], "status": "waiting"}
            save_device_data(dev_data)
            msg = "تم اختيار الاختبار '" + chosen_test + "' وتفعيل قاعة الانتظار على هذا الجهاز بنجاح!"
            
        elif action == 'start_quiz':
            active_data['status'] = 'started'
            chosen_test = active_data.get('active')
            if chosen_test in results:
                results[chosen_test]['status'] = 'started'
            save_device_data(dev_data)
            msg = "🚀 تم إعطاء إشارة الانطلاق وبدأ الاختبار للتلاميذ!"
            
        elif action == 'finish_quiz':
            active_data['status'] = 'finished'
            chosen_test = active_data.get('active')
            if chosen_test in results:
                results[chosen_test]['status'] = 'finished'
            save_device_data(dev_data)
            msg = "🏁 تم إنهاء الاختبار وعرض النتائج على هواتف الجميع!"
            
        elif action == 'add_test':
            t_name = request.form.get('test_name', '').strip()
            if t_name and t_name not in tests:
                tests[t_name] = []
                save_device_data(dev_data)
                msg = "تم إضافة الاختبار '" + t_name + "' بنجاح!"
        elif action == 'delete_test':
            t_name = request.form.get('test_name')
            if t_name in tests:
                del tests[t_name]
                if active_data.get('active') == t_name:
                    active_data['active'] = ""
                    active_data['status'] = 'waiting'
                if t_name in results:
                    del results[t_name]
                save_device_data(dev_data)
                msg = "تم حذف الاختبار بنجاح!"

    active_test = active_data.get('active', '')
    test_status = active_data.get('status', 'waiting')
    
    current_participants = []
    finished_scores = []
    if active_test and active_test in results:
        current_participants = results[active_test].get("participants", [])
        finished_scores = results[active_test].get("scores", [])
        
    participants_html = ""
    for p in current_participants:
        has_finished = any(s['name'] == p['name'] for s in finished_scores)
        status_text = " ✅ (أنهى الاختبار)" if has_finished else " ⏳ (جاري الإجابة...)"
        participants_html += "<li>👤 <b>" + p['name'] + "</b> " + status_text + "</li>"
        
    teacher_qr_html = ""
    if active_test:
        quiz_url = request.host_url.rstrip('/') + url_for('student_entry')
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=" + quiz_url
        
        control_buttons = ""
        if test_status == 'waiting':
            control_buttons = """
                <form method="POST">
                    <input type="hidden" name="action" value="start_quiz">
                    <button type="submit" style="background: #059669; font-size: 18px; padding: 15px;">🚀 انطلاق الاختبار الآن للتلاميذ</button>
                </form>
            """
        elif test_status == 'started':
            control_buttons = """
                <p style="color: #d97706; font-weight: bold;">⏳ الاختبار جاري...</p>
                <form method="POST">
                    <input type="hidden" name="action" value="finish_quiz">
                    <button type="submit" style="background: #dc2626; font-size: 18px; padding: 15px;">🏁 إنهاء الاختبار وإظهار النتائج للجميع</button>
                </form>
            """
        else:
            control_buttons = """
                <p style="color: #16a34a; font-weight: bold;">🏁 انتهى الاختبار وتم نشر النتائج والإصلاح!</p>
                <a href="/results/""" + urllib.parse.quote(active_test) + """" class="btn" style="background: #2563eb;">🏆 عرض النتائج النهائية والإصلاح</a>
            """

        teacher_qr_html = """
            <div style="margin-top: 20px; padding: 15px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; text-align: center;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #1e3a8a;">📱 QR كود الدخول للتلاميذ (خاص بهذه اللعبة على جهازك):</p>
                <img src=""" + qr_url + """ alt="QR Code" style="width: 150px; height: 150px; border-radius: 6px;">
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #4b5563;">امسح الكود لتسجيل الدخول والانتظار</p>
                
                <hr style="margin: 15px 0;">
                <h3>👥 متابعة التلاميذ وحالة تقدمهم:</h3>
                <ul style="text-align: right; background: #fff; padding: 10px 20px; border-radius: 6px; border: 1px solid #d1d5db;">
                    """ + (participants_html if participants_html else "<li>لا يوجد تلاميذ مسجلون حتى الآن...</li>") + """
                </ul>
                <script>
                    setTimeout(function() {
                        var activeEl = document.activeElement;
                        if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'SELECT' || activeEl.tagName === 'TEXTAREA')) {
                            return;
                        }
                        window.location.reload();
                    }, 3000);
                </script>
                
                <div style="margin-top: 20px;">
                    """ + control_buttons + """
                </div>
            </div>
        """
                
    test_select_options = ""
    for name in tests.keys():
        sel = "selected" if name == active_test else ""
        test_select_options += '<option value="' + name + '" ' + sel + '>' + name + '</option>'
    
    tests_management_html = ""
    for name in tests.keys():
        tests_management_html += """
            <div class="admin-test-row">
                <span><b>""" + name + """</b> (""" + str(len(tests[name])) + """ أسئلة)</span>
                <div style="display: flex; gap: 5px;">
                    <a href="/teacher/edit_test/""" + urllib.parse.quote(name) + """" class="btn" style="padding: 6px 12px; font-size: 14px; margin: 0; background: #2563eb;">⚙️ تعديل/أسئلة</a>
                    <form method="POST" style="margin:0;" onsubmit="return confirm('هل أنت متأكد من حذف هذا الاختبار؟');">
                        <input type="hidden" name="action" value="delete_test">
                        <input type="hidden" name="test_name" value="""" + name + """">
                        <button type="submit" style="padding: 6px 12px; font-size: 13px; margin: 0; background: #dc2626;">حذف</button>
                    </form>
                </div>
            </div>
        """
    
    content = """
        <h2>لوحة تحكم الأستاذ (خاصة بجهازك فقط)</h2>
        <p style="color: green; font-weight: bold;">""" + msg + """</p>
        
        <hr style="margin: 20px 0;">
        <h3>🎯 اختيار وتفعيل الاختبار</h3>
        <form method="POST">
            <input type="hidden" name="action" value="set_active">
            <label>اختر الاختبار الذي تريد تفعيله:</label>
            <select name="active_test">""" + test_select_options + """</select>
            <button type="submit" style="background: #2563eb;">تفعيل هذا الاختبار وفتح قاعة الانتظار</button>
        </form>
        
        """ + teacher_qr_html + """
        
        <hr style="margin: 20px 0;">
        <h3>📚 إدارة الاختبارات الخاصة بك</h3>
        """ + (tests_management_html if tests_management_html else "<p>لا توجد اختبارات مضافة بعد على هذا الجهاز.</p>") + """
        
        <hr style="margin: 20px 0;">
        <h3>إضافة اختبار جديد</h3>
        <form method="POST">
            <input type="hidden" name="action" value="add_test">
            <input type="text" name="test_name" placeholder="اسم الاختبار الجديد" required>
            <button type="submit" style="background: #059669;">إضافة الاختبار</button>
        </form>
        
        <br>
        <a href="/" class="btn" style="background: #6b7280;">الرجوع للرئيسية</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/teacher/edit_test/<test_name>', methods=['GET', 'POST'])
def edit_test(test_name):
    dev_data = load_device_data()
    tests = dev_data["tests"]
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
            save_device_data(dev_data)
            msg = "تم إضافة السؤال بنجاح!"
        elif action == 'delete_question':
            try:
                q_idx = int(request.form.get('q_idx'))
                if 0 <= q_idx < len(tests[test_name]):
                    tests[test_name].pop(q_idx)
                    save_device_data(dev_data)
                    msg = "تم حذف السؤال بنجاح!"
                else:
                    msg = "رقم السؤال غير صحيح!"
            except Exception as e:
                msg = f"خطأ في الحذف: {str(e)}"

    questions = tests[test_name]
    q_list_html = ""
    for idx, q in enumerate(questions):
        correct_opt = q['options'][q['answer']]
        q_list_html += """
            <div class="admin-test-row">
                <div style="text-align: right; flex-grow: 1;">
                    <p style="margin: 0 0 5px 0;"><b>السؤال """ + str(idx+1) + """:</b> """ + q['question'] + """</p>
                    <p style="margin: 0; font-size: 13px; color: #4b5563;">الإجابة الصحيحة: <b>""" + correct_opt + """</b></p>
                </div>
                <form method="POST" style="margin: 0;" onsubmit="return confirm('هل تريد حذف هذا السؤال؟');">
                    <input type="hidden" name="action" value="delete_question">
                    <input type="hidden" name="q_idx" value="""" + str(idx) + """">
                    <button type="submit" style="padding: 6px 10px; font-size: 13px; margin: 0; background: #dc2626;">حذف</button>
                </form>
            </div>
        """

    content = """
        <h2>إدارة اختبار: """ + test_name + """</h2>
        <p style="color: green; font-weight: bold;">""" + msg + """</p>
        
        <h3 style="margin-top: 15px;">أسئلة الاختبار الحالية:</h3>
        """ + (q_list_html if q_list_html else "<p>لا توجد أسئلة في هذا الاختبار بعد.</p>") + """
        
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
    
    





        
     
