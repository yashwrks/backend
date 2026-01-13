import json
import os
import base64
import azure.cognitiveservices.speech as speechsdk
from channels.generic.websocket import AsyncWebsocketConsumer

class TwilioMediaConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        print("🟢 Twilio WebSocket Connected")

        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )

        self.audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=self.audio_stream)

        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )

        self.recognizer.recognized.connect(self.on_recognized)
        self.recognizer.start_continuous_recognition()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["event"] == "media":
            audio = base64.b64decode(data["media"]["payload"])
            self.audio_stream.write(audio)

    async def disconnect(self, close_code):
        self.audio_stream.close()
        self.recognizer.stop_continuous_recognition()
        print("🔴 Call Ended")

    def on_recognized(self, evt):
        if evt.result.text:
            print("📝 USER SAID:", evt.result.text)
