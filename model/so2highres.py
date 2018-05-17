from valverest.database import db9 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['HRCPK', 'HRHLK', 'HRNPT', 'HRPKE', 'HRPLO', 'HRSDH']
_tidkeys    = [db.ForeignKey(x + '.tid') for x in _tablenames]
_ridkeys    = [db.ForeignKey(x + '.rid') for x in _tablenames]

class SO2HighResBase(object):
    __bind_key__ = 'so2highres'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    so2       = db.Column(db.Float)
    ws        = db.Column(db.Float)
    wd        = db.Column(db.Float)
    wdstd     = db.Column(db.Float)
    gust      = db.Column(db.Float)
    xtemp     = db.Column(db.Float)
    rh        = db.Column(db.Float)
    bp        = db.Column(db.Float)
    tip       = db.Column(db.Float)
    itemp     = db.Column(db.Float)
    bv        = db.Column(db.Float)
    flow      = db.Column(db.Float)
    elecbv    = db.Column(db.Float)
    tid       = db.Column(db.Integer)
    rid       = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('SO2HighResRank', uselist=False, viewonly=True)

    @declared_attr
    def translation(self):
        return db.relationship('SO2HighResTranslation', uselist=False, viewonly=True)

class SO2HighResTranslation(db.Model):
    __tablename__ = 'translations'
    __bind_key__  = 'so2highres'

    tid     = db.Column(db.Integer, *_tidkeys, primary_key=True)
    name    = db.Column(db.String(255))
    cso2    = db.Column(db.Float)
    dso2    = db.Column(db.Float)
    cws     = db.Column(db.Float)
    dws     = db.Column(db.Float)
    cwd     = db.Column(db.Float)
    dwd     = db.Column(db.Float)
    cwdstd  = db.Column(db.Float)
    dwdstd  = db.Column(db.Float)
    cgust   = db.Column(db.Float)
    dgust   = db.Column(db.Float)
    cxtemp  = db.Column(db.Float)
    dxtemp  = db.Column(db.Float)
    crh     = db.Column(db.Float)
    drh     = db.Column(db.Float)
    cbp     = db.Column(db.Float)
    dbp     = db.Column(db.Float)
    ctip    = db.Column(db.Float)
    dtip    = db.Column(db.Float)
    citemp  = db.Column(db.Float)
    ditemp  = db.Column(db.Float)
    cbv     = db.Column(db.Float)
    dbv     = db.Column(db.Float)
    cflow   = db.Column(db.Float)
    dflow   = db.Column(db.Float)
    celecbv = db.Column(db.Float)
    delecbv = db.Column(db.Float)

class SO2HighResRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'so2highres'

    rid  = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)

for name in _tablenames:
    c = type(name.upper(), (SO2HighResBase, db.Model), { '__bind_key__': 'so2highres', '__tablename__': name })
    globals()[c.__name__] = c
    del c
