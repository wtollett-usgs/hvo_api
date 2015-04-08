from valverest.database import db3 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['FLY0', 'FLY1', 'FLY2', 'FLY3', 'FLY4', 'FLY5', 'FLY6', 'FLY7', 'FLY8', 'FLY9', 'FLYA']
_ridkeys    = [db.ForeignKey(x + '.rid') for x in _tablenames]

class FlyspecBase(object):
    __bind_key__ = 'flyspec'

    timestamp        = db.Column('j2ksec', db.Float, primary_key=True)
    bstflux          = db.Column(db.Float)
    bstfluxmean      = db.Column(db.Float)
    bstfluxmeanstdev = db.Column(db.Float)
    flux01           = db.Column(db.Float)
    fluxsdh          = db.Column(db.Float)
    ps               = db.Column(db.Float)
    pd               = db.Column(db.Float)
    specs            = db.Column(db.Float)
    nflag            = db.Column(db.Float)
    sflag            = db.Column(db.Float)
    colpath          = db.Column(db.Float)
    satpix           = db.Column(db.Float)
    inttime          = db.Column(db.Float)
    boxtemp          = db.Column(db.Float)
    sysvolt          = db.Column(db.Float)
    current          = db.Column(db.Float)
    tid              = db.Column(db.Integer)
    rid              = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('FlyspecRank', uselist=False)

class FlyspecRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'flyspec'

    rid  = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)

for name in _tablenames:
    c = type(name.upper(), (FlyspecBase, db.Model), { '__bind_key__': 'flyspec', '__tablename__': name })
    globals()[c.__name__] = c
    del c
