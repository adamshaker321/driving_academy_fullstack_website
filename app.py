import os
import datetime
from datetime import timedelta
import mysql.connector
from flask import Flask,render_template,redirect,request,url_for
from werkzeug.utils import secure_filename
from db_config import get_connection
app = Flask(__name__)



def reset_week(table_number):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # آخر أسبوع مسجّل للجدول
    cursor.execute("SELECT * FROM weeks WHERE table_number=%s ORDER BY end_date DESC LIMIT 1", (table_number,))
    last_week = cursor.fetchone()

    today = datetime.today().date()

    if not last_week:
        new_start = today
        new_end = today + timedelta(days=5)  
        cursor.execute(
            "INSERT INTO weeks (table_number, start_date, end_date) VALUES (%s, %s, %s)",
            (table_number, new_start, new_end)
        )
        conn.commit()
        conn.close()
        return

    if today > last_week['end_date']:
        # بداية الأسبوع الجديد بعد آخر نهاية
        new_start = last_week['end_date'] + timedelta(days=1)
        new_end = new_start + timedelta(days=5)  # أسبوع 6 أيام
        
        # امسح الحجوزات القديمة للجدول ده
        cursor.execute("DELETE FROM client_manual_sessions WHERE table_number=%s", (table_number,))
        cursor.execute("DELETE FROM client_automatic_sessions WHERE table_number=%s", (table_number,))

        # سجل الأسبوع الجديد
        cursor.execute(
            "INSERT INTO weeks (table_number, start_date, end_date) VALUES (%s,%s,%s)",
            (table_number, new_start, new_end)
        )
        conn.commit()

    conn.close()

@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/admin",methods=['GET','POST'])
def admin():
    message=False
    if request.method=='POST':
        admin_id=request.form['Admin_id']
        admin_name=request.form['Admin_name']
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("select admin_id ,admin_name from admins")
        rows=cursor.fetchall()
        for row in rows:
            if admin_id ==row[0] and admin_name == row[1]:
                return redirect("/dashboard")
            else:                
                message='⚠️ ادخل رمز ومستخدم صحيحين '
                return render_template("admin.html",message=message)

        cursor.close()
        conn.close()    
    return render_template("admin.html")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
@app.route("/offers")
def offers():
    return render_template("offers.html")
@app.route("/register",methods=['GET','POST'])
def register():
    message=False
    if request.method == 'POST':
        user_id = request.form['client_id']
        user_name = request.form['client_name']
        course = request.form.get('course')
        phone=request.form['phone']
        conn = get_connection()
        cursor = conn.cursor()

        # نشوف إذا الـ ID موجود
        cursor.execute("SELECT id FROM clients WHERE id = %s", (user_id,))
        existing_client = cursor.fetchone()

        if existing_client:
            message='رمز ال id مستخدم بالفعل'
            # لو موجود يرجعه لنفس الصفحة
            cursor.close()
            conn.close()
            return render_template("register.html",message=message)
        else:
            # لو مش موجود يضيفه
            cursor.execute("INSERT INTO clients (id, `name`, course , phone_number) VALUES (%s, %s, %s, %s)", 
                           (user_id, user_name, course , phone))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/dashboard')

    return render_template("register.html")
@app.route("/removing", methods=['GET', 'POST'])
def removing():
    message=False
    if request.method == "POST":
        user_id = request.form['client_id']

        conn = get_connection()
        cursor = conn.cursor()

        # تحقق إذا العميل موجود
        cursor.execute("SELECT id FROM clients WHERE id = %s", (user_id,))
        existing_client = cursor.fetchone()

        if existing_client:
            # حذف العميل
            cursor.execute("DELETE FROM client_manual_sessions WHERE id = %s", (user_id,))
            cursor.execute("DELETE FROM client_automatic_sessions WHERE id = %s", (user_id,))
            cursor.execute("DELETE FROM clients WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect("/dashboard")
        else:
            # لو العميل مش موجود
            message='العميل لم يكن مسجل بالفعل !'
            cursor.close()
            conn.close()
            return render_template("removing.html",message=message)  # أو صفحة تنبيه

    return render_template("removing.html")
@app.route("/booking",methods=['GET','POST'])
def booking():
    message=False
    if request.method == 'POST':
        clients_id = request.form["client_id"]
        clients_course = request.form.get('course')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id ,course FROM clients WHERE id=%s", (clients_id,))
        row = cursor.fetchone()
        
        if row:
            cursor.close()
            conn.close()
            
            if row[1] == 'manual':
                return redirect("/manual_booking")
            elif row[1] == 'automatic':
                return redirect("/automatic_booking")
            elif row[1] =='mix':
                if clients_course=='manual':
                    return redirect("/manual_booking")
                elif clients_course=='automatic':
                    return redirect("/automatic_booking")
        else:

            cursor.close()
            conn.close()
            message='⚠️ ادخل رمز صحيح '
            return render_template("booking.html",message=message)


        
    return render_template("booking.html",message=message)












@app.route("/manual_booking", methods=["GET", "POST"])
def manual_booking():
    conn = get_connection()
    cursor = conn.cursor()

    message = None  
    already_booked_message = None
    booked_confirmed_message = None
    more_than_two_sessions = None

    if request.method == 'POST':
        client_name = request.form['name']                
        client_id = request.form['password']              
        session_date = request.form['session_day_hour']   
        phone_number = request.form['phone']              

        # السعة القصوى لكل slot
        MAX_CAPACITY = 3  

        # عدد الحجوزات الحالية في نفس slot
        cursor.execute("""
            SELECT COUNT(*) FROM client_manual_sessions
            WHERE session_day = %s
        """, (session_date,))
        current_bookings = cursor.fetchone()[0]

        if current_bookings >= MAX_CAPACITY:
            message = "⚠ المعاد ده اتحجز بالكامل."
        else:
            # التأكد إن العميل مايحجزش نفس slot مرتين
            cursor.execute("""
                SELECT COUNT(*) FROM client_manual_sessions
                WHERE id = %s AND session_day = %s
            """, (client_id, session_date))
            already_booked = cursor.fetchone()[0] > 0

            if already_booked:
                already_booked_message = "⚠ انت حجزت المعاد ده قبل كده."
            else:
                # التأكد إن العميل موجود
                cursor.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
                client_exists = cursor.fetchone()

                if client_exists:
                    cursor.execute("SELECT count(*) FROM client_manual_sessions where id = %s", (client_id,))
                    total_sessions_per_week= cursor.fetchone()[0]
                    if total_sessions_per_week < 2:
                        cursor.execute("""
                            INSERT INTO client_manual_sessions (id, client_name, phone, session_day, book_date)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                        conn.commit()
                        booked_confirmed_message = "✅ تم الحجز بنجاح."
                    else:
                        more_than_two_sessions = "⚠️ لقد قمت بحجز أكثر من معادين في هذا الأسبوع. "
                        
                else:
                    message = "⚠ العميل غير موجود."

    # جلب أسماء العملاء لكل slot
    cursor.execute("SELECT session_day, client_name FROM client_manual_sessions")
    rows = cursor.fetchall()
    booked_slots_names = {}
    for session, name in rows:
        if session not in booked_slots_names:
            booked_slots_names[session] = []
        booked_slots_names[session].append(name)

    cursor.close()
    conn.close()

    return render_template(
        "manual_booking.html",
        booked_slots_names=booked_slots_names,
        already_booked_message=already_booked_message if 'already_booked_message' in locals() else None,
        booked_confirmed_message=booked_confirmed_message ,
        more_than_two_sessions=more_than_two_sessions ,    
        message=message
    )





@app.route("/automatic_booking", methods=["GET", "POST"])
def automatic_booking():
    conn = get_connection()
    cursor = conn.cursor()

    message = None  
    already_booked_message = None
    booked_confirmed_message = None
    more_than_two_sessions = None

    if request.method == 'POST':
        client_name = request.form['name']                
        client_id = request.form['password']              
        session_date = request.form['session_day_hour']   
        phone_number = request.form['phone']              

        MAX_CAPACITY = 2  # السعة القصوى لكل slot

        # عدد الحجوزات الحالية في نفس slot
        cursor.execute("""
            SELECT COUNT(*) FROM client_automatic_sessions
            WHERE session_day = %s
        """, (session_date,))
        current_bookings = cursor.fetchone()[0]

        if current_bookings >= MAX_CAPACITY:
            message = "⚠ المعاد ده اتحجز بالكامل."
        else:
            # التأكد إن العميل مايحجزش نفس slot مرتين
            cursor.execute("""
                SELECT COUNT(*) FROM client_automatic_sessions
                WHERE id = %s AND session_day = %s
            """, (client_id, session_date))
            already_booked = cursor.fetchone()[0] > 0

            if already_booked:
                already_booked_message = "⚠ انت حجزت المعاد ده قبل كده."
            else:
                # التأكد إن العميل موجود
                cursor.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
                client_exists = cursor.fetchone()

                if client_exists:
                    cursor.execute("SELECT count(*) FROM client_automatic_sessions where id = %s", (client_id,))
                    total_sessions_per_week = cursor.fetchone()[0]  
                    if total_sessions_per_week < 2:
                        
                        cursor.execute("""
                            INSERT INTO client_automatic_sessions (id, client_name, phone, session_day, book_date)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (client_id, client_name, phone_number, session_date, datetime.datetime.now()))
                        conn.commit()
                        booked_confirmed_message = "✅ تم الحجز بنجاح."
                    else:
                        more_than_two_sessions = "⚠️ لقد قمت بحجز أكثر من معادين في هذا الأسبوع. "
                else:
                    message = "⚠ العميل غير موجود."

    # جلب أسماء العملاء لكل slot
    cursor.execute("SELECT session_day, client_name FROM client_automatic_sessions")
    rows = cursor.fetchall()
    booked_slots_names = {}
    for session, name in rows:
        if session not in booked_slots_names:
            booked_slots_names[session] = []
        booked_slots_names[session].append(name)

    cursor.close()
    conn.close()

    return render_template(
        "automatic_booking.html",
        booked_slots_names=booked_slots_names,
        already_booked_message=already_booked_message ,
        booked_confirmed_message=booked_confirmed_message,
        more_than_two_sessions=more_than_two_sessions,
        message=message
    )


@app.route("/cancel_booking", methods=["POST"])
def cancel_booking():
    cancel_id = request.form.get("cancel_id")
    session_day_hour = request.form.get("session_day_hour")
    session_type = request.form.get("session_type", "manual")  # نوع الحجز

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
        cursor.close()
        conn.close()

        # هنا نعمل redirect عشان نستفيد من نفس اللوجيك اللي بيجهز البيانات
        return redirect(f"/{session_type}_booking")
    else:
        cursor.close()
        conn.close()
        return redirect(f"/{session_type}_booking")

@app.route("/clients_data")
def clients_data():
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

    cursor.close()
    conn.close()

    return render_template("clients_data.html", data_manual=data_manual, data_auto=data_auto , data_mix=data_mix)
UPLOAD_FOLDER = os.path.join("static", "files")
@app.route("/add_review",methods=["GET","POST"])
def add_review():

    if request.method == "POST":
        file = request.files['file']
        caption = request.form.get('description', '')

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # حفظ الملف في فولدر static
            file.save(file_path)

            # تخزين البيانات في قاعدة البيانات
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_reviews (file_name, file_path, caption, publish_date)
                VALUES (%s, %s, %s, %s)
            """, (filename, f"static/files/{filename}", caption,datetime.datetime.today()))
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for("dashboard"))

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
    if request.method == "POST":
        filename = request.form['filename']

        conn = get_connection()
        cursor = conn.cursor()

        #validation
        cursor.execute("SELECT file_path FROM file_reviews WHERE file_name = %s", (filename,))
        file_data = cursor.fetchone()

        if file_data:
            file_path = file_data[0]

            
            cursor.execute("DELETE FROM file_reviews WHERE file_name = %s", (filename,))
            conn.commit()
            cursor.close()
            conn.close()

            
            full_path = os.path.join(os.getcwd(), file_path)
            if os.path.exists(full_path):
                os.remove(full_path)

            return redirect(url_for("dashboard"))
        else:
            cursor.close()
            conn.close()
            return "❌ الملف غير موجود", 404

    return render_template("remove_review.html")    

@app.route("/login",methods=["GET","POST"])
def login():
    message = None
    if request.method == 'POST':
        user_id = request.form['client_id']
        user_name = request.form['client_name']
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

        # check if the user is a client
        cursor.execute("SELECT id, name, course FROM clients WHERE id = %s AND name = %s", (user_id, user_name))
        existing_client = cursor.fetchone()

        if existing_client:
            course = existing_client[2]

            if course == 'manual':
                cursor.execute("SELECT client_name, id, phone, session_day FROM client_manual_sessions WHERE id = %s", (user_id,))
                sessions_manual = cursor.fetchall()
                return render_template("client_page.html", sessions_manual=sessions_manual)

            elif course == 'automatic':
                cursor.execute("SELECT client_name, id, phone, session_day FROM client_automatic_sessions WHERE id = %s", (user_id,))
                sessions_automatic = cursor.fetchall()
                return render_template("client_page.html", sessions_automatic=sessions_automatic)

            elif course == 'mix':
                cursor.execute("SELECT client_name, id, phone, session_day FROM client_manual_sessions WHERE id = %s", (user_id,))
                sessions_manual = cursor.fetchall()
                cursor.execute("SELECT client_name, id, phone, session_day FROM client_automatic_sessions WHERE id = %s", (user_id,))
                sessions_automatic = cursor.fetchall()
                return render_template("client_page.html", sessions_manual=sessions_manual, sessions_automatic=sessions_automatic)

        else:
            message = 'ادخل بيانات صحيحة !'
            return render_template("login.html", message=message)

    return render_template("login.html")

@app.route("/client_page")
def client_page():
    return render_template("client_page.html")    
if __name__=="__main__":
    app.run(debug=True)
    