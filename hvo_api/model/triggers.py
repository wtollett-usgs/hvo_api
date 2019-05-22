# -*- coding: utf-8 -*-
from valverest.database import db6 as db

_tablenames = ['2816$HWZ$NP', 'AHUD$EWZ$HV', 'AIND$HWZ$HV', 'ALEP$EWZ$HV',
               'BYL$HWZ$HV', 'CPKD$EWZ$HV', 'DAND$EWZ$HV', 'DESD$EWZ$HV',
               'ERZ1$EWZ$HV', 'ERZ1$HWZ$HV', 'ERZ2$EWZ$HV', 'ERZ2$HWZ$HV',
               'ERZ3$HWZ$HV', 'ERZ4$HWZ$HV', 'HAT$HWZ$HV', 'HLPD$HWZ$HV',
               'HSSD$HWZ$HV', 'HTCD$EWZ$HV', 'HUAD$HWZ$HV', 'JCUZ$HWZ$HV',
               'JOKA$HWZ$HV', 'KAED$EWZ$HV', 'KHLU$HWZ$PT', 'KKH$EHZ$PT',
               'KKO$HWZ$HV', 'KLUD$EWZ$HV', 'KNHD$EWZ$HV', 'KUPD$EWZ$HV',
               'MITD$EWZ$HV', 'MLOD$HWZ$HV', 'MOKD$HWZ$HV', 'NPOC$HWZ$HV',
               'NPT$HWZ$HV', 'OBL$HWZ$HV', 'OTLD$EWZ$HV', 'P07$EHN$HV',
               'PAUD$HWZ$HV', 'PHOD$HNZ$HV', 'PHOD$HWZ$HV', 'PLAD$EWZ$HV',
               'POLD$EWZ$HV', 'PPLD$EWZ$HV', 'PUHI$HWZ$HV', 'RCOD$EWZ$HV',
               'RIMD$HWZ$HV', 'SBL$HWZ$HV', 'SDH$HWZ$HV', 'STCD$HWZ$HV',
               'SWRD$EWZ$HV', 'TOUO$HWZ$HV', 'UWB$HWZ$HV', 'WAPM$EWZ$HV',
               'WILD$EWZ$HV', 'WRM$HWZ$HV']


class TriggersBase(object):
    __bind_key__ = 'triggers'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    triggers = db.Column(db.Float)


for name in _tablenames:
    c = type(name.upper(), (TriggersBase, db.Model),
             {'__bind_key__': 'triggers', '__tablename__': name})
    globals()[c.__name__] = c
    del c
