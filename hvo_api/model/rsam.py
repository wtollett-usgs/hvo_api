# -*- coding: utf-8 -*-
from valverest.database import db5 as db

_tablenames = ['2836$HNZ$NP', 'AHUD$BDF$HV', 'AHUD$EHZ$HV', 'AHUD$EWZ$HV',
               'AIND$BDF$HV', 'AIND$HHZ$HV', 'AIND$HWZ$HV', 'ALEP$EHZ$HV',
               'ALEP$EWZ$HV', 'BYL$HHZ$HV', 'BYL$HWZ$HV', 'CACD$EHZ$HV',
               'CPKD$EHZ$HV', 'CPKD$EWZ$HV', 'DAND$EHZ$HV', 'DAND$EWZ$HV',
               'DESD$EHZ$HV', 'DESD$EWZ$HV', 'DEVL$HHZ$HV', 'DHH$EHZ$PT',
               'ELEP$EHZ$HV', 'ERZ1$HHZ$HV', 'ERZ1$HWZ$HV', 'ERZ2$HHZ$HV',
               'ERZ2$HWZ$HV', 'ERZ3$HHZ$HV', 'ERZ3$HWZ$HV', 'ERZ4$HHZ$HV',
               'ERZ4$HWZ$HV', 'ERZ5$HHZ$HV', 'HAT$HHZ$HV', 'HAT$HWZ$HV',
               'HILB$HHZ$PT', 'HLK$HHZ$PT', 'HLPD$HHZ$HV', 'HLPD$HWZ$HV',
               'HON$HHZ$PT', 'HOVE$HHZ$HV', 'HOVE$HWZ$HV', 'HPUD$EHZ$HV',
               'HSSD$HHZ$HV', 'HSSD$HWZ$HV', 'HTCD$EHZ$HV', 'HTCD$EWZ$HV',
               'HUAD$HHZ$HV', 'HUAD$HWZ$HV', 'JCUZ$HHZ$HV', 'JCUZ$HWL$HV',
               'JCUZ$HWZ$HV', 'JOKA$HHZ$HV', 'JOKA$HWZ$HV', 'KAAD$EHZ$HV',
               'KAED$EHZ$HV', 'KAED$EWZ$HV', 'KEKH$HHZ$PT', 'KHLH$HHZ$PT',
               'KHLU$HHZ$PT', 'KHLU1$BDF$UH', 'KHLU2$BDF$UH', 'KHLU3$BDF$UH',
               'KHLU4$BDF$UH', 'KHU$HHZ$PT', 'KIND$HHZ$HV', 'KIND$HWZ$HV',
               'KKH$EHZ$PT', 'KKO$HHZ$HV', 'KKO$HWZ$HV', 'KKUD$EHZ$HV',
               'KLUD$EHZ$HV', 'KLUD$EWZ$HV', 'KNHD$EHZ$HV', 'KNHD$EWZ$HV',
               'KOHD$EHZ$HV', 'KUPD$EHZ$HV', 'KUPD$EWZ$HV', 'LIH$HHZ$PT',
               'MENE1$BDF$UH', 'MENE2$BDF$UH', 'MENE3$BDF$UH', 'MENE4$BDF$UH',
               'MENE5$BDF$UH', 'MITD$EHZ$HV', 'MITD$EWZ$HV', 'MLOA$HHZ$PT',
               'MLOD$HHZ$HV', 'MLOD$HWZ$HV', 'MOKD$HHZ$HV', 'MOKD$HWL$HV',
               'MOKD$HWZ$HV', 'NAGD$EHZ$HV', 'NAHU$EHZ$HV', 'NPOC$HHZ$HV',
               'NPOC$HWL$HV', 'NPOC$HWZ$HV', 'NPT$HHZ$HV', 'NPT$HWL$HV',
               'NPT$HWZ$HV', 'OBL$HHZ$HV', 'OBL$HWZ$HV', 'OPA$HHZ$PT',
               'OTLD$EHZ$HV', 'OTLD$EWZ$HV', 'OVED$EHZ$HV', 'OVED$EWZ$HV',
               'P07$EHE$HV', 'P07$EHN$HV', 'P07$EHZ$HV', 'P07$EWZ$HV',
               'PAUD$HHZ$HV', 'PAUD$HWL$HV', 'PAUD$HWZ$HV', 'PHOD$HNE$HV',
               'PHOD$HNN$HV', 'PHOD$HNZ$HV', 'PHOD$HWZ$HV', 'PLAD$EHZ$HV',
               'PLAD$EWZ$HV', 'POLD$EHZ$HV', 'POLD$EWZ$HV', 'PPLD$EHZ$HV',
               'PPLD$EWZ$HV', 'PUHI$HHZ$HV', 'PUHI$HWZ$HV', 'RCOD$EHZ$HV',
               'RCOD$EWZ$HV', 'RIMD$HHZ$HV', 'RIMD$HWL$HV', 'RIMD$HWZ$HV',
               'RSDD$EHZ$HV', 'SBL$HHZ$HV', 'SBL$HWZ$HV', 'SDH$HHZ$HV',
               'SDH$HWZ$HV', 'SKAM$HHZ$HV', 'SPDD$EHZ$HV', 'STCD$HHZ$HV',
               'STCD$HWL$HV', 'STCD$HWZ$HV', 'SWRD$EHZ$HV', 'SWRD$EWZ$HV',
               'TOUO$HHZ$HV', 'TOUO$HWZ$HV', 'TRAD$EHZ$HV', 'TRAD$EWZ$HV',
               'UWB$HHZ$HV', 'UWB$HWZ$HV', 'UWE$HHZ$HV', 'WAID$EHZ$HV',
               'WAPM$EHZ$HV', 'WAPM$EWZ$HV', 'WILD$EHZ$HV', 'WILD$EWL$HV',
               'WILD$EWZ$HV', 'WMR$EHZ$PT', 'WOOD$EHZ$HV', 'WRM$HHZ$HV',
               'WRM$HWZ$HV']


class RSAMBase(object):
    __bind_key__ = 'rsam'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    rsam = db.Column(db.Float)


for name in _tablenames:
    c = type(name.upper(), (RSAMBase, db.Model),
             {'__bind_key__': 'rsam', '__tablename__': name})
    globals()[c.__name__] = c
    del c
