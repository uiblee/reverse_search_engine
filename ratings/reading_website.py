from flask import Flask, render_template, redirect, request, session, url_for, current_app, make_response
from model import session as db_session, User 
from functools import update_wrapper
from datetime import timedelta

app = Flask(__name__)

app.secret_key = 'alkfjaw39nv21F5.24;55./966339fhde'


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        print origin
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

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
        return render_template("index.html")

    return redirect(url_for("log_in"))

@app.route("/view_user_profile")
def view_user_profile():
    user_id = session['user_id']

    return render_template("view_user_profile.html")
    
@app.route("/receive_names", methods=["GET", "POST", "OPTIONS"])
@crossdomain(origin="*", headers=["X-Requested-With"])
def receive_names():
#    print request.form
#    print request.form['names']
#    print request.form['people']
    print request.form.getlist("names[]")
#    print request.form['names']

    return "Posted"



if __name__ == "__main__":
    app.run(debug=True)