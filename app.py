
from flask import Flask,render_template,redirect,request
from db_config import get_connection
app = Flask(__name__)

@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/admin",methods=['GET','POST'])
def admin():
    if request.method=='POST':
        admin_id=request.form['Admin_id']
        admin_name=request.form['Admin_name']
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("select admin_id from admins")
        rows=cursor.fetchall()
        for row in rows:
            if admin_id ==row[0]:
                return redirect("/dashboard")
            else:
                return redirect("/admin")
    return render_template("admin.html")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
@app.route("/offers")
def offers():
    return render_template("offers.html")
@app.route("/register",methods=['GET','POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['client_id']
        user_name = request.form['client_name']
        course = request.form['course']

        conn = get_connection()
        cursor = conn.cursor()

        # نشوف إذا الـ ID موجود
        cursor.execute("SELECT id FROM clients WHERE id = %s", (user_id,))
        existing_client = cursor.fetchone()

        if existing_client:
            # لو موجود يرجعه لنفس الصفحة
            cursor.close()
            conn.close()
            return redirect("/register")
        else:
            # لو مش موجود يضيفه
            cursor.execute("INSERT INTO clients (id, `name`, course) VALUES (%s, %s, %s)", 
                           (user_id, user_name, course))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/dashboard')

    return render_template("register.html")
@app.route("/removing", methods=['GET', 'POST'])
def removing():
    if request.method == "POST":
        user_id = request.form['client_id']

        conn = get_connection()
        cursor = conn.cursor()

        # تحقق إذا العميل موجود
        cursor.execute("SELECT id FROM clients WHERE id = %s", (user_id,))
        existing_client = cursor.fetchone()

        if existing_client:
            # حذف العميل
            cursor.execute("DELETE FROM clients WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect("/dashboard")
        else:
            # لو العميل مش موجود
            cursor.close()
            conn.close()
            return redirect("/removing")  # أو صفحة تنبيه

    return render_template("removing.html")
@app.route("/booking")
def booking():
    return render_template("booking.html")
@app.route("/cancel_booking")
def cancel_booking():
    return render_template("cancel_booking.html")

@app.route("/clients_data")
def clients_data():
    conn = get_connection()
    cursor = conn.cursor()

    # بيانات المانيوال
    cursor.execute("SELECT id, name, course FROM clients WHERE course = 'مانيوال'")
    data_manual = cursor.fetchall()

    # بيانات الأوتوماتيك
    cursor.execute("SELECT id, name, course FROM clients WHERE course = 'اوتوماتيك'")
    data_auto = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("clients_data.html", data_manual=data_manual, data_auto=data_auto)
if __name__=="__main__":
    app.run(debug=True)
