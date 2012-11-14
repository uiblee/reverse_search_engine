from flask import Flask, render_template, redirect, request, session, url_for, current_app, make_response, abort
from model import session as db_session, User 
from functools import update_wrapper
from datetime import timedelta
from flask_oauth import OAuth
import facebook

import json
from apiclient.discovery import build_from_document, build
import httplib2
import random
from oauth2client.client import OAuth2WebServerFlow

#import atom.data
import gdata.data
import gdata.contacts.client
import gdata.contacts.data

app = Flask(__name__)
app.secret_key = 'alkfjaw39nv21F5.24;55./966339fhde'

# Google OAuth

Google_clientid = '844670940206.apps.googleusercontent.com'
Google_secret = 'Q7DfeqV-JXIvfpviWae6k7sT'

@app.route('/google_login')
def google_login():
    flow = OAuth2WebServerFlow(client_id=Google_clientid,
    client_secret=Google_secret,
    scope='https://www.googleapis.com/auth/contacts',
    redirect_uri='http://localhost:5000/oauth2callback',
    approval_prompt='force',
    access_type='offline')

    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)

@app.route('/signout')
def signout():
    del session['credentials']
    session['message'] = "You have logged out"

    return redirect(url_for("log_in"))

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    if code:
    # exchange the authorization code for user credentials
        flow = OAuth2WebServerFlow(CLIENT_ID,
        CLIENT_SECRET,
        "https://www.googleapis.com/auth/contacts")
        flow.redirect_uri = request.base_url
        try:
            credentials = flow.step2_exchange(code)
        except Exception as e:
            print "Unable to get an access token because ", e.message
            # store these credentials for the current user in the session
        session['credentials'] = credentials
    return redirect(url_for('google_contacts'))

@app.route('/google_contacts')
def google_contacts():
    credentials = session['credentials']
    if credentials == None:
        return redirect(url_for('login'))
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build("contacts", "v3", http=http)
    feed = gd_client.GetContacts()
    for i, entry in enumerate(feed.entry):
        print '\n%s %s' % (i+1, entry.name.full_name.text)
        if entry.content:
            print '    %s' % (entry.content.text)


  #return render_template("index.html", calendar_list=calendar_list)


# Twitter OAuth

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='<your key here>',
    consumer_secret='<your secret here>')

def get_twitter_token(token=None):
    return session.get('twitter_token')

@app.route('/twitter_login')
def login():
    return twitter.authorize(callback=url_for('twitter_oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/twitter_oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret'])
    session['twitter_user'] = resp['screen_name']
    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(url_for ("twitter_friends"))

# need to adapt this for twitter
@app.route("/twitter_friends")
def facebook_friends():
    token = session['twitter_token']
    graph = facebook.GraphAPI(token)
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    twitter_list = [friend['name'] for friend in friends['data']]
    print twitter_list
    return render_template("index.html")

# Facebook OAuth

FACEBOOK_APP_ID = '103699949794696'
FACEBOOK_APP_SECRET = '1e4b52bacc0d598ad86f9322c567a923'

oauth = OAuth()

facebook_oauth = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': ('email, ')})

@facebook_oauth.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route("/facebook_login")
def facebook_login():
    return facebook_oauth.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route("/debug")
def debug_view():
    print session
    return

@app.route("/facebook_authorized")
@facebook_oauth.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['logged_in'] = True
    session['facebook_token'] = resp['access_token']
    return redirect(url_for("facebook_friends"))
    
@app.route("/facebook_friends")
def facebook_friends():
    token = session['facebook_token']
    graph = facebook.GraphAPI(token)
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    friend_list = [friend['name'] for friend in friends['data']]
    print friend_list
    return render_template("index.html")

def check_names():
    # replace this with ajax data
    people = open("myFile.txt")


@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))

# Pulls in Javascript/Jquery from site

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
    
#receives javascript/jquery scraping

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