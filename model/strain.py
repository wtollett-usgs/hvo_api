from valverest.database import db6 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['HOK', 'MLO', 'MLS']
_tidkeys    = [db.ForeignKey(x + '.tid') for x in _tablenames]
_ridkeys    = [db.ForeignKey(x + '.rid') for x in _tablenames]

class StrainBase(object):
    __bind_key__ = 'strain'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    dt01      = db.Column(db.Float)
    dt02      = db.Column(db.Float)
    barometer = db.Column(db.Float)
    tid       = db.Column(db.Integer)
    rid       = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('StrainRank', uselist=False, viewonly=True)

    @declared_attr
    def translation(self):
        return db.relationship('StrainTranslation', uselist=False, viewonly=True)

class StrainTranslation(db.Model):
    __tablename__ = 'translations'
    __bind_key__  = 'strain'

    tid        = db.Column(db.Integer, *_tidkeys, primary_key=True)
    name       = db.Column(db.String(255))
    cdt01      = db.Column(db.Float)
    ddt01      = db.Column(db.Float)
    cdt02      = db.Column(db.Float)
    ddt02      = db.Column(db.Float)
    cbarometer = db.Column(db.Float)
    dbarometer = db.Column(db.Float)

class StrainRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'strain'

    rid  = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)

for name in _tablenames:
    c = type(name.upper(), (StrainBase, db.Model), { '__bind_key__': 'strain', '__tablename__': name })
    globals()[c.__name__] = c
    del c
