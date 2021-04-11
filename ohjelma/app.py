from flask import Flask
from flask import redirect, render_template, request,session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash



app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT password FROM usersf WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if user == None:
    # TODO: invalid username

        return render_template("index.html", word="WRONG USERNAME")

    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
        # TODO: correct username and password
            redirect("/topics")
        else:
            return render_template("index.html", word="WRONG PASSWORD")
        # TODO: invalid password
        
    session["username"] = username
    return redirect("/topics")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/createUserRedirect")
def createUserRedirect():
    
    return render_template("createUser.html")

@app.route("/createUser",methods=["POST"])
def createUser():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO usersf (username,password) VALUES (:username,:password)"
    db.session.execute(sql, {"username":username,"password":hash_value})
    db.session.commit()
    
    return redirect("/")


@app.route("/topics")
def front():
    
    
    sql =db.session.execute("SELECT topic,username,topics.id FROM topics, usersf, topic_creator WHERE topics.id=topic_creator.topic_id and topic_creator.user_id=usersf.id")
    topics = sql.fetchall()
    
    #result = db.session.execute("SELECT id, topic FROM topics")
    #topics = result.fetchall()
    
    #result = db.session.execute("SELECT user_id, topic_id FROM topic_creator")###
    #user_ids = result.fetchall()

    
    #result = db.session.execute("SELECT username FROM userfs")
    #usernames = result.fetchall()#####################################################

    return render_template("topics.html", topics=topics)

@app.route("/create",methods=["POST"])
def create():
    username=session.get('username')
    topic = request.form["topic"]

    sql = "INSERT INTO topics (topic) VALUES (:topic) RETURNING id" ###uusi 
    result =db.session.execute(sql, {"topic":topic}) ###uusi
    topic_id = result.fetchone()[0] ##uusi

    aql = "SELECT id FROM usersf WHERE username=:username"
    resultaql = db.session.execute(aql, {"username":username})
    user_id = resultaql.fetchone()[0]
    
    bql = "INSERT INTO topic_creator (topic_id, user_id) VALUES (:topic_id, :user_id)"
    db.session.execute(bql, {"topic_id":topic_id, "user_id":user_id})
    
    db.session.commit()  
   
    return redirect("/topics")

@app.route("/new_topic")
def new_subject():
    return render_template("new_topic.html")


@app.route("/topic/<int:id>")
def subject(id):
    
    
    sql = "SELECT topic,id FROM topics WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()[0]
    
    sql = text("SELECT message,username FROM messages WHERE message_id=:id")
    result = db.session.execute(sql,{"id":id} )
    messages = result.fetchall()
    

    return render_template("messages.html",topic=topic, id = id, messages = messages)

@app.route("/send",methods=["POST"])
def send():
    username=session.get('username')
    message_id = request.form["id"]

    message = request.form["message"]
    sql = "INSERT INTO messages (message, message_id,username) VALUES (:message, :message_id, :username)"
    db.session.execute(sql, {"message":message,"message_id":message_id,"username":username})
    
    db.session.commit()
    return redirect("/topic/"+str(message_id))

@app.route("/<username>")
def user(username):
    name = username
    sql=("SELECT T.id, topic, username FROM topics T, usersf U, topic_creator C WHERE U.username=:username AND T.id = C.topic_id AND C.user_id = U.id")
    result =db.session.execute(sql,{"username":username})

    return render_template("test.html",result =result,name = name)

@app.route("/search")
def search():
    

    query = request.args["query"]
    sql = "SELECT id, topic FROM topics WHERE topic LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    topics = result.fetchall()
    return render_template("search.html",topics=topics)


@app.route("/search_message")
def search_message():
    
    query =request.args["query_message"]
    sql = "SELECT id, message FROM messages WHERE message LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    messages = result.fetchall()

    return render_template("search.html",messages=messages)

@app.route("/search_user")
def search_user():
    
    query =request.args["query_user"]
    sql = "SELECT id, username FROM usersf WHERE username LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    users = result.fetchall()

    return render_template("search.html",users=users)

@app.route("/searchgo")
def topic_search():
    return render_template("search.html")