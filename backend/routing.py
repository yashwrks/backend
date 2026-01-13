from django.urls import re_path
from home.consumers.twilio_media import TwilioMediaConsumer

websocket_urlpatterns = [
    re_path(r"^ws/twilio/media/$", TwilioMediaConsumer.as_asgi()),
]
