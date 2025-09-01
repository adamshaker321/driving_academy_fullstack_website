import os
import datetime
from datetime import timedelta
import mysql.connector
from mysql.connector import pooling
from flask import Flask,render_template,redirect,request,url_for
from werkzeug.utils import secure_filename
from db_config import get_connection
app = Flask(__name__)




def get_current_period_manual():
    # اليوم اللي عايز تبدأ منه
    first_saturday = datetime.date(2025, 8, 23)  # مثال البداية

    today = datetime.date.today()
    diff_days = (today - first_saturday).days
    weeks_passed = diff_days // 7

    # الأسبوع الحالي
    if weeks_passed % 2 == 0:
        start = first_saturday + timedelta(weeks=weeks_passed)
    else:
        start = first_saturday + timedelta(weeks=weeks_passed + 1)

    end = start + timedelta(days=5)  # الخميس

    # تعديل: لو الأسبوع خلص قبل اليوم الحالي، يبقى الأسبوع الجديد يبقى من السبت بعد السبت التالي
    if today > end:
        # حساب عدد أيام للوصول للسبت التالي للأسبوع القادم
        days_to_next_next_saturday = ((today - start).days // 7 + 2) * 7
        start = first_saturday + timedelta(days=days_to_next_next_saturday)
        end = start + timedelta(days=5)
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM hidden_slots where booking_type=%s",("manual_1",))
        conn.commit()
        cursor.close()
        conn.close()

    return start, end


def get_current_period_manual_2():
    first_saturday = datetime.date(2025, 8, 30)  # التاريخ اللي انت عايزه

    today = datetime.date.today()

    # لو اليوم قبل أول سبت → نبدأ من أول سبت
    if today < first_saturday:
        start = first_saturday
    else:
        diff_days = (today - first_saturday).days
        weeks_passed = diff_days // 7
        if weeks_passed % 2 == 0:
            start = first_saturday + timedelta(weeks=weeks_passed)
        else:
            start = first_saturday + timedelta(weeks=weeks_passed + 1)

    end = start + timedelta(days=5)  # الخميس

    # لو الأسبوع خلص قبل اليوم الحالي
    if today > end:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM hidden_slots where booking_type=%s",("manual_2",))
        conn.commit()
        cursor.close()
        conn.close()

    return start, end

def get_current_period_auto():
    # اليوم اللي عايز تبدأ منه
    first_saturday = datetime.date(2025, 8, 23)  # مثال البداية

    today = datetime.date.today()
    diff_days = (today - first_saturday).days
    weeks_passed = diff_days // 7

    # الأسبوع الحالي
    if weeks_passed % 2 == 0:
        start = first_saturday + timedelta(weeks=weeks_passed)
    else:
        start = first_saturday + timedelta(weeks=weeks_passed + 1)

    end = start + timedelta(days=5)  # الخميس

    # تعديل: لو الأسبوع خلص قبل اليوم الحالي، يبقى الأسبوع الجديد يبقى من السبت بعد السبت التالي
    if today > end:
        # حساب عدد أيام للوصول للسبت التالي للأسبوع القادم
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM hidden_slots where booking_type=%s",("auto_1",))
        conn.commit()
        cursor.close()
        conn.close()
    return start, end

def get_current_period_auto_2():
    first_saturday = datetime.date(2025, 8, 30)  # التاريخ اللي انت عايزه

    today = datetime.date.today()

    # لو اليوم قبل أول سبت → نبدأ من أول سبت
    if today < first_saturday:
        start = first_saturday
    else:
        diff_days = (today - first_saturday).days
        weeks_passed = diff_days // 7
        if weeks_passed % 2 == 0:
            start = first_saturday + timedelta(weeks=weeks_passed)
        else:
            start = first_saturday + timedelta(weeks=weeks_passed + 1)

    end = start + timedelta(days=5)  # الخميس

    # لو الأسبوع خلص قبل اليوم الحالي
    if today > end:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM hidden_slots where booking_type=%s",("auto_2",))
        conn.commit()
        cursor.close()
        conn.close()
    return start, end





@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/manager_page")
def manager_page():
    return render_template("manager_page.html")

@app.route("/offers")
def offers():
    return render_template("offers.html")

@app.route("/register",methods=['GET','POST'])
def register():
    conn=None
    cursor=None
    message=False
    if request.method == 'POST':
        user_id = request.form['client_id']
        user_name = request.form['client_name']
        course = request.form.get('course')
        phone=request.form['phone']
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # نشوف إذا الـ ID موجود
            cursor.execute("SELECT id FROM clients WHERE id = %s", (user_id,))
            existing_client = cursor.fetchone()

            if existing_client:
                message='رمز ال id مستخدم بالفعل'
                # لو موجود يرجعه لنفس الصفحة
                return render_template("register.html",message=message)
            else:
                # لو مش موجود يضيفه
                cursor.execute("INSERT INTO clients (id, `name`, course , phone_number) VALUES (%s, %s, %s, %s)", 
                            (user_id, user_name, course , phone))
                conn.commit()
                return redirect('/home')
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("register.html")
@app.route("/removing", methods=['GET', 'POST'])
def removing():
    conn=None
    cursor=None
    message=False
    if request.method == "POST":
        user_id = request.form['client_id']
        try:
                
            conn = get_connection()
            cursor = conn.cursor()

            # تحقق إذا العميل موجود
            cursor.execute("SELECT id FROM clients WHERE id = %s", (user_id,))
            existing_client = cursor.fetchone()

            if existing_client:
                # حذف العميل
                cursor.execute("DELETE FROM clients WHERE id = %s", (user_id,))
                conn.commit()
                return redirect("/home")
            else:
                # لو العميل مش موجود
                message='العميل لم يكن مسجل بالفعل !'
                return render_template("removing.html",message=message)  # أو صفحة تنبيه
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("removing.html")
@app.route("/booking",methods=['GET','POST'])
def booking():
    start_date_1, end_date_1 = get_current_period_manual()
    start_date_1_2, end_date_1_2 = get_current_period_manual_2()
    start_date_1_auto, end_date_1_auto = get_current_period_auto()
    start_date_1_2_auto, end_date_1_2_auto = get_current_period_auto_2()
    conn=None
    cursor=None
    message=False
    if request.method == 'POST':
        clients_id = request.form["client_id"]
        clients_course = request.form.get('course')
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id ,course FROM clients WHERE id=%s", (clients_id,))
            row = cursor.fetchone()
            
            if row:
                
                if row[1] == 'manual':
                    cursor.execute("select count(*) from manual_sessions_per_client where id=%s",(clients_id,))
                    total_sessions= cursor.fetchone()[0]
                    if total_sessions <5:
                        if start_date_1<start_date_1_2:
                            return redirect("/manual_booking")
                        else:
                            return redirect("/manual_booking_2")
                    else:
                        message='⚠️ انهيت حصصك'
                
                elif row[1] == 'automatic':
                    cursor.execute("select count(*) from automatic_sessions_per_client where id=%s",(clients_id,))
                    total_sessions= cursor.fetchone()[0]
                    if total_sessions <5:
                        if start_date_1_auto<start_date_1_2_auto:
                            return redirect("/automatic_booking")
                        else:
                            return redirect("/automatic_booking_2")
                    else:
                        message='⚠️ انهيت حصصك'
                    
                elif row[1] =='mix':
                    cursor.execute("select count(*) from manual_sessions_per_client where id=%s",(clients_id,))
                    total_manual_sessions= cursor.fetchone()[0]
                    cursor.execute("select count(*) from automatic_sessions_per_client where id=%s",(clients_id,))
                    total_automatic_sessions= cursor.fetchone()[0]
                    if total_manual_sessions <3 and total_automatic_sessions ==0:
                        if start_date_1<start_date_1_2:
                            return redirect("/manual_booking")
                        else:
                            return redirect("/manual_booking_2")
                    elif total_manual_sessions>=3 and total_automatic_sessions <3:
                        if start_date_1_auto<start_date_1_2_auto:
                            return redirect("/automatic_booking")
                        else:
                            return redirect("/automatic_booking_2")
                    else:
                        message='⚠️ انهيت حصصك'

            else:

                message='⚠️ ادخل رمز صحيح '
                return render_template("booking.html",message=message)
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        
    return render_template("booking.html",message=message)












@app.route("/manual_booking", methods=["GET", "POST"])
def manual_booking():
    conn = None
    cursor = None
    try:        
        conn = get_connection()
        cursor = conn.cursor()
        start_date, end_date = get_current_period_manual()
        today = datetime.date.today()

        if today > end_date:
            cursor.execute("DELETE FROM client_manual_sessions")
            conn.commit()

        days_list = []
        arabic_days = ["السبت","الأحد","الاثنين","الثلاثاء","الأربعاء","الخميس"]
        for i, day_name in enumerate(arabic_days):
            current_date = start_date + timedelta(days=i)
            is_past = current_date < today
            disable_cancel = 0 <= (current_date - today).days < 1
            days_list.append({
                "name": day_name,
                "date": current_date.strftime("%d/%m"),
                "full_date": current_date,
                "is_past": is_past,
                "disable_cancel": disable_cancel
            })

        message = None
        already_booked_message = None
        booked_confirmed_message = None
        more_than_two_sessions = None

        if request.method == 'POST':
            client_name = request.form['name']
            client_id = request.form['password']
            session_date = request.form['session_day_hour']
            phone_number = request.form['phone']

            # ✅ لو الباسورد السري اتكتب → نخفي الزرار من الجدول
            if client_id == "4818959_capashrafess_3916801":
                slot_index = request.form.get("slot_index")
                cursor.execute("INSERT INTO hidden_slots (session_day, slot_index ,booking_type) VALUES (%s, %s, %s)", (f"{session_date}_{slot_index}","manual_1","manual_1"))
                conn.commit()
                booked_confirmed_message = "✅ تم اخفاء هذا المكان فقط."
            else:
                MAX_CAPACITY = 3
                cursor.execute("""
                    SELECT COUNT(*) FROM client_manual_sessions WHERE session_day = %s
                """, (session_date,))
                current_bookings = cursor.fetchone()[0]

                if current_bookings >= MAX_CAPACITY:
                    message = "⚠ المعاد ده اتحجز بالكامل."
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM client_manual_sessions WHERE id = %s AND session_day = %s
                    """, (client_id, session_date))
                    already_booked = cursor.fetchone()[0] > 0

                    if already_booked:
                        already_booked_message = "⚠ انت حجزت المعاد ده قبل كده."
                    else:
                        cursor.execute("SELECT id,course FROM clients WHERE id = %s", (client_id,))
                        client_exists = cursor.fetchone()
                        if client_exists and client_exists[1] in ['mix', 'manual']:
                            cursor.execute("SELECT count(*) FROM client_manual_sessions where id = %s", (client_id,))
                            total_sessions_per_week = cursor.fetchone()[0]
                            if total_sessions_per_week < 2:
                                cursor.execute("""
                                    INSERT INTO client_manual_sessions (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                                conn.commit()

                                cursor.execute("""
                                    INSERT INTO manual_sessions_per_client (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                                conn.commit()

                                booked_confirmed_message = "✅ تم الحجز بنجاح."
                            else:
                                more_than_two_sessions = "⚠️ وصلت الحد الاقصى هذا الاسبوع. "
                        else:
                            message = "⚠ ادخل كود صحيح"

        cursor.execute("SELECT session_day, client_name FROM client_manual_sessions")
        rows = cursor.fetchall()
        booked_slots_names = {}
        for session, name in rows:
            if session not in booked_slots_names:
                booked_slots_names[session] = []
            booked_slots_names[session].append(name)
        cursor.execute("SELECT session_day, slot_index FROM hidden_slots where booking_type=%s",("manual_1",))
        hidden_slots= cursor.fetchall()
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template(
        "manual_booking.html",
        booked_slots_names=booked_slots_names,
        already_booked_message=already_booked_message,
        booked_confirmed_message=booked_confirmed_message,
        more_than_two_sessions=more_than_two_sessions,
        message=message,
        start_date=start_date,
        end_date=end_date,
        days_list=days_list,
        today=today,
        hidden_slots=hidden_slots   # ✅ نبعتها للـ Frontend
    )



@app.route("/manual_booking_2", methods=["GET", "POST"])
def manual_booking_2():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        start_date, end_date = get_current_period_manual_2()
        today = datetime.date.today()

        if today > end_date:
            cursor.execute("DELETE FROM client_manual_sessions_2")
            conn.commit()

        message = None  
        already_booked_message = None
        booked_confirmed_message = None
        more_than_two_sessions = None

        if request.method == 'POST':
            client_name = request.form['name']                
            client_id = request.form['password']              
            session_date = request.form['session_day_hour']   
            phone_number = request.form['phone']   
            slot_index = request.form.get("slot_index")  # 👈 رقم الزرار اللي اتضغط

            if client_id == "4818959_capashrafess_3916801":
                cursor.execute("INSERT INTO hidden_slots (session_day, slot_index, booking_type) VALUES (%s, %s, %s)", (f"{session_date}_{slot_index}","manual_2","manual_2"))
                conn.commit()
                booked_confirmed_message = "✅ تم اخفاء زرار الحجز لهذا المكان فقط."
            else:
                MAX_CAPACITY = 3  
                cursor.execute("""
                    SELECT COUNT(*) FROM client_manual_sessions_2
                    WHERE session_day = %s
                """, (session_date,))
                current_bookings = cursor.fetchone()[0]

                if current_bookings >= MAX_CAPACITY:
                    message = "⚠ المعاد ده اتحجز بالكامل."
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM client_manual_sessions_2
                        WHERE id = %s AND session_day = %s
                    """, (client_id, session_date))
                    already_booked = cursor.fetchone()[0] > 0

                    if already_booked:
                        already_booked_message = "⚠ انت حجزت المعاد ده قبل كده."
                    else:
                        cursor.execute("SELECT id,course FROM clients WHERE id = %s", (client_id,))
                        client_exists = cursor.fetchone()

                        if client_exists and client_exists[1] in ['mix', 'manual']:
                            cursor.execute("SELECT count(*) FROM client_manual_sessions_2 where id = %s", (client_id,))
                            total_sessions_per_week = cursor.fetchone()[0]
                            if total_sessions_per_week < 2:
                                cursor.execute("""
                                    INSERT INTO client_manual_sessions_2 (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                                conn.commit()
                                cursor.execute("""
                                    INSERT INTO manual_sessions_per_client (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                                conn.commit()
                                booked_confirmed_message = "✅ تم الحجز بنجاح."
                            else:
                                more_than_two_sessions = "⚠️ وصلت الحد الاقصى هذا الاسبوع. "
                        else:
                            message = "⚠ ادخل كود صحيح"

        cursor.execute("SELECT session_day, client_name FROM client_manual_sessions_2")
        rows = cursor.fetchall()
        booked_slots_names = {}
        for session, name in rows:
            if session not in booked_slots_names:
                booked_slots_names[session] = []
            booked_slots_names[session].append(name)

        # حساب تواريخ الأيام
        week_days = []
        arabic_days = ["السبت","الأحد","الاثنين","الثلاثاء","الأربعاء","الخميس"]
        for i, day_name in enumerate(arabic_days):
            current_date = start_date + timedelta(days=i)
            is_past = current_date < today
            disable_cancel = 0 <= (current_date - today).days < 1
            week_days.append({
                "name": day_name,
                "date": current_date,
                "is_past": is_past,
                "disable_cancel": disable_cancel
            })
        cursor.execute("SELECT session_day, slot_index FROM hidden_slots where booking_type=%s",("manual_2",))
        hidden_slots= cursor.fetchall()
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template(
        "manual_booking_2.html",
        booked_slots_names=booked_slots_names,
        already_booked_message=already_booked_message,
        booked_confirmed_message=booked_confirmed_message,
        more_than_two_sessions=more_than_two_sessions,    
        message=message,
        start_date=start_date,
        end_date=end_date,
        week_days=week_days,
        today=today,
        hidden_slots= hidden_slots  # ✅ نبعتها للـ Frontend
    )


@app.route("/automatic_booking", methods=["GET", "POST"])
def automatic_booking():
    conn = None
    cursor = None
    try:

        conn = get_connection()
        cursor = conn.cursor()
        start_date, end_date = get_current_period_auto()
        today = datetime.date.today()

        # لو اليوم بعد نهاية الفترة → نمسح الحجوزات
        if today > end_date:
            cursor.execute("DELETE FROM client_automatic_sessions")
            conn.commit()

        message = None
        already_booked_message = None
        booked_confirmed_message = None
        more_than_two_sessions = None

        # تجهيز الأيام مع التواريخ + فلاغ منع الإلغاء
        days_of_week = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        days_with_dates = []
        for i, day in enumerate(days_of_week):
            day_date = start_date + timedelta(days=i)
            # لو باقي يوم أو أقل → ممنوع الإلغاء
            disable_cancel = (day_date - today).days < 1
            days_with_dates.append({"name": day, "date": day_date, "disable_cancel": disable_cancel})

        if request.method == 'POST':
            client_name = request.form['name']
            client_id = request.form['password']
            session_date = request.form['session_day_hour']
            phone_number = request.form['phone']
            slot_index = request.form.get("slot_index")  # 👈 رقم الزرار اللي اتضغط

            if client_id == "4818959_capashrafess_3916801":
                cursor.execute("INSERT INTO hidden_slots (session_day, slot_index, booking_type) VALUES (%s, %s, %s)", (f"{session_date}_{slot_index}","auto_1","auto_1"))
                conn.commit()
                booked_confirmed_message = "✅ تم اخفاء زرار الحجز لهذا المكان فقط."
            else:

                MAX_CAPACITY = 2  # السعة القصوى لكل slot

                cursor.execute("""
                    SELECT COUNT(*) FROM client_automatic_sessions
                    WHERE session_day = %s
                """, (session_date,))
                current_bookings = cursor.fetchone()[0]

                if current_bookings >= MAX_CAPACITY:
                    message = "⚠ المعاد ده اتحجز بالكامل."
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM client_automatic_sessions
                        WHERE id = %s AND session_day = %s
                    """, (client_id, session_date))
                    already_booked = cursor.fetchone()[0] > 0

                    if already_booked:
                        already_booked_message = "⚠ انت حجزت المعاد ده قبل كده."
                    else:
                        cursor.execute("SELECT id,course FROM clients WHERE id = %s", (client_id,))
                        client_exists = cursor.fetchone()

                        if client_exists and client_exists[1] in ['mix', 'automatic']:
                            cursor.execute("SELECT count(*) FROM client_automatic_sessions where id = %s", (client_id,))
                            total_sessions_per_week = cursor.fetchone()[0]
                            if total_sessions_per_week < 2:
                                cursor.execute("""
                                    INSERT INTO client_automatic_sessions (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                                conn.commit()

                                cursor.execute("""
                                    INSERT INTO automatic_sessions_per_client (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                                conn.commit()

                                booked_confirmed_message = "✅ تم الحجز بنجاح."
                            else:
                                more_than_two_sessions = "⚠️ وصلت الحد الاقصى هذا الاسبوع. "
                        else:
                            message = "⚠ ادخل كود صحيح"

        # جمع أسماء المحجوزين لكل slot
        cursor.execute("SELECT session_day, client_name FROM client_automatic_sessions")
        rows = cursor.fetchall()
        booked_slots_names = {}
        for session, name in rows:
            if session not in booked_slots_names:
                booked_slots_names[session] = []
            booked_slots_names[session].append(name)

        cursor.execute("SELECT session_day, slot_index FROM hidden_slots where booking_type=%s",("auto_1",))
        hidden_slots= cursor.fetchall()

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        "automatic_booking.html",
        booked_slots_names=booked_slots_names,
        already_booked_message=already_booked_message,
        booked_confirmed_message=booked_confirmed_message,
        more_than_two_sessions=more_than_two_sessions,
        message=message,
        start_date=start_date,
        end_date=end_date,
        days_with_dates=days_with_dates,
        today=today,
        hidden_slots=hidden_slots  # ✅ نبعتها للـ Frontend
    )

@app.route("/automatic_booking_2", methods=['GET', 'POST'])
def automatic_booking_2():
    conn = None
    cursor = None
    try:

        conn = get_connection()
        cursor = conn.cursor()
        start_date, end_date = get_current_period_auto_2()
        today = datetime.date.today()

        if today > end_date:
            cursor.execute("DELETE FROM client_automatic_sessions_2")
            conn.commit()

        message = None  
        already_booked_message = None
        booked_confirmed_message = None
        more_than_two_sessions = None

        # الأيام + التواريخ + فلاغ منع الإلغاء لو باقي يوم أو أقل
        days_of_week = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        days_with_dates = []
        for i, day in enumerate(days_of_week):
            day_date = start_date + timedelta(days=i)
            disable_cancel = (day_date - today).days < 1  # لو باقي يوم أو أقل → ممنوع الإلغاء
            days_with_dates.append({"name": day, "date": day_date, "disable_cancel": disable_cancel, "date_str": day_date.strftime("%Y-%m-%d")})

        if request.method == 'POST':
            client_name = request.form['name']
            client_id = request.form['password']
            session_date = request.form['session_day_hour']
            phone_number = request.form['phone']
            slot_index = request.form.get("slot_index")  # 👈 رقم الزرار اللي اتضغط

            if client_id == "4818959_capashrafess_3916801":
                cursor.execute("INSERT INTO hidden_slots (session_day, slot_index, booking_type) VALUES (%s, %s, %s)", (f"{session_date}_{slot_index}","auto_2","auto_2"))
                conn.commit()
                booked_confirmed_message = "✅ تم اخفاء زرار الحجز لهذا المكان فقط."
            else:
                MAX_CAPACITY = 2  

                cursor.execute("""
                    SELECT COUNT(*) FROM client_automatic_sessions_2
                    WHERE session_day = %s
                """, (session_date,))
                current_bookings = cursor.fetchone()[0]

                if current_bookings >= MAX_CAPACITY:
                    message = "⚠ المعاد ده اتحجز بالكامل."
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM client_automatic_sessions_2
                        WHERE id = %s AND session_day = %s
                    """, (client_id, session_date))
                    already_booked = cursor.fetchone()[0] > 0

                    if already_booked:
                        already_booked_message = "⚠ انت حجزت المعاد ده قبل كده."
                    else:
                        cursor.execute("SELECT id ,course FROM clients WHERE id = %s", (client_id,))
                        client_exists = cursor.fetchone()

                        if client_exists and client_exists[1] in ['mix', 'automatic']:
                            cursor.execute("SELECT count(*) FROM client_automatic_sessions_2 where id = %s", (client_id,))
                            total_sessions_per_week = cursor.fetchone()[0]  
                            if total_sessions_per_week < 2:
                                cursor.execute("""
                                    INSERT INTO client_automatic_sessions_2 (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                                conn.commit()

                                cursor.execute("""
                                    INSERT INTO automatic_sessions_per_client (id, client_name, phone, session_day, book_date)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))     
                                conn.commit()

                                booked_confirmed_message = "✅ تم الحجز بنجاح."
                            else:
                                more_than_two_sessions = "⚠️ وصلت الحد الاقصى هذا الاسبوع. "
                        else:
                            message = "⚠ ادخل كود صحيح"

        cursor.execute("SELECT session_day, client_name FROM client_automatic_sessions_2")
        rows = cursor.fetchall()
        booked_slots_names = {}
        for session, name in rows:
            if session not in booked_slots_names:
                booked_slots_names[session] = []
            booked_slots_names[session].append(name)
        cursor.execute("SELECT session_day, slot_index FROM hidden_slots where booking_type=%s",("auto_2",))
        hidden_slots= cursor.fetchall()

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        "automatic_booking_2.html",
        booked_slots_names=booked_slots_names,
        already_booked_message=already_booked_message,
        booked_confirmed_message=booked_confirmed_message,
        more_than_two_sessions=more_than_two_sessions,
        message=message,
        start_date=start_date,
        end_date=end_date,
        days_with_dates=days_with_dates,
        today=today,
        hidden_slots=hidden_slots   # ✅ نبعتها للـ Frontend
    )

@app.route("/cancel_booking", methods=["POST"])
def cancel_booking():
    cancel_id = request.form.get("cancel_id")
    session_day_hour = request.form.get("session_day_hour")
    session_type = request.form.get("session_type", "manual")  # نوع الحجز
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if session_type == "manual":
            table_name = "client_manual_sessions"
        else:
            table_name = "client_automatic_sessions"

        cursor.execute(
            f"SELECT * FROM {table_name} WHERE id = %s AND session_day = %s",
            (cancel_id, session_day_hour)
        )
        booking = cursor.fetchone()

        if booking:
            cursor.execute(
                f"DELETE FROM {table_name} WHERE id = %s AND session_day = %s",
                (cancel_id, session_day_hour)
            )
            conn.commit()
            cursor.execute(f"DELETE FROM {session_type}_sessions_per_client WHERE id = %s AND session_day = %s", (cancel_id, session_day_hour))
            conn.commit()
            cursor.close()
            conn.close()
        
            # هنا نعمل redirect عشان نستفيد من نفس اللوجيك اللي بيجهز البيانات
            return redirect(f"/{session_type}_booking")
        else:
            cursor.close()
            conn.close()
            return redirect(f"/{session_type}_booking")

    except Exception as e:
        return f"An error occurred: {e}"

@app.route("/cancel_booking_2", methods=["POST"])
def cancel_booking_2():
    cancel_id = request.form.get("cancel_id")
    session_day_hour = request.form.get("session_day_hour")
    session_type = request.form.get("session_type", "manual")  # نوع الحجز

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if session_type == "manual":
            table_name = "client_manual_sessions_2"
        else:
            table_name = "client_automatic_sessions_2"

        cursor.execute(
            f"SELECT * FROM {table_name} WHERE id = %s AND session_day = %s",
            (cancel_id, session_day_hour)
        )
        booking = cursor.fetchone()

        if booking:
            cursor.execute(
                f"DELETE FROM {table_name} WHERE id = %s AND session_day = %s",
                (cancel_id, session_day_hour)
            )
            conn.commit()
            cursor.execute(f"DELETE FROM {session_type}_sessions_per_client WHERE id = %s AND session_day = %s", (cancel_id, session_day_hour))

            conn.commit()
            cursor.close()
            conn.close()

            # هنا نعمل redirect عشان نستفيد من نفس اللوجيك اللي بيجهز البيانات
            return redirect(f"/{session_type}_booking_2")
        else:
            cursor.close()
            conn.close()
            return redirect(f"/{session_type}_booking_2")
    except Exception as e:
        return f"An error occurred: {e}"
@app.route("/clients_data")
def clients_data():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # بيانات المانيوال
        cursor.execute("SELECT id, name, course , phone_number FROM clients WHERE course = 'manual'")
        data_manual = cursor.fetchall()

        # بيانات الأوتوماتيك
        cursor.execute("SELECT id, name, course , phone_number FROM clients WHERE course = 'automatic'")
        data_auto = cursor.fetchall()
        
        # بيانات الميكس
        cursor.execute("SELECT id, name, course , phone_number FROM clients WHERE course = 'mix'")
        data_mix = cursor.fetchall()

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template("clients_data.html", data_manual=data_manual, data_auto=data_auto , data_mix=data_mix)
UPLOAD_FOLDER = os.path.join("static", "files")
@app.route("/add_review",methods=["GET","POST"])
def add_review():
    conn = None
    cursor = None

    if request.method == "POST":
        file = request.files['file']
        caption = request.form.get('description', '')
        

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # حفظ الملف في فولدر static
            file.save(file_path)

            # تخزين البيانات في قاعدة البيانات
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO file_reviews (file_name, file_path, caption, publish_date)
                    VALUES ( %s, %s, %s,%s)
                """, ( filename, f"static/files/{filename}", caption,datetime.datetime.today()))
                conn.commit()

                return redirect(url_for("manager_page"))
            except Exception as e:
                return f"An error occurred: {e}"
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
    return render_template("add_review.html")
@app.route("/reviews")
def reviews():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM file_reviews ORDER BY publish_date DESC")
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("reviews.html", reviews=reviews)
@app.route("/remove_review",methods=["GET","POST"])
def remove_review():
    conn = None
    cursor = None
    invalid_message = None
    if request.method == "POST":
        file_id = request.form['file_number']
        try:
            conn = get_connection()
            cursor = conn.cursor()

            #validation
            cursor.execute("SELECT id , file_path FROM file_reviews WHERE id = %s", (file_id,))
            file_data = cursor.fetchone()

            if file_data:
                cursor.execute("DELETE FROM file_reviews WHERE id = %s", (file_id,))
                conn.commit()
                file_path = file_data[1]
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                return redirect(url_for("manager_page"))
            else:
                invalid_message = "⚠️ رقم الملف غير صحيح !"
        except Exception as e:
            return f"An error occurred: {e}"
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("remove_review.html", invalid_message=invalid_message)    

@app.route("/login",methods=["GET","POST"])
def login():
    conn = None
    cursor = None
    message = None
    if request.method == 'POST':
        user_id = request.form['client_id']
        user_name = request.form['client_name']
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # نشوف إذا الـ Admin موجود
            cursor.execute(
                "SELECT admin_id, admin_name FROM admins WHERE admin_id = %s AND admin_name = %s",
                (user_id, user_name)
            )
            existing_admin = cursor.fetchone()

            if existing_admin:
                return redirect("/dashboard")   

            # check if the user is the manager
            
            cursor.execute("SELECT manager_id,manager_name FROM managers WHERE manager_id = %s AND manager_name = %s", (user_id, user_name))
        
            existing_manager = cursor.fetchone()
        
            if existing_manager:
                return redirect("/manager_page")



            # check if the user is a client
            cursor.execute("SELECT id, name, course FROM clients WHERE id = %s AND name = %s", (user_id, user_name))
            existing_client = cursor.fetchone()

            if existing_client:
                course = existing_client[2]

                if course == 'manual':
                    cursor.execute("SELECT client_name, id, phone, session_day FROM manual_sessions_per_client WHERE id = %s", (user_id,))
                    sessions_manual = cursor.fetchall()
                    return render_template("client_page.html", sessions_manual=sessions_manual)

                elif course == 'automatic':
                    cursor.execute("SELECT client_name, id, phone, session_day FROM automatic_sessions_per_client WHERE id = %s", (user_id,))
                    sessions_automatic = cursor.fetchall()
                    return render_template("client_page.html", sessions_automatic=sessions_automatic)

                elif course == 'mix':
                    cursor.execute("SELECT client_name, id, phone, session_day FROM manual_sessions_per_client WHERE id = %s", (user_id,))
                    sessions_manual = cursor.fetchall()
                    cursor.execute("SELECT client_name, id, phone, session_day FROM automatic_sessions_per_client WHERE id = %s", (user_id,))
                    sessions_automatic = cursor.fetchall()
                    return render_template("client_page.html", sessions_manual=sessions_manual, sessions_automatic=sessions_automatic)

            else:
                message = 'ادخل بيانات صحيحة !'
                return render_template("login.html", message=message)
        except Exception as e:
            return f"An error occurred: {e}"
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("login.html")


@app.route("/add_admin", methods=["GET", "POST"])
def add_admin():
    conn = None
    cursor = None
    message = None      
    if request.method == 'POST':
        admin_id = request.form['adm_id']
        admin_name = request.form['adm_name']
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # نشوف إذا الـ Admin موجود
            cursor.execute("SELECT admin_id FROM admins WHERE admin_id = %s", (admin_id,))
            existing_admin = cursor.fetchone()      
            if existing_admin:
                message = 'هذا الكود مستخدم بالفعل'
                return render_template("add_admin.html", message=message)
            else:
                # لو مش موجود يضيفه
                cursor.execute("INSERT INTO admins (admin_id, admin_name) VALUES (%s, %s)", 
                            (admin_id, admin_name))
                conn.commit()
                return redirect('/manager_page')
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("add_admin.html", message=message)

@app.route("/remove_admin", methods=["GET", "POST"])    
def remove_admin():
    conn = None
    cursor = None
    message = None
    if request.method == 'POST':
        admin_id = request.form['adm_id']
        try:

            conn = get_connection()
            cursor = conn.cursor()
            # تحقق إذا الـ Admin موجود
            cursor.execute("SELECT admin_id FROM admins WHERE admin_id = %s", (admin_id,))
            existing_admin = cursor.fetchone()
            if existing_admin:
                # حذف الـ Admin
                cursor.execute("DELETE FROM admins WHERE admin_id = %s", (admin_id,))
                conn.commit()
                return redirect("/manager_page")
            else:
                message = 'هذا الكود غير موجود !'
                return render_template("remove_admin.html", message=message)
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()        
    return render_template("remove_admin.html", message=message)

@app.route("/admins_data")
def admins_data():
    try:
        conn = None
        cursor = None
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT admin_name, admin_id FROM admins")
        data = cursor.fetchall()
    except Exception as e:
        return f"An error occurred: {e}"
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template("admins_data.html", data=data)


@app.route("/client_page")
def client_page():
    return render_template("client_page.html")    
if __name__=="__main__":
    app.run(debug=True)
    