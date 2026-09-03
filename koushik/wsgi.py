import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'koushik.settings')

application = get_wsgi_application()

# Vercel expects 'app' as the handler
app = application
