from db import db
from flask import session,request
def hide_topic(id):
    sql = "UPDATE topics SET visible=1 WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()  

def show_topic(id):
    sql = "UPDATE topics SET visible=0 WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()

def hiding_message(id):
    
    sql = "UPDATE messages SET visible=1 WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()  

def showing_message(id):

    sql = "UPDATE messages SET visible=0 WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()  
    