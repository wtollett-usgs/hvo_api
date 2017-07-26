from valverest.database import db5 as db

class LavaLevel(db.Model):
    __tablename__ = 'HMM'
    __bind_key__  = 'lavalevel'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    lavalevel = db.Column(db.Float)
    tid       = db.Column(db.Integer)
    rid       = db.Column(db.Integer, primary_key=True)
    rank      = db.relationship('LavaLevelRank', uselist=False,  viewonly=True)

class LavaLevelRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'lavalevel'

    rid  = db.Column(db.Integer, db.ForeignKey('HMM.rid'), primary_key=True)
    name = db.Column(db.String(24))
    rank = db.Column(db.Integer)
