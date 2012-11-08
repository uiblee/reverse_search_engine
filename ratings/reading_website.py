from flask import Flask, render_template, redirect, request, session, url_for
from model import session as db_session, User 

app = Flask(__name__)

app.secret_key = 'alkfjaw39nv21F5.24;55./966339fhde'

@app.route("/")
def index():
    user_list = db_session.query(User).all()
    return render_template("add_user.html")

@app.route("/login")
def log_in():
        return render_template("add_user.html")

@app.route("/new_user", methods=["POST"])
def add_user():
    username = request.form['username']
    password = request.form['password']
    current_added_user = User.new_user(username, password)
    return redirect("/view_user_profile")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    print request.form
    username = request.form['username']
    password = request.form['password']
    user = db_session.query(User).filter_by(username=username).first()
    if not user:
        return redirect(url_for("log_in"))
    
    if user.password == password:
        session['user_id'] = user.id
        return redirect(url_for("view_user_profile"))

    return redirect(url_for("log_in"))

@app.route("/view_user_profile")
def view_user_profile():
    user_id = session['user_id']

    return render_template("view_user_profile.html")
    



if __name__ == "__main__":
    app.run(debug=True)