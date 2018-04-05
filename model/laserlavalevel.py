from valverest.database import db8 as db

class LaserLavaLevel(db.Model):
    __tablename__ = 'HMM'
    __bind_key__  = 'laserlavalevel'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    sealevel    = db.Column(db.Float)
    overlook    = db.Column(db.Float)
    tid         = db.Column(db.Integer)
    rid         = db.Column(db.Integer, primary_key=True)
    rank        = db.relationship('LaserLavaLevelRank', uselist=False,  viewonly=True)
    translation = db.relationship('LaserLavaLevelTranslation', uselist=False, viewonly=True)

class LaserLavaLevelRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'laserlavalevel'

    rid  = db.Column(db.Integer, db.ForeignKey('HMM.rid'), primary_key=True)
    name = db.Column(db.String(24))
    rank = db.Column(db.Integer)

class LaserLavaLevelTranslation(db.Model):
    __tablename__ = 'translations'
    __bind_key__  = 'laserlavalevel'

    tid       = db.Column(db.Integer, db.ForeignKey('HMM.tid'), primary_key=True)
    name      = db.Column(db.String(255))
    csealevel = db.Column(db.Float)
    dsealevel = db.Column(db.Float)
    coverlook = db.Column(db.Float)
    doverlook = db.Column(db.Float)