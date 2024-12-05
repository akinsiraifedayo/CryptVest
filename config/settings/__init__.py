

# your_project/settings/__init__.py

import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from ..production import *
    import pymysql
    pymysql.install_as_MySQLdb()
else:
    from ..development import *
