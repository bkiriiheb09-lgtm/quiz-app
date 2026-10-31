import os
import json
import time
import uuid
import urllib.parse
import subprocess
import sys

# تثبيت مكتبة supabase أوتوماتيكياً إذا لم تكن موجودة
try:
    from supabase import create_client, Client
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
    from supabase import create_client, Client

from flask import Flask, render_template_string, request, redirect, url_for, session

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

app = Flask(__name__)
app.secret_key = "super_secret_quiz_key_device_isolated_2026"

def get_device_id():
    """الحصول على معرف فريد ومستقل لكل أستاذ/جهاز"""
    if 'device_id' not in session:
        session['device_id'] = str(uuid.uuid4())
    return session['device_id']

def get_teacher_file(t_id):
    safe_id = "".join(c for c in t_id if c.isalnum() or c in ('_', '-'))
    return f"device_{safe_id}.json"

def load_teacher_data(t_id):
    """تحميل بيانات الأستاذ من Supabase أولاً أو الملف المحلي كاحتياط"""
    default_tests = {
        "اختبار رياضيات 1": [
            {"question": "9 * 6 =", "options": ["54", "49", "63"], "answer": 0},
            {"question": "8 * 3 =", "options": ["21", "24", "27"], "answer": 1}
        ]
    }
    
    default_data = {
        "tests": default_tests,
        "active_test": {"active": "", "status": "waiting"},
        "results": {}
    }
    
    if not t_id:
        return default_data
        
    if supabase:
        try:
            res = supabase.table('kv_store').select('value').eq('key', f'teacher_data_{t_id}').execute()
            if res.data and len(res.data) > 0:
                data = res.data[0]['value']
                if not data.get("tests"):
                    data["tests"] = default_tests
                return data
        except Exception as e:
            print("Supabase Load Error:", e)
            
    # احتياطياً من الملف المحلي
    filename = get_teacher_file(t_id)
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not data.get("tests"):
                    data["tests"] = default_tests
                return data
        except:
            return default_data
            
    return default_data

def save_teacher_data(t_id, data):
    """حفظ البيانات بصفة دائمة في Supabase وفي الملف المحلي"""
    if not t_id:
        return
    try:
        filename = get_teacher_file(t_id)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Local Save Error:", e)
        
    if supabase:
        try:
            supabase.table('kv_store').upsert({
                'key': f'teacher_data_{t_id}', 
                'value': data
            }).execute()
        except Exception as e:
            print("Supabase Save Error:", e)

HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>منصة الاختبارات التعليمية</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background-color: #1e3a8a; color: #000; margin: 0; padding: 20px; text-align: center; }
        .card { background: #fff; width: 95%; max-width: 700px; margin: 30px auto; padding: 25px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); text-align: right; box-sizing: border-box; }
        h2, h3, p { color: #000; }
        button, input[type="submit"], a.btn { background: #3b82f6; color: white; border: none; padding: 12px 20px; margin: 10px 0; border-radius: 8px; cursor: pointer; font-size: 16px; text-decoration: none; display: block; width: 100%; box-sizing: border-box; text-align: center; }
        button:hover, a.btn:hover { background: #2563eb; }
        input[type="text"], input[type="password"], select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
        label { display: block; margin: 10px 0; font-size: 16px; cursor: pointer; }
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
                osc.stop(ctx.currentTime + 0.1);
            } catch(e) {}
        }
    </script>
</head>
<body>
    <div class="card">
        {{ content|safe }}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    content = """
    <h2>مرحباً بكم في منصة الاختبارات التفاعلية</h2>
    <p>اختر واجهة الدخول المناسبة لك:</p>
    <a href="/teacher_dashboard" class="btn" style="background: #059669;">👨‍🏫 لوحة تحكم الأستاذ</a>
    <a href="/student_join" class="btn" style="background: #2563eb;">🎓 دخول التلاميذ للاختبار</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/teacher_dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    t_id = get_device_id()
    dev_data = load_teacher_data(t_id)
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
            save_teacher_data(t_id, dev_data)
            msg = "تم اختيار الاختبار '" + chosen_test + "' وتفعيل قاعة الانتظار بنجاح!"
            
        elif action == 'start_quiz':
            active_data['status'] = 'started'
            chosen_test = active_data.get('active')
            if chosen_test in results:
                results[chosen_test]['status'] = 'started'
            save_teacher_data(t_id, dev_data)
            msg = "🚀 تم إعطاء إشارة الانطلاق وبدأ الاختبار للتلاميذ!"
            
        elif action == 'finish_quiz':
            active_data['status'] = 'finished'
            chosen_test = active_data.get('active')
            if chosen_test in results:
                results[chosen_test]['status'] = 'finished'
            save_teacher_data(t_id, dev_data)
            msg = "🏁 تم إنهاء الاختبار وعرض النتائج على هواتف الجميع!"
            
        elif action == 'add_test':
            t_name = request.form.get('test_name', '').strip()
            if t_name and t_name not in tests:
                tests[t_name] = []
                save_teacher_data(t_id, dev_data)
                msg = "تم إضافة الاختبار '" + t_name + "' بنجاح!"

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
        quiz_url = request.host_url.rstrip('/') + url_for('student_entry', teacher=t_id)
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=" + urllib.parse.quote(quiz_url)
        
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
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #1e3a8a;">📱 QR كود الدخول للتلاميذ:</p>
                <img src="{qr_url}" alt="QR Code" style="width: 150px; height: 150px; border-radius: 6px;">
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #4b5563;">امسح الكود لتسجيل الدخول والانتظار</p>
                
                <hr style="margin: 15px 0;">
                <h3>👥 متابعة التلاميذ وحالة تقدمهم:</h3>
                <ul style="text-align: right; background: #fff; padding: 10px 20px; border-radius: 6px; border: 1px solid #d1d5db;">
                    {participants_html if participants_html else "<li>لا يوجد تلاميذ مسجلون حتى الآن...</li>"}
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
                    {control_buttons}
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
                    <form action="/teacher/delete_test/""" + urllib.parse.quote(name) + """" method="POST" style="margin:0;" onsubmit="return confirm('هل أنت متأكد من حذف هذا الاختبار؟');">
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
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/teacher/delete_test/<path:test_name>', methods=['POST'])
def delete_test(test_name):
    t_id = get_device_id()
    dev_data = load_teacher_data(t_id)
    tests = dev_data["tests"]
    active_data = dev_data["active_test"]
    results = dev_data["results"]
    if test_name in tests:
        del tests[test_name]
        if active_data.get('active') == test_name:
            active_data['active'] = ""
            active_data['status'] = 'waiting'
        if test_name in results:
            del results[test_name]
        save_teacher_data(t_id, dev_data)
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/edit_test/<path:test_name>', methods=['GET', 'POST'])
def edit_test(test_name):
    t_id = get_device_id()
    dev_data = load_teacher_data(t_id)

    tests = dev_data.get("tests", {})
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
            
            if test_name not in tests:
                tests[test_name] = []
                
            tests[test_name].append({
                "question": q_text,
                "options": [opt0, opt1, opt2],
                "answer": ans
            })
            
            save_teacher_data(t_id, dev_data)
            msg = "تم إضافة السؤال بنجاح"

    questions = tests.get(test_name, [])
    q_list_html = ""
    for idx, q in enumerate(questions):
        correct_opt = q['options'][q['answer']]
        q_list_html += f"""
            <div class="admin-test-row">
                <div style="text-align: right; flex-grow: 1;">
                    <p style="margin: 0 0 5px 0;"><b>السؤال {idx+1}:</b> {q['question']}</p>
                    <p style="margin: 0; color: #16a34a; font-size: 14px;">الإجابة الصحيحة: <b>{correct_opt}</b></p>
                </div>
            </div>
        """

    content = f"""
        <h2>إدارة اختبار: {test_name}</h2>
        <p style="color: green; font-weight: bold;">{msg}</p>
        
        <h3>أسئلة الاختبار الحالية:</h3>
        {q_list_html if q_list_html else "<p>لا توجد أسئلة في هذا الاختبار بعد.</p>"}
        
        <hr style="margin: 20px 0;">
        <h3>➕ إضافة سؤال جديد لهذا الاختبار</h3>
        <form method="POST" onsubmit="playClickSound()">
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
        <a href="/teacher_dashboard" class="btn" style="background: #6b7280;">← رجوع لوحة التحكم</a>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/student_join', defaults={'teacher': None}, methods=['GET', 'POST'])
@app.route('/student_entry/<teacher>', methods=['GET', 'POST'])
def student_entry(teacher):
    t_id = teacher or session.get('teacher_id')
    if not t_id:
        t_id = get_device_id()
    
    session['teacher_id'] = t_id
    dev_data = load_teacher_data(t_id)
    active_data = dev_data["active_test"]
    test_name = active_data.get('active')
    
    if not test_name:
        content = """
            <h2>تنبيه</h2>
            <p>⏳ لم يقم الأستاذ بتفعيل أي اختبار حتى الآن. الرجاء الانتظار قليلاً...</p>
            <script>
                setTimeout(function() {
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
            session['start_time'] = time.time()
            results = dev_data["results"]
            
            if test_name not in results:
                results[test_name] = {"participants": [], "scores": [], "status": active_data.get('status', 'waiting')}
            
            existing_names = [p['name'] for p in results[test_name].get("participants", [])]
            if name not in existing_names:
                results[test_name]["participants"].append({"name": name, "joined_at": time.time()})
                save_teacher_data(t_id, dev_data)
            
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
        return redirect(url_for('index'))
    
    t_id = session.get('teacher_id')
    dev_data = load_teacher_data(t_id)
    active_data = dev_data["active_test"]
    test_name = active_data.get('active')
    status = active_data.get('status', 'waiting')
    
    if test_name and status == 'started':
        return redirect(url_for('quiz', test_name=test_name))
        
    content = """
        <h2>قاعة الانتظار</h2>
        <p>مرحباً <b>""" + session.get('student_name', '') + """</b></p>
        <p>⏳ في انتظار إشارة الانطلاق من الأستاذ للاختبار (<b>""" + str(test_name) + """</b>)...</p>
        <script>
            setTimeout(function() {
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
        return redirect(url_for('index'))
    
    t_id = session.get('teacher_id')
    dev_data = load_teacher_data(t_id)
    active_data = dev_data["active_test"]
    if active_data.get('status') == 'finished':
        return redirect(url_for('student_waiting_results', test_name=test_name))

    tests = dev_data["tests"]
    if test_name not in tests:
        return redirect(url_for('index'))
    
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
        save_teacher_data(t_id, dev_data)
        return redirect(url_for('student_waiting_results', test_name=test_name))
        
    q_html = ""
    for i, q in enumerate(questions):
        opts = q["options"]
        q_html += f"""
        <div style="background: #f9fafb; padding: 15px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #e5e7eb; text-align: right;">
            <p style="margin: 0 0 10px 0;"><b>السؤال {i+1}: {q['question']}</b></p>
            <label><input type="radio" name="q_{i}" value="0" required> {opts[0]}</label>
            <label><input type="radio" name="q_{i}" value="1" required> {opts[1]}</label>
            <label><input type="radio" name="q_{i}" value="2" required> {opts[2]}</label>
        </div>
        """
        
    content = """
        <h2>اختبار: """ + test_name + """</h2>
        <form method="POST">
            """ + q_html + """
            <button type="submit" style="background: #059669;">إرسال الإجابات النهائية</button>
        </form>
    """
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/student_waiting_results/<test_name>')
def student_waiting_results(test_name):
    if 'student_name' not in session:
        return redirect(url_for('index'))
        
    t_id = session.get('teacher_id')
    dev_data = load_teacher_data(t_id)
    active_data = dev_data["active_test"]
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
    t_id = session.get('teacher_id') or get_device_id()
    dev_data = load_teacher_data(t_id)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)





        
     
