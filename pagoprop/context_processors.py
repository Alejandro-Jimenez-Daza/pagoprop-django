# pagoprop/context_processors.py

from django.conf import settings

def whatsapp_admin(request):
    """
    Hace disponible el número de WhatsApp del administrador
    en todos los templates de forma segura.
    """
    return {
        'WHATSAPP_ADMIN': settings.WHATSAPP_ADMIN
    }