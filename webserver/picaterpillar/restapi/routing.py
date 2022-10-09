from django.urls import re_path

from restapi import consumers

websocket_urlpatterns = [
    re_path(r'ws/uart/$', consumers.UartConsumer.as_asgi()),
]