import os
import sys
from django.core.wsgi import get_wsgi_application
sys.path.append('/django/desarrollo/catastro')
sys.path.append('/django/desarrollo/catastro/catastro')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catastro.settings')

application = get_wsgi_application()