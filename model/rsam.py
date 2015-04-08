from valverest.database import db5 as db

_tablenames = ['AFOK$EHZ$MI','AFOK$SHZ$MI','AHU$EHZ$HV','AHUD$BDF$HV','AHUD$EHZ$HV','AHUD$EWZ$HV','AIND$BDF$HV',
               'AIND$HHZ$HV','AIND$HWZ$HV','ALEP$EHZ$HV','ALEP$EWZ$HV','ANA2$EHZ$MI','ANA2$SHZ$MI','ANNE$EHZ$MI',
               'BYL$HHZ$HV','BYL$HWZ$HV','CAC$EHZ$HV','CACD$EHZ$HV','CPK$EHZ$HV','CPKD$EHZ$HV','CPKD$EWZ$HV',
               'DAN$EHZ$HV','DAND$EHZ$HV','DAND$EWZ$HV','DES$EHZ$HV','DESD$EHZ$HV','DESD$EWZ$HV','DEVL$HHZ$HV',
               'DHH$EHZ$PT','ESR$EHZ$HV','HAT$HHZ$HV','HAT$HWZ$HV','HILB$HHZ$PT','HLK$HHZ$PT','HLPD$HHZ$HV',
               'HLPD$HWZ$HV','HON$HHZ$PT','HPAH$HHZ$PT','HPUD$EHZ$HV','HSS$EHZ$HV','HSSD$HHZ$HV','HSSD$HWZ$HV',
               'HTCD$EHZ$HV','HTCD$EWZ$HV','HUAD$HHZ$HV','HUAD$HWZ$HV','HUL$EHZ$HV','HULD$HHZ$HV','HULD$HWZ$HV',
               'JCUZ$HHZ$HV','JCUZ$HWL$HV','JCUZ$HWZ$HV','JOKA$HHZ$HV','JOKA$HWZ$HV','KAA$EHZ$HV','KAAD$EHZ$HV',
               'KAED$EHZ$HV','KAED$EWZ$HV','KHLU1$BDF$UH','KHLU2$BDF$UH','KHLU3$BDF$UH','KHLU4$BDF$UH','KHLU$HHZ$PT',
               'KHU$BHZ$HV','KHU$HHZ$PT','KII$EHZ$HV','KKH$EHZ$PT','KKO$HHZ$HV','KKO$HWZ$HV','KKUD$EHZ$HV',
               'KLC$EHZ$HV','KLU$EHZ$HV','KLUD$EHZ$HV','KLUD$EWZ$HV','KNH$EHZ$HV','KNHD$EHZ$HV','KNHD$EWZ$HV',
               'KOHD$EHZ$HV','KUP$EHZ$HV','KUP$EWZ$HV','KUPD$EHZ$HV','KUPD$EWZ$HV','LIH$HHZ$PT','MENE1$BDF$UH',
               'MENE2$BDF$UH','MENE3$BDF$UH','MENE4$BDF$UH','MENE5$BDF$UH','MITD$EHZ$HV','MITD$EWZ$HV','MLO$EHZ$HV',
               'MLOA$HHZ$PT','MLOD$HHZ$HV','MLOD$HWZ$HV','MOK$EHZ$HV','MOKD$HHZ$HV','MOKD$HWL$HV','MOKD$HWZ$HV',
               'MPR$EHZ$HV','NAGD$EHZ$HV','NAHU$EHZ$HV','NPB$HHZ$HV','NPB$HWZ$HV','NPB$LWZ$HV','NPB$MWZ$HV',
               'NPOC$HHZ$HV','NPOC$HWL$HV','NPOC$HWZ$HV','NPT$EHZ$HV','NPT$HHZ$HV','NPT$HWL$HV','NPT$HWZ$HV',
               'OBL$HHZ$HV','OBL$HWZ$HV','OPA$HHZ$PT','OTL$EHZ$HV','OTLD$EHZ$HV','OTLD$EWZ$HV','OVE$EHZ$HV',
               'OVED$EHZ$HV','OVED$EWZ$HV','PAU$HHZ$HV','PAUD$HHZ$HV','PAUD$HWL$HV','PAUD$HWZ$HV','PLA$EHZ$HV',
               'PLAD$EHZ$HV','PLAD$EWZ$HV','POL$EHZ$HV','POLD$EHZ$HV','POLD$EWZ$HV','PPL$EHZ$HV','PPLD$EHZ$HV',
               'PPLD$EWZ$HV','RCO$EHZ$HV','RCOD$EHZ$HV','RCOD$EWZ$HV','RIM$EHZ$HV','RIMD$EHZ$HV','RIMD$HHZ$HV',
               'RIMD$HWL$HV','RIMD$HWZ$HV','RSDD$EHZ$HV','RSDD$HHZ$HV','RSDD$HWZ$HV','SAP2$EHZ$MI','SAP2$SHZ$MI',
               'SAPN$SHZ$MI','SARN$EHZ$MI','SARN$SHZ$MI','SBL$HHZ$HV','SBL$HWZ$HV','SDH$HHZ$HV','SDH$HWZ$HV',
               'SPDD$EHZ$HV','SRM$HHZ$HV','STC$BHZ$HV','STC$EHZ$HV','STCD$HHZ$HV','STCD$HWL$HV','STCD$HWZ$HV',
               'SWR$EHZ$HV','SWRD$EHZ$HV','SWRD$EWZ$HV','TOUO$HHZ$HV','TOUO$HWZ$HV','TRAD$EHZ$HV','TRAD$EWZ$HV',
               'URA$EHZ$HV','UWB$HHZ$HV','UWB$HWZ$HV','UWE$HHZ$HV','UXL$BHZ$HV','WAID$EHZ$HV','WIL$EHZ$HV',
               'WILD$EHZ$HV','WILD$EWL$HV','WILD$EWZ$HV','WMR$EHZ$PT','WOB$EHZ$HV','WOOD$EHZ$HV','WRM$HHZ$HV',
               'WRM$HWZ$HV','v_AFOK$EHZ$MI_10_min_avg','v_AFOK$SHZ$MI_10_min_avg','v_AHU$EHZ$HV_10_min_avg',
               'v_AHUD$BDF$HV_10_min_avg','v_AHUD$EHZ$HV_10_min_avg','v_AHUD$EWZ$HV_10_min_avg',
               'v_AIND$BDF$HV_10_min_avg','v_AIND$HHZ$HV_10_min_avg','v_AIND$HWZ$HV_10_min_avg',
               'v_ALEP$EHZ$HV_10_min_avg','v_ALEP$EWZ$HV_10_min_avg','v_ANA2$EHZ$MI_10_min_avg',
               'v_ANA2$SHZ$MI_10_min_avg','v_ANNE$EHZ$MI_10_min_avg','v_BYL$HHZ$HV_10_min_avg',
               'v_BYL$HWZ$HV_10_min_avg','v_CAC$EHZ$HV_10_min_avg','v_CACD$EHZ$HV_10_min_avg',
               'v_CPK$EHZ$HV_10_min_avg','v_CPKD$EHZ$HV_10_min_avg','v_CPKD$EWZ$HV_10_min_avg',
               'v_DAN$EHZ$HV_10_min_avg','v_DAND$EHZ$HV_10_min_avg','v_DAND$EWZ$HV_10_min_avg',
               'v_DES$EHZ$HV_10_min_avg','v_DESD$EHZ$HV_10_min_avg','v_DESD$EWZ$HV_10_min_avg',
               'v_DEVL$HHZ$HV_10_min_avg','v_DHH$EHZ$PT_10_min_avg','v_ESR$EHZ$HV_10_min_avg',
               'v_HAT$HHZ$HV_10_min_avg','v_HAT$HWZ$HV_10_min_avg','v_HILB$HHZ$PT_10_min_avg',
               'v_HLK$HHZ$PT_10_min_avg','v_HLPD$HHZ$HV_10_min_avg','v_HLPD$HWZ$HV_10_min_avg',
               'v_HON$HHZ$PT_10_min_avg','v_HPAH$HHZ$PT_10_min_avg','v_HPUD$EHZ$HV_10_min_avg',
               'v_HSS$EHZ$HV_10_min_avg','v_HSSD$HHZ$HV_10_min_avg','v_HSSD$HWZ$HV_10_min_avg',
               'v_HTCD$EHZ$HV_10_min_avg','v_HTCD$EWZ$HV_10_min_avg','v_HUAD$HHZ$HV_10_min_avg',
               'v_HUAD$HWZ$HV_10_min_avg','v_HUL$EHZ$HV_10_min_avg','v_HULD$HHZ$HV_10_min_avg',
               'v_HULD$HWZ$HV_10_min_avg','v_JCUZ$HHZ$HV_10_min_avg','v_JCUZ$HWL$HV_10_min_avg',
               'v_JCUZ$HWZ$HV_10_min_avg','v_JOKA$HHZ$HV_10_min_avg','v_JOKA$HWZ$HV_10_min_avg',
               'v_KAA$EHZ$HV_10_min_avg','v_KAAD$EHZ$HV_10_min_avg','v_KAED$EHZ$HV_10_min_avg',
               'v_KAED$EWZ$HV_10_min_avg','v_KHLU1$BDF$UH_10_min_avg','v_KHLU2$BDF$UH_10_min_avg',
               'v_KHLU3$BDF$UH_10_min_avg','v_KHLU4$BDF$UH_10_min_avg','v_KHLU$HHZ$PT_10_min_avg',
               'v_KHU$BHZ$HV_10_min_avg','v_KHU$HHZ$PT_10_min_avg','v_KII$EHZ$HV_10_min_avg','v_KKH$EHZ$PT_10_min_avg',
               'v_KKO$HHZ$HV_10_min_avg','v_KKO$HWZ$HV_10_min_avg','v_KKUD$EHZ$HV_10_min_avg',
               'v_KLC$EHZ$HV_10_min_avg','v_KLU$EHZ$HV_10_min_avg','v_KLUD$EHZ$HV_10_min_avg',
               'v_KLUD$EWZ$HV_10_min_avg','v_KNH$EHZ$HV_10_min_avg','v_KNHD$EHZ$HV_10_min_avg',
               'v_KNHD$EWZ$HV_10_min_avg','v_KOHD$EHZ$HV_10_min_avg','v_KUP$EHZ$HV_10_min_avg',
               'v_KUP$EWZ$HV_10_min_avg','v_KUPD$EHZ$HV_10_min_avg','v_KUPD$EWZ$HV_10_min_avg',
               'v_LIH$HHZ$PT_10_min_avg','v_MENE1$BDF$UH_10_min_avg','v_MENE2$BDF$UH_10_min_avg',
               'v_MENE3$BDF$UH_10_min_avg','v_MENE4$BDF$UH_10_min_avg','v_MENE5$BDF$UH_10_min_avg',
               'v_MITD$EHZ$HV_10_min_avg','v_MITD$EWZ$HV_10_min_avg','v_MLO$EHZ$HV_10_min_avg',
               'v_MLOA$HHZ$PT_10_min_avg','v_MLOD$HHZ$HV_10_min_avg','v_MLOD$HWZ$HV_10_min_avg',
               'v_MOK$EHZ$HV_10_min_avg','v_MOKD$HHZ$HV_10_min_avg','v_MOKD$HWL$HV_10_min_avg',
               'v_MOKD$HWZ$HV_10_min_avg','v_MPR$EHZ$HV_10_min_avg','v_NAGD$EHZ$HV_10_min_avg',
               'v_NAHU$EHZ$HV_10_min_avg','v_NPB$HHZ$HV_10_min_avg','v_NPB$HWZ$HV_10_min_avg',
               'v_NPB$LWZ$HV_10_min_avg','v_NPB$MWZ$HV_10_min_avg','v_NPOC$HHZ$HV_10_min_avg',
               'v_NPOC$HWL$HV_10_min_avg','v_NPOC$HWZ$HV_10_min_avg','v_NPT$EHZ$HV_10_min_avg',
               'v_NPT$HHZ$HV_10_min_avg','v_NPT$HWL$HV_10_min_avg','v_NPT$HWZ$HV_10_min_avg',
               'v_OBL$HHZ$HV_10_min_avg','v_OBL$HWZ$HV_10_min_avg','v_OPA$HHZ$PT_10_min_avg',
               'v_OTL$EHZ$HV_10_min_avg','v_OTLD$EHZ$HV_10_min_avg','v_OTLD$EWZ$HV_10_min_avg',
               'v_OVE$EHZ$HV_10_min_avg','v_OVED$EHZ$HV_10_min_avg','v_OVED$EWZ$HV_10_min_avg',
               'v_PAU$HHZ$HV_10_min_avg','v_PAUD$HHZ$HV_10_min_avg','v_PAUD$HWL$HV_10_min_avg',
               'v_PAUD$HWZ$HV_10_min_avg','v_PLA$EHZ$HV_10_min_avg','v_PLAD$EHZ$HV_10_min_avg',
               'v_PLAD$EWZ$HV_10_min_avg','v_POL$EHZ$HV_10_min_avg','v_POLD$EHZ$HV_10_min_avg',
               'v_POLD$EWZ$HV_10_min_avg','v_PPL$EHZ$HV_10_min_avg','v_PPLD$EHZ$HV_10_min_avg',
               'v_PPLD$EWZ$HV_10_min_avg','v_RCO$EHZ$HV_10_min_avg','v_RCOD$EHZ$HV_10_min_avg',
               'v_RCOD$EWZ$HV_10_min_avg','v_RIM$EHZ$HV_10_min_avg','v_RIMD$EHZ$HV_10_min_avg',
               'v_RIMD$HHZ$HV_10_min_avg','v_RIMD$HWL$HV_10_min_avg','v_RIMD$HWZ$HV_10_min_avg',
               'v_RSDD$EHZ$HV_10_min_avg','v_RSDD$HHZ$HV_10_min_avg','v_RSDD$HWZ$HV_10_min_avg',
               'v_SAP2$EHZ$MI_10_min_avg','v_SAP2$SHZ$MI_10_min_avg','v_SAPN$SHZ$MI_10_min_avg',
               'v_SARN$EHZ$MI_10_min_avg','v_SARN$SHZ$MI_10_min_avg','v_SBL$HHZ$HV_10_min_avg',
               'v_SBL$HWZ$HV_10_min_avg','v_SDH$HHZ$HV_10_min_avg','v_SDH$HWZ$HV_10_min_avg',
               'v_SPDD$EHZ$HV_10_min_avg','v_SRM$HHZ$HV_10_min_avg','v_STC$BHZ$HV_10_min_avg',
               'v_STC$EHZ$HV_10_min_avg','v_STCD$HHZ$HV_10_min_avg','v_STCD$HWL$HV_10_min_avg',
               'v_STCD$HWZ$HV_10_min_avg','v_SWR$EHZ$HV_10_min_avg','v_SWRD$EHZ$HV_10_min_avg',
               'v_SWRD$EWZ$HV_10_min_avg','v_TOUO$HHZ$HV_10_min_avg','v_TOUO$HWZ$HV_10_min_avg',
               'v_TRAD$EHZ$HV_10_min_avg','v_TRAD$EWZ$HV_10_min_avg','v_URA$EHZ$HV_10_min_avg',
               'v_UWB$HHZ$HV_10_min_avg','v_UWB$HWZ$HV_10_min_avg','v_UWE$HHZ$HV_10_min_avg',
               'v_UXL$BHZ$HV_10_min_avg','v_WAID$EHZ$HV_10_min_avg','v_WIL$EHZ$HV_10_min_avg',
               'v_WILD$EHZ$HV_10_min_avg','v_WILD$EWL$HV_10_min_avg','v_WILD$EWZ$HV_10_min_avg',
               'v_WMR$EHZ$PT_10_min_avg','v_WOB$EHZ$HV_10_min_avg','v_WOOD$EHZ$HV_10_min_avg',
               'v_WRM$HHZ$HV_10_min_avg','v_WRM$HWZ$HV_10_min_avg']

class RSAMBase(object):
    __bind_key__ = 'rsam'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    rsam      = db.Column(db.Float)

for name in _tablenames:
    c = type(name.upper(), (RSAMBase, db.Model), { '__bind_key__': 'rsam', '__tablename__': name })
    globals()[c.__name__] = c
    del c
