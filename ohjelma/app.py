from ohjelma.start import start
from flask import redirect, render_template, request,session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from ohjelma.db import db

import ohjelma.searches




@start.route("/")
def index():
    return render_template("index.html")

@start.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    

    sql = "SELECT password,admin FROM usersf WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    

    if user == None:
    
        return render_template("index.html", word="WRONG USERNAME")

    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):

            session["username"] = username
            if user[1] == 1:
                session["level"] = "admin"
            else:
                session["level"] = "normal"
            
            return redirect("/topics")
        else:
            return render_template("index.html", word="WRONG PASSWORD")
    
        
    
    return redirect("/topics")

@start.route("/logout")
def logout():
    del session["username"]
    
    return redirect("/")

@start.route("/createUserRedirect")
def createUserRedirect():
    
    return render_template("createUser.html")

@start.route("/createUser",methods=["POST"])
def createUser():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO usersf (username,password) VALUES (:username,:password)"
    db.session.execute(sql, {"username":username,"password":hash_value})
    db.session.commit()
    
    return redirect("/")


@start.route("/topics")
def front():
    
    
    sql =db.session.execute("SELECT topic,usersf.username,topics.id,topics.visible FROM topics, usersf, topic_creator WHERE topics.id=topic_creator.topic_id and topic_creator.user_id=usersf.id")
    topics = sql.fetchall()

   
    
    #result = db.session.execute("SELECT id, topic FROM topics")
    #topics = result.fetchall()
    
    #result = db.session.execute("SELECT user_id, topic_id FROM topic_creator")###
    #user_ids = result.fetchall()

    
    #result = db.session.execute("SELECT username FROM userfs")
    #usernames = result.fetchall()#####################################################

    return render_template("topics.html", topics=topics)

@start.route("/create",methods=["POST"])
def create():
    username=session.get('username')
    topic = request.form["topic"]

    sql = "INSERT INTO topics (topic,visible) VALUES (:topic,0) RETURNING id" ###uusi 
    result =db.session.execute(sql, {"topic":topic}) ###uusi
    topic_id = result.fetchone()[0] ##uusi

    aql = "SELECT id FROM usersf WHERE username=:username"
    resultaql = db.session.execute(aql, {"username":username})
    user_id = resultaql.fetchone()[0]
    
    bql = "INSERT INTO topic_creator (topic_id, user_id) VALUES (:topic_id, :user_id)"
    db.session.execute(bql, {"topic_id":topic_id, "user_id":user_id})
    
    db.session.commit()  
   
    return redirect("/topics")

@start.route("/new_topic")
def new_subject():
    return render_template("new_topic.html")


@start.route("/topic/<int:id>")
def subject(id):
    
    
    sql = "SELECT topic,id FROM topics WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()[0]
    
    sql = text("SELECT message,username FROM messages WHERE message_id=:id AND visible=:1")
    result = db.session.execute(sql,{"id":id,"1":1} )
    messages = result.fetchall()
    
    sql ="SELECT  COUNT(message) FROM messages WHERE visible = 1 AND message_id=:id  GROUP BY message_id;"
    result = db.session.execute(sql,{"id":id} )
    count = result.fetchall() 
    

    return render_template("messages.html",topic=topic, id = id, messages = messages,count =count)

@start.route("/send",methods=["POST"])
def send():
    username=session.get('username')
    message_id = request.form["id"]

    message = request.form["message"]
    sql = "INSERT INTO messages (message, message_id,username,visible) VALUES (:message, :message_id, :username, :visible)"
    db.session.execute(sql, {"message":message,"message_id":message_id,"username":username,"visible":1})
    
    db.session.commit()
    return redirect("/topic/"+str(message_id))

@start.route("/<username>")
def user(username):
    name = username
    sql=("SELECT T.id, topic, username FROM topics T, usersf U, topic_creator C WHERE U.username=:username AND T.id = C.topic_id AND C.user_id = U.id AND T.visible = 0")
    result =db.session.execute(sql,{"username":username})
    
    sql=("SELECT message FROM messages WHERE username=:username AND visible=:1 ")
    messages = db.session.execute(sql,{"username":username,"1":1})
    

    return render_template("test.html",result =result,name = name, messages= messages)

@start.route("/search")
def search():

    topics = searches.get_topic()

    return render_template("search.html",topics=topics)


@start.route("/search_message")
def search_message():
    
    messages = searches.get_messages()

    return render_template("search.html",messages=messages)

@start.route("/search_user")
def search_user():
    
    users = searches.get_user()

    return render_template("search.html",users=users)

@start.route("/searchgo")
def topic_search():
    return render_template("search.html")

@start.route("/hide/<int:id>")
def hide(id):
   
    sql = "UPDATE topics SET visible=1 WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()  
    
    return redirect("/topics")

@start.route("/show/<int:id>")
def show(id):
    sql = "UPDATE topics SET visible=0 WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()  
    
    return redirect("/topics")

