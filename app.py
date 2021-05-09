from start import start
from flask import redirect, render_template, request,session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy import text
from sqlalchemy import exc
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

import searches
import visible



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
    try:
        db.session.execute(sql, {"username":username,"password":hash_value})

        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        error = "Nimi on varattu! valitse toinen nimi"
        return render_template("error.html",error = error )
    return redirect("/")


@start.route("/topics")
def front():
    
    name=session.get('username')
    
    sql ="SELECT username  FROM usersf WHERE username=:name"
    result =db.session.execute(sql, {"name":name})
    if  result.fetchone() == None: 
        error = " ei oikeutta, luo käyttäjä tili"
        return render_template("error.html", error = error)
    else:
        sql =db.session.execute("SELECT topic,usersf.username,topics.id,topics.visible,time FROM topics, usersf, topic_creator WHERE topics.id=topic_creator.topic_id and topic_creator.user_id=usersf.id")
        topics = sql.fetchall()


        return render_template("topics.html", topics=topics)

@start.route("/create",methods=["POST"])
def create():
    username=session.get('username')
    topic = request.form["topic"]
    if len(topic) > 120:
        return render_template("new_topic.html", error="Otsikko ei saa olla yli 120 merkkiä")
    else:    
        sql = "INSERT INTO topics (topic,visible,time) VALUES (:topic,0,NOW()) RETURNING id" 
        result =db.session.execute(sql, {"topic":topic}) 
        topic_id = result.fetchone()[0] 

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
    
    name=session.get('username')
    
    sql ="SELECT username  FROM usersf WHERE username=:name"
    result =db.session.execute(sql, {"name":name})
    if  result.fetchone() == None: 
        error = " ei oikeutta, luo käyttäjä tili"
        return render_template("error.html", error = error)
    else:
    
        sql = "SELECT topic,id FROM topics WHERE id=:id"
        result = db.session.execute(sql, {"id":id})
        topic = result.fetchone()[0]
    
        sql = text("SELECT message,username,visible,id,time FROM messages WHERE message_id=:id")
        result = db.session.execute(sql,{"id":id} )
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
    sql = "INSERT INTO messages (message, message_id,username,visible,time) VALUES (:message, :message_id, :username, :visible,NOW())"
    db.session.execute(sql, {"message":message,"message_id":message_id,"username":username,"visible":0})
    
    db.session.commit()
    return redirect("/topic/"+str(message_id))

@start.route("/<username>")
def user(username):
    uname=session.get('username')
    
    sql ="SELECT username  FROM usersf WHERE username=:uname"
    result =db.session.execute(sql, {"uname":uname})
    if  result.fetchone() == None: 
        error = " ei oikeutta, luo käyttäjä tili"
        return render_template("error.html", error = error)
    else:
        name = username
        user=session.get('username')
        sql=("SELECT T.id, topic, username FROM topics T, usersf U, topic_creator C WHERE U.username=:username AND T.id = C.topic_id AND C.user_id = U.id AND T.visible = 0")
        result =db.session.execute(sql,{"username":username})
    
        sql=("SELECT message,topic,topics.id FROM messages,topics WHERE username=:username AND messages.visible=:0 AND message_id =topics.id ")
        messages = db.session.execute(sql,{"username":username,"0":0})
    
        sql= ("SELECT * FROM private_messages WHERE username_from=:user OR username_to=:user")
        private = db.session.execute(sql,{"user":user,"user":user})

        return render_template("test.html",result =result,name = name, messages= messages,private=private)

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
    name=session.get('username')
    
    sql ="SELECT username  FROM usersf WHERE username=:name"
    result =db.session.execute(sql, {"name":name})
    if  result.fetchone() == None: 
        error = " ei oikeutta, luo käyttäjä tili"
        return render_template("error.html", error = error)
    else:
        return render_template("search.html")

@start.route("/hide/<int:id>")
def hide(id):
    visible.hide_topic(id)
    
    return redirect("/topics")

@start.route("/show/<int:id>")
def show(id):  
    visible.show_topic(id)
    return redirect("/topics")

@start.route("/hide_message/<int:id>")
def hide_message(id):
    topic_id = request.referrer
    visible.hiding_message(id)
    
    return redirect(topic_id)

@start.route("/show_message/<int:id>" )
def show_message(id):
    topic_id = request.referrer
    visible.showing_message(id)
    
    return redirect(topic_id)


@start.route("/send_private",methods=["POST"])
def send_private():
    page = request.referrer
    username_from=session.get('username')
    
    username_to = request.form['name']
    message = request.form["message"]
    
    sql = "INSERT INTO private_messages (message,username_from,username_to,visible,time) VALUES (:message,  :username,:username_to, :visible,NOW())"
    db.session.execute(sql, {"message":message,"username":username_from,"username_to":username_to,"visible":0})
    
    db.session.commit()
    return redirect(page)

