import sys

sys.path.append('/hvo/www/html/hvo_api')
sys.path.append('/hvo/www/html/hvo_api/env/lib/python2.6/site-packages')

from valverest import create_app
application = create_app(env='prod')
