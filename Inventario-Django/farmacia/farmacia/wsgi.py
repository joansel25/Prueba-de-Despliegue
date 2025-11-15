"""
WSGI config for farmacia project.
"""

import os
import sys

# ✅ CONFIGURACIÓN CRÍTICA PARA VERCEL
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmacia.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Esto ayudará a ver el error en los logs
    def application(environ, start_response):
        start_response('500 Error', [('Content-Type', 'text/plain')])
        return [f"Error: {str(e)}".encode()]