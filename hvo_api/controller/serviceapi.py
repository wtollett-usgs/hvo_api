# -*- coding: utf-8 -*-
from flask import url_for
from flask_restful import Resource


class ServiceAPI(Resource):
    def get(self):
        return {'ASH_URL': url_for('ash'),
                'EDXRF_URL': url_for('edxrf'),
                'FLYSPEC_URL': url_for('flyspec'),
                'GPS_URL': url_for('gps'),
                'HYPOCENTER_URL': url_for('hypocenter'),
                'LASERLAVALEVEL_URL': url_for('laserlavalevel'),
                'LAVALEVEL_URL': url_for('lavalevel'),
                'LOGS_URL': url_for('logs'),
                'NPSADVISORY_URL': url_for('npsadvisory'),
                'RSAM_URL': url_for('rsam'),
                'RTNET_URL': url_for('rtnet'),
                'SO2EMISSIONS_URL': url_for('so2emissions'),
                'SO2HIGHRES_URL': url_for('so2highres'),
                'STRAIN_URL': url_for('strain'),
                'TILT_URL': url_for('tilt'),
                'TREMOR_URL': url_for('tremor'),
                'TRIGGERS_URL': url_for('triggers')}, 200
