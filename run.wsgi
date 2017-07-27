import sys

sys.path.append('/hvo/www/html/hvo_api')

from valverest import create_app
application = create_app(env='prod')
