from valverest.database import db10 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['69FL', '92YN', 'AHUP', 'ALEP', 'BDPK', 'BLBP', 'BYRL', 'CALS',
               'CNPK', 'CRIM', 'DEVL', 'EPLA', 'ERZ1', 'ERZ2', 'ERZ3', 'ERZ4',
               'HILR', 'HOVE', 'HOVL', 'JCUZ', 'JOKA', 'KAMO', 'KEAM', 'KIND',
               'KOSM', 'MKAI', 'MLRD', 'MLSP', 'MOKP', 'NANT', 'NPIT', 'NUPM',
               'OUTL', 'PG2R', 'PHAN', 'PKMU', 'PMAU', 'PUHI', 'PULU', 'PUOC',
               'PWRL', 'TOUO', 'UWEV', 'V120', 'VO46', 'VO47', 'VSAS', 'WAPM']
_ridkeys    = [db.ForeignKey(x + '.rid') for x in _tablenames]

class RTNetBase(object):
    __bind_key__ = 'rtnet'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    north     = db.Column(db.Float)
    northErr  = db.Column(db.Float)
    east      = db.Column(db.Float)
    eastErr   = db.Column(db.Float)
    up        = db.Column(db.Float)
    upErr     = db.Column(db.Float)
    qual      = db.Column(db.Float)
    numL1Amb  = db.Column(db.Float)
    numSat    = db.Column(db.Float)
    numL2Amb  = db.Column(db.Float)
    tropDel   = db.Column(db.Float)
    tropErr   = db.Column(db.Float)
    rid       = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('RTNetRank', uselist=False, viewonly=True)

class RTNetRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'rtnet'

    rid  = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)

for name in _tablenames:
    c = type(name.upper(), (RTNetBase, db.Model), { '__bind_key__': 'rtnet', '__tablename__': name })
    globals()[c.__name__] = c
    del c
