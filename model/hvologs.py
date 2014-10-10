from valverest.database import db2 as db

class Post(db.Model):
    __tablename__ = 'tblobsinfo'
    __bind_key__  = 'hvologs'

    obsID      = db.Column(db.Integer, primary_key=True)
    userID     = db.Column(db.Integer, default=0)
    obstypeID  = db.Column(db.Integer)
    observtime = db.Column(db.DateTime)
    subject    = db.Column(db.String(255))
    obstext    = db.Column(db.Text)
    obsdate    = db.Column(db.DateTime)
    observer   = db.Column(db.Text)
    sortdate   = db.Column(db.DateTime)

    def __init__(self, uid, dt, subject, text, observer):
        self.userID     = uid
        self.obstypeID  = 4 # Seismology
        self.observtime = dt
        self.obsdate    = dt
        self.sortdate   = dt
        self.subject    = subject
        self.obstext    = text
        self.observer   = observer

class User(db.Model):
    __tablename__ = 'tblusers'
    __bind_key__  = 'hvologs'

    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)

class ListVolc(db.Model):
    __tablename__ = 'tbllistvolc'
    __bind_key__  = 'hvologs'

    VolcNameID = db.Column(db.Integer, primary_key=True)
    Volcano    = db.Column(db.String(50))

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

    def __init__(self, volcname, obs, volcid):
        self.VolcNameID = volcname
        self.obsid      = obs
        self.volcano_id = volcid
