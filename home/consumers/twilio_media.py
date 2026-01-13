import json
import base64
import audioop
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

from home.services.azure_stt import AzureSpeechStream
from home.services.azure_tts import AzureTTS
from home.services.gemini_llm import GeminiLLM


class TwilioMediaConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        print("🔗 Twilio WebSocket connected")

        self.call_sid = None
        self.stream_sid = None
        self.loop = asyncio.get_event_loop()

        # AI + TTS
        self.llm = GeminiLLM()
        self.tts = AzureTTS()

        # Azure STT
        self.azure_stt = AzureSpeechStream(
            on_final_text=self.sync_final_text_callback
        )

        print("✅ Azure STT + Gemini + Azure TTS initialized")

    # ---------- STT CALLBACK ----------
    def sync_final_text_callback(self, text: str):
        asyncio.run_coroutine_threadsafe(
            self.handle_final_text(text),
            self.loop
        )

    async def handle_final_text(self, text: str):
        print(f"📝 USER SAID: {text}")

        try:
            # 1️⃣ Generate AI response
            reply = self.llm.generate(text)
            print(f"🤖 AI REPLY: {reply}")

            # 2️⃣ Text → Speech (16k PCM)
            pcm_16k = self.tts.synthesize(reply)

            # 3️⃣ Convert 16k PCM → 8k μ-law
            pcm_8k, _ = audioop.ratecv(pcm_16k, 2, 1, 16000, 8000, None)
            mulaw = audioop.lin2ulaw(pcm_8k, 2)

            payload = base64.b64encode(mulaw).decode("utf-8")

            # 4️⃣ Send audio back to Twilio
            await self.send(text_data=json.dumps({
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": payload
                }
            }))

            print("🔊 AI voice sent to call")

        except Exception as e:
            print(f"❌ AI/TTS error: {e}")

    # ---------- TWILIO EVENTS ----------
    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        message = json.loads(text_data)
        event = message.get("event")

        if event == "start":
            self.call_sid = message["start"]["callSid"]
            self.stream_sid = message["start"]["streamSid"]
            print(f"📞 Call started | {self.call_sid}")

        elif event == "media":
            payload = message["media"]["payload"]

            mulaw = base64.b64decode(payload)
            pcm_8k = audioop.ulaw2lin(mulaw, 2)
            pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)

            self.azure_stt.push_audio(pcm_16k)

        elif event == "stop":
            print(f"🛑 Call ended | {self.call_sid}")
            self.azure_stt.close()
            await self.close()

    async def disconnect(self, close_code):
        print(f"❌ WebSocket disconnected | code={close_code}")
        if hasattr(self, "azure_stt"):
            self.azure_stt.close()
