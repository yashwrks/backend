from django.urls import re_path
from home.utils.twilio_stream import TwilioMediaConsumer

websocket_urlpatterns = [
    re_path(r"ws/twilio/stream/$", TwilioMediaConsumer.as_asgi()),
]
