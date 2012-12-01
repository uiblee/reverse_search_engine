from flask import Flask, render_template, redirect, request, session, url_for, current_app, make_response, abort, jsonify
from model import session as db_session, User 
from functools import update_wrapper
from datetime import timedelta
from flask_oauth import OAuth, OAuthException
import facebook
import linkedin

import json
from apiclient.discovery import build_from_document, build
import httplib2
import random
from oauth2client.client import OAuth2WebServerFlow

import atom.data
import gdata.data
import gdata.contacts.client
import gdata.contacts.data
import gdata.docs.client

from rauth.service import OAuth1Service

app = Flask(__name__)
app.secret_key = 'alkfjaw39nv21F5.24;55./966339fhde'
oauth = OAuth()

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

@app.route('/google_signout')
def signout():
    del session['credentials']
    session['message'] = "You have logged out"
    return redirect(url_for("log_in"))

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    if code:
        flow = OAuth2WebServerFlow(Google_clientid,
        Google_secret,
        "https://www.googleapis.com/auth/contacts")
        flow.redirect_uri = request.base_url
        try:
            credentials = flow.step2_exchange(code)
        except Exception as e:
            print "Unable to get an access token because ", e.message
        session['credentials'] = credentials
        user_id = session['user_id']
        user = db_session.query(User).get(user_id)
        user.google_token = credentials.access_token
        db_session.commit()
    return redirect(url_for('google_contacts'))

@app.route('/google_contacts')
def google_contacts():
    user_id = session['user_id']
    google_token = db_session.query(User).get(user_id).google_token
    gd_client = gdata.contacts.client.ContactsClient(auth_token=google_token, 
        source='<var>reverse_search</var>')
    feed = gd_client.get_contacts(desired_class=gdata.contacts.data.ContactsFeed)
    #feed = gd_client.GetContacts()
    PrintFeed(feed)    
    for i, entry in enumerate(feed.entry):
        print '\n%s %s' % (i+1, entry.name.full_name.text)
        if entry.content:
            print '    %s' % (entry.content.text)

#LinkedIn API

LINKEDIN_API_BASE = 'http://api.linkedin.com/v1/'
Company_name = 'reverse_search'
Application_Name = 'reverse_search'
linkedin_API_Key = 'abg21kidsac8'
linkedin_Secret_Key ='7dcDOogWTrNmVnkA'

linkedin_api = OAuth1Service(
name = Application_Name,
consumer_key = linkedin_API_Key,
consumer_secret = linkedin_Secret_Key,
request_token_url='https://api.linkedin.com/uas/oauth/requestToken',
access_token_url='https://api.linkedin.com/uas/oauth/accessToken',
authorize_url='https://www.linkedin.com/uas/oauth/authenticate')

@app.route('/linkedin_login')
def linkedin_login():
    app.logger.debug('authorize app in linkedin')
    request_token, request_token_secret = \
        linkedin_api.get_request_token(method='GET',
                                  oauth_callback='http://localhost:5000/linkedin_tokens',
                                  params={"scope": "r_basicprofile r_emailaddress r_fullprofile r_network"})   
    session['request_token'] = request_token
    session['request_token_secret'] = request_token_secret    
    authorize_url = linkedin_api.get_authorize_url(request_token)
    return redirect(authorize_url)

@app.route("/linkedin_tokens")
def linkedin_tokens():  
    request_token = request.args.get('oauth_token', None)
    request_token_secret = session['request_token_secret']
    verifier = request.args.get('oauth_verifier', None)
    print 'debug: ', request_token, request_token_secret, verifier
    if request_token and verifier:
        print 'Request TOKEN: ', request_token
        print 'VERIFIER: ', verifier
        resp = linkedin_api.get_access_token('POST',
             request_token=request_token,
             request_token_secret=request_token_secret,
             data={'oauth_verifier': verifier})                
        assert resp.response.status_code == 200, resp.response.reason
        data = resp.content
        access_token = data['oauth_token']
        access_token_secret = data['oauth_token_secret']
        session['access_token'] = access_token
        session['access_token_secret'] = access_token_secret
        user_id = session['user_id']
        user = db_session.query(User).get(user_id)
        user.linkedin_token = json.dumps([access_token, access_token_secret])
        db_session.commit()
        print access_token, access_token_secret, user.linkedin_token
        return redirect(url_for('linkedin_connections'))
    else:
        app.logger.debug('redirecting to login')
        return redirect(url_for('linkedin_login'))
   
@app.errorhandler(OAuthException)
def handle_oauth_exception(error):
    return redirect(url_for("linkedin_connections"))

@app.route('/linkedin_connections')
def linkedin_connections():
    if not 'access_token' in session:
        return redirect(url_for('linkedin_login'))
    user_id = session['user_id']
    linkedin_token = json.loads(db_session.query(User).get(user_id).linkedin_token)
    access_token = linkedin_token[0]
    access_token_secret = linkedin_token[1]
    response = linkedin_api.get(
        LINKEDIN_API_BASE + 'people/~/connections',
        params={'format': 'json'},
        access_token=access_token,
        access_token_secret=access_token_secret)
    connections = response.content
    connections = connections['values']
    li_connections = []
    li_connections_employer = {}
    for connection in connections:
        connection_name = connection['firstName'] + " " + connection['lastName']
        li_connections.append(connection_name)
        if connection.get("headline") is None:
            continue
        pull_employer = connection['headline']
        employment = connection['headline'].split(" at ")
        if len(employment) > 1:
            title = employment[0]
            employer = employment[1]
        else:
            title = employment[0]
            employer = None
        # title, employer = connection['headline'].split(" at ", 2)
        # connection_employer = re.match("\sat\s(\S*\s*\S*)", connection_employer)
        if employer:
            #try:
            li_connections_employer.setdefault(employer, []).append(connection_name)
            #     li_connections_employer[employer].append(connection_name)
            # except KeyError:
            #     li_connections_employer[employer] = connection_name
    print li_connections
    print li_connections_employer
    user_id = session['user_id']
    return render_template("index.html", li_connections=li_connections, 
        li_connections_employer=li_connections_employer, user_id=user_id)

# Twitter OAuth

# twitter = oauth.remote_app('twitter',
#     base_url='https://api.twitter.com/1/',
#     request_token_url='https://api.twitter.com/oauth/request_token',
#     access_token_url='https://api.twitter.com/oauth/access_token',
#     authorize_url='https://api.twitter.com/oauth/authenticate',
#     consumer_key='<your key here>',
#     consumer_secret='<your secret here>')

# def get_twitter_token(token=None):
#     return session.get('twitter_token')

# @app.route('/twitter_login')response = linkedin.get(
    #     LINKEDIN_API_BASE + 'people/~/connections',
    #     params={'format': 'json'},
    #     access_token=session.get('access_token'),
    #     access_token_secret=session.get('access_token_secret'))
    # resp = response.content 
    # print resp['_total']
    # return 'You have: ' + str(resp['_total']) + ' connections.'
# def login():
#     return twitter.authorize(callback=url_for('twitter_oauth_authorized',
#         next=request.args.get('next') or request.referrer or None))

# @app.route('/twitter_oauth-authorized')
# @twitter.authorized_handler
# def oauth_authorized(resp):
#     next_url = request.args.get('next') or url_for('index')
#     if resp is None:
#         flash(u'You denied the request to sign in.')
#         return redirect(next_url)
#     session['twitter_token'] = (
#         resp['oauth_token'],
#         resp['oauth_token_secret'])
#     session['twitter_user'] = resp['screen_name']
#     flash('You were signed in as %s' % resp['screen_name'])
#     return redirect(url_for ("twitter_friends"))

# # need to adapt this for twitter
# @app.route("/twitter_friends")
# def facebook_friends():
#     token = session['twitter_token']
#     graph = facebook.GraphAPI(token)
#     profile = graph.get_object("me")
#     friends = graph.get_connections("me", "friends")
#     twitter_list = [friend['name'] for friend in friends['data']]
#     print twitter_list
#     return render_template("index.html")

# Facebook OAuth

FACEBOOK_APP_ID = '103699949794696'
FACEBOOK_APP_SECRET = '1e4b52bacc0d598ad86f9322c567a923'

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
    user_id = session['user_id']
    user = db_session.query(User).get(user_id)
    user.facebook_token = resp['access_token']
    db_session.commit()
    return redirect(url_for("facebook_friends"))
    
@app.route("/facebook_friends")
def facebook_friends():
    token = session['facebook_token']
    graph = facebook.GraphAPI(token)
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    friend_list = [friend['name'] for friend in friends['data']]
    user_id = session['user_id']
    print friend_list
    return render_template("index.html", friend_list=friend_list, user_id=user_id)

def check_names(friend_list, names_from_site, keywords, linkedin_connections, 
    linkedin_connections_employer):
    connections = {}
    friend_list = [friend.lower() for friend in friend_list]
    names_from_site = [name.lower() for name in names_from_site]
    keywords = [keyword.lower() for keyword in keywords]
    linkedin_connections = [connection.lower() for connection in linkedin_connections]
    # linkedin_connections_employer = linkedin_connections_employer((k.lower(), v) for k,v in 
    #     {'My Key':'My Value'}.iteritems())
    for person in names_from_site:
        person_dict = {}
        if person in friend_list:
            person_dict['facebook'] = True            
        if person in keywords:
            person_dict['keywords'] = True
        if person in linkedin_connections:
            person_dict['linkedin'] = True
        if person in linkedin_connections_employer:
            employing = linkedin_connections_employer.get(person)
            person_dict['company'] = employing
        if person_dict:
            connections[person] = person_dict
    return connections

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))

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

@app.route("/about")
def about():
    return render_template("about.html")

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
        return redirect("/view_user_profile")
    return redirect(url_for("log_in"))

@app.route("/view_user_profile")
def view_user_profile():
    print session
    user_id = session['user_id']
    keywords = db_session.query(User).get(user_id).keywords
    if keywords:
        keywords = json.loads(keywords)
    if not keywords:
        keywords = []
    return render_template("view_user_profile.html", user_id=user_id, keywords=keywords)
    
@app.route("/view_user_profile/<int:user_id>", methods=["POST"])
def user_keywords(user_id):
    keywords = request.form['keywords']
    if not keywords:
        return redirect("/view_user_profile")
    listed_keywords = keywords.split(';')
    user = db_session.query(User).get(user_id)
    old_keywords = json.loads(user.keywords or "[]") or []
    keywords = old_keywords + listed_keywords    
    keywords = json.dumps(keywords)
    user.keywords = keywords
    db_session.commit()
    return redirect("/view_user_profile")

@app.route("/delete_keywords/<keyword>", methods=['GET'])
def delete_user_keywords(keyword):
    user_id = session['user_id']
    user = db_session.query(User).get(user_id)
    
    old_keywords = json.loads(user.keywords)
    old_keywords.remove(keyword)
    keywords = json.dumps(old_keywords)
    user.keywords = keywords
    db_session.commit()
    return redirect("/view_user_profile")

@app.route("/receive_names/<int:user_id>", methods=["GET", "POST", "OPTIONS"])
@crossdomain(origin="*", headers=["X-Requested-With"])
def receive_names(user_id):
    names_from_site = request.form.getlist("names[]")
    friend_list = pulling_friends(user_id)
    linkedin_connections, linkedin_connections_employer = pulling_connections(user_id)
    keywords = json.loads(db_session.query(User).get(user_id).keywords)
    connections = check_names(friend_list, names_from_site, keywords, linkedin_connections, 
        linkedin_connections_employer)
    print connections
    return jsonify(connections)
    
def pulling_friends(user_id):
    facebook_token = db_session.query(User).get(user_id).facebook_token
    graph = facebook.GraphAPI(facebook_token)
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    friend_list = [friend['name'] for friend in friends['data']]
    return friend_list

def pulling_connections(user_id):
    linkedin_token = json.loads(db_session.query(User).get(user_id).linkedin_token)
    access_token = linkedin_token[0]
    access_token_secret = linkedin_token[1]
    response = linkedin_api.get(
        LINKEDIN_API_BASE + 'people/~/connections',
        params={'format': 'json'},
        access_token=access_token,
        access_token_secret=access_token_secret)
    connections = response.content
    connections = connections['values']
    li_connections = []
    li_connections_employer = {}
    for connection in connections:
        connection_name = connection['firstName'] + " " + connection['lastName']
        li_connections.append(connection_name)
        if connection.get("headline") is None:
            continue
        pull_employer = connection['headline']
        employment = connection['headline'].split(" at ")
        if len(employment) > 1:
            title = employment[0]
            employer = employment[1]
        else:
            title = employment[0]
            employer = None
        if employer:
            employer = employer.lower()
            li_connections_employer.setdefault(employer, []).append(connection_name)          
    return li_connections, li_connections_employer

if __name__ == "__main__":
    app.run(debug=True)