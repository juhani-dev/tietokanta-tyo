from ohjelma.db import db
from flask import session,request
from werkzeug.security import check_password_hash, generate_password_hash


def get_topic():
    query = request.args["query"]
    sql = "SELECT id, topic FROM topics WHERE topic LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    topics = result.fetchall()
    return topics

def get_messages():
    query =request.args["query_message"]
    sql = "SELECT username, message FROM messages WHERE message LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    messages = result.fetchall()
    return messages

def get_user():
    query =request.args["query_user"]
    sql = "SELECT id, username FROM usersf WHERE username LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    users = result.fetchall()
    return users
