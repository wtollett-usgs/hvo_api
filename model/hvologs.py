from sqlalchemy.ext.declarative import declared_attr
from valverest.database import db2 as db

class Post(db.Model):
    __tablename__ = 'tblobsinfo'
    __bind_key__  = 'hvologs'

    obsID      = db.Column(db.Integer, primary_key=True)
    userID     = db.Column(db.Integer, default=0)
    obstypeID  = db.Column(db.Integer)
    observtime = db.Column(db.DateTime)
    subject    = db.Column(db.String(255))
    parentID   = db.Column(db.String(255))
    obstext    = db.Column(db.Text)
    obsdate    = db.Column(db.DateTime)
    observer   = db.Column(db.Text)
    sortdate   = db.Column(db.DateTime)
    published  = db.Column(db.String)

    @declared_attr
    def user(self):
        return db.relationship('LogUser', uselist=False)

class Volcano(db.Model):
    __tablename__ = 'volcano'
    __bind_key__  = 'hvologs'

    volcano_id   = db.Column(db.String(10), primary_key=True)
    volcano_name = db.Column(db.String(50))

class VolcLink(db.Model):
    __tablename__ = 'tbllinkobstovolcid'
    __bind_key__  = 'hvologs'

    linkobstovolcid = db.Column(db.Integer, unique=True)
    VolcNameID      = db.Column(db.Integer, primary_key=True)
    obsid           = db.Column(db.Integer, primary_key=True)
    volcano_id      = db.Column(db.String(25))

class KeywordLink(db.Model):
    __tablename__ = 'tbllinkobstoobskeywordid'
    __bind_key__  = 'hvologs'

    linkobstoobskeywordid = db.Column(db.Integer, unique=True)
    obsid                 = db.Column(db.Integer, primary_key=True)
    obskeywordid          = db.Column(db.Integer, primary_key=True)

class LogUser(db.Model):
    __tablename__ = 'user'
    __bind_key__  = 'hvologsauth'

    user_id = db.Column(db.Integer, db.ForeignKey('tblobsinfo.userID'), primary_key=True)
    first   = db.Column(db.String)
    last    = db.Column(db.String)
