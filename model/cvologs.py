from valverest.database import db3 as db

class Post(db.Model):
    __tablename__ = "tblobsinfo"
    __bind_key__  = "cvologs"

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
        self.obstypeID  = 4
        self.observtime = dt
        self.obsdate    = dt
        self.sortdate   = dt
        self.subject    = subject
        self.obstext    = text
        self.observer   = observer

class User(db.Model):
    __tablename__ = "tblusers"
    __bind_key__  = "hvologs"

    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
