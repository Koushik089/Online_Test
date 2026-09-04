import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'koushik.settings')

application = get_wsgi_application()

# Auto-migrate and seed questions on cold start
try:
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)
    call_command('seed_questions', verbosity=0)
except Exception:
    pass

app = application
