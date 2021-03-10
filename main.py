from flask import Flask, render_template, request, redirect, url_for, make_response
from models.dbsettings import db
from models.user import User
from models.topic import Topic
from models.comment import Comment
import uuid
import hashlib
import datetime
import os
import smartninja_redis

redis = smartninja_redis.from_url(os.environ.get("REDIS_URL"))

app = Flask(__name__)
db.create_all()

# Get the User - from session_token or None is logged in.
@app.route("/get_user")
def get_user():
    session_token = request.cookies.get("session_token")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None
    return user

# Home Page - if no User, log-in
@app.route("/")
def index():
    user = get_user()
    # if user:
    #     return render_template("topic_create.html", user=user)
    # else:
    return render_template("index.html", user=user)

# Login handler
@app.route("/login", methods=["GET", "POST"])
def login():
    # display the index page to allow login credentials.
    if request.method == "GET":
        return render_template("index.html")

    # enter the login credentials
    else:
        email = request.form.get("user-email")
        password = request.form.get("login-password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # define the user
        user = db.query(User).filter_by(email=email).first()
        # if no user, then haven't signed up.
        if not user:
            return render_template("signup.html")
        else:
            # if there is a user, checking on correct password
            if hashed_password != user.password_hash:
                return "Incorrect Password.  Please Try Again"
            # is the user active?  If so, proceed, if not, back to signup.
            elif user.active == 1:
                # if active, create session_token and commit to the database
                session_token = str(uuid.uuid4())
                user.session_token = session_token

                db.add(user)
                db.commit()

                response = make_response(redirect(url_for('index')))
                response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

            return response

# Signup handler - create a new user.
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # displays the signup page
    if request.method == "GET":
        return render_template("signup.html")
    else:
        # Get the new user information.
        name = request.form.get("user-name")
        email = request.form.get("user-email")
        password = request.form.get("signup-password")
        password2 = request.form.get("signup-password2")
        # Do the two passwords match?
        if password != password2:
            return "The Passwords Do Not Match.  Please try again."
        else:
            # if the passwords match, create a new user, put it in the db.
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            session_token = str(uuid.uuid4())
            active = 1
            user = User(name=name, email=email, password_hash=hashed_password, session_token=session_token, active=active)

            db.add(user)
            db.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response

# Logout handler - deletes the session_token for that user.  Displays the Index page for login.
@app.route("/logout")
def logout():

    session_token = ""
    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", session_token)
    return response

@app.route("/all_topics", methods=["GET"])
def all_topics():

    all_topics = db.query(Comment.topic).all()

    return render_template("all_topics.html", comments=all_topics)


# Topic View handler
@app.route("/topic_view/<topic_id>", methods=["GET"])
def topic_view(topic_id):

    topic = db.query(Topic).get(int(topic_id))
    comments = db.query(Comment).filter_by(topic_id=topic_id).all()

    return render_template("topic_view.html", topic=topic, comments=comments)



# Create the Topic Handler
@app.route("/topic_create", methods=["GET", "POST"])
def topic_create():

    user = get_user()

    # only a logged in user can create a topic.
    if not user:
        render_template("signup.html")

    # Display the Topic Create Page
    if request.method == "GET":
        # create the csrf token
        csrf_token = str(uuid.uuid4())
        # use the redis app
        redis.set(name=csrf_token, value=user.name)

        return render_template("topic_create.html", user=user, csrf_token=csrf_token)

    elif request.method == "POST":
    #     Get the CSRF token back and ensure that it matches what was sent.
        csrf = request.form.get("csrf")
        redis_csrf_name = redis.get(name=csrf).decode()

        # see that the csrf came back and then that it matches what was sent
        if redis_csrf_name and redis_csrf_name == user.name:
            # Create the Topic Title, Text and post it.

            topic_title = request.form.get("topic-title")
            topic_text = request.form.get("topic-text")
            created = datetime.datetime.now().date()
            # Post it
            topic = Topic.create(title=topic_title, text=topic_text, created=created, creator=user)

            return redirect(url_for('all_topics'))
        else:
            return "CSRF token is not valid"


# handler to edit a topic
@app.route("/topic_edit/<topic_id>", methods=["GET", "POST"])
def topic_edit(topic_id):

    # get the topic that is to be edited
    topic = db.query(Topic).get(int(topic_id))

    # Only allow the creator of the Topic to edit it.
    user = get_user()

    if user.name == topic.creator.name:

        # display the topic to be edited
        if request.method == "GET":
            return render_template("topic_edit.html", topic=topic)
        # get the edited topic details and post it
        else:
            topic.title = request.form.get("new-topic-title")
            topic.text = request.form.get("new-topic-text")

            db.commit()

            return redirect(url_for('all_topics'))
    else:
        return "You are not the author of this topic.  Edit is not allowed."

# Create the Comment Create Handler
@app.route("/comment_create/<topic_id>", methods=["GET", "POST"])
def comment_create(topic_id):

    user = get_user()

    # only a logged in user can comment on a topic.
    if not user:
        render_template("signup.html")

    # get the topic that is to be edited
    topic = db.query(Topic).get(int(topic_id))

    # Display the Comment Create Page
    if request.method == "GET":
        # create the csrf token
        csrf_token = str(uuid.uuid4())
        # use the redis app
        redis.set(name=csrf_token, value=user.name)

        return render_template("comment_create.html", user=user, csrf_token=csrf_token, topic=topic)

    elif request.method == "POST":
    #     Get the CSRF token back and ensure that it matches what was sent.
        csrf = request.form.get("csrf")
        redis_csrf_name = redis.get(name=csrf).decode()

        # see that the csrf came back and then that it matches what was sent
        if redis_csrf_name and redis_csrf_name == user.name:

            # Create the Topic Comment and post it.

            comment_text = request.form.get("comment-text")
            created = datetime.datetime.now().date()
            # Post it
            comment = Comment.create(text=comment_text, created=created, author=user, topic=topic)

            return redirect(url_for('all_topics'))
        else:
            return "CSRF token is not valid"



if __name__ == '__main__':
    app.run()