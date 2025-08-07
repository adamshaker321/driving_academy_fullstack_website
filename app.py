from flask import Flask,render_template,redirect,request
from db_config import get_connection
app = Flask(__name__)

@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/admin")
def admin():
    return render_template("admin.html")
@app.route("/offers")
def offers():
    return render_template("offers.html")
@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        user_id=request.form['client_id']
        user_name=request.form['client_name']
        course=request.form['course']
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("INSERT INTO clients (id,`name`,course) VALUES (%s, %s, %s)", (user_id, user_name,course))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/home')
    return render_template("register.html")
@app.route("/removing",methods=['GET','POST'])
def removing():
    if request.method=="POST":
        user_id=request.form['client_id']
        user_name=request.form['client_name']
        course=request.form['course']
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("delete from clients where id=%s",(user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/home')
    return render_template("removing.html")
@app.route("/booking")
def booking():
    return render_template("booking.html")
if __name__=="__main__":
    app.run(debug=True)