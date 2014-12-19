from valverest.database import db5 as db

_tablenames = ['AHUD_EHZ_HV', 'AIND_HHZ_HV', 'ALEP_EHZ_HV', 'ANA2_EHZ_MI', 'ANNE_EHZ_MI', 'BYL__HHZ_HV', 'BYL__HWZ_HV',
               'CACD_EHZ_HV', 'CPKD_EHZ_HV', 'DAND_EHZ_HV', 'DESD_EHZ_HV', 'ESR__EHZ_HV', 'HAT__HHZ_HV', 'HAT__HWZ_HV',
               'HLPD_HHZ_HV', 'HLPD_HWZ_HV', 'HPAH_HHZ_PT', 'HPUD_EHZ_HV', 'HSSD_HHZ_HV', 'HSSD_HWZ_HV', 'HTCD_EHZ_HV',
               'HUAD_HHZ_HV', 'HUAD_HWZ_HV', 'HULD_HHZ_HV', 'HULD_HWZ_HV', 'JCUZ_HHZ_HV', 'JCUZ_HWL_HV', 'JCUZ_HWZ_HV',
               'JOKA_HHZ_HV', 'JOKA_HWZ_HV', 'KAAD_EHZ_HV', 'KAED_EHZ_HV', 'KHLU_HHZ_PT', 'KHU__HHZ_PT', 'KKH__EHZ_PT',
               'KKO__HHZ_HV', 'KKO__HWZ_HV', 'KKUD_EHZ_HV', 'KLUD_EHZ_HV', 'KNHD_EHZ_HV', 'KUPD_EHZ_HV', 'MITD_EHZ_HV',
               'MLOA_HHZ_PT', 'MOKD_HHZ_HV', 'MOKD_HWL_HV', 'MOKD_HWZ_HV', 'NAGD_EHZ_HV', 'NAHU_EHZ_HV', 'NPOC_HHZ_HV',
               'NPOC_HWL_HV', 'NPOC_HWZ_HV', 'NPT__HHZ_HV', 'NPT__HWL_HV', 'NPT__HWZ_HV', 'OBL__HHZ_HV', 'OBL__HWZ_HV',
               'OTLD_EHZ_HV', 'PAUD_HHZ_HV', 'PAUD_HWL_HV', 'PAUD_HWZ_HV', 'PLAD_EHZ_HV', 'POLD_EHZ_HV', 'PPLD_EHZ_HV',
               'RCOD_EHZ_HV', 'RIMD_EHZ_HV', 'RIMD_HHZ_HV', 'RIMD_HWL_HV', 'RIMD_HWZ_HV', 'RSDD_HHZ_HV', 'RSDD_HWZ_HV',
               'SAP2_EHZ_MI', 'SARN_EHZ_MI', 'SBL__HHZ_HV', 'SBL__HWZ_HV', 'SDH__HHZ_HV', 'SDH__HWZ_HV', 'SPDD_EHZ_HV',
               'STCD_HHZ_HV', 'STCD_HWZ_HV', 'SWRD_EHZ_HV', 'TOUO_HHZ_HV', 'TRAD_EHZ_HV', 'UWB__HHZ_HV', 'UWB__HWZ_HV',
               'UWE__HHZ_HV', 'WILD_EHZ_HV', 'WILD_EWL_HV', 'WOOD_EHZ_HV', 'WRM__HHZ_HV', 'WRM__HWZ_HV']

class RSAMBase(object):
    __bind_key__ = 'rsam'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    rsam      = db.Column(db.Float)

for name in _tablenames:
    c = type(name.upper(), (RSAMBase, db.Model), { '__bind_key__': 'rsam', '__tablename__': name })
    globals()[c.__name__] = c
    del c
