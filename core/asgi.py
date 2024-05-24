"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_asgi_application()



# project/core/asgi.py
# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator, OriginValidato
# from channels.auth import AuthMiddlewareStack
# from apps.notification import routing

# django_asgi_app = get_asgi_application()

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# # Initialize Django ASGI application early to ensure the AppRegistry
# # is populated before importing code that may import ORM models.


# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator(
#         AuthMiddlewareStack(  
#             URLRouter(
#                 routing.websocket_urlpatterns
#             )
#         )
#     ),
# })
