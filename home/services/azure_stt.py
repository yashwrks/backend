import os
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import languageconfig


class AzureSpeechStream:
    def __init__(self, on_final_text):
        self.on_final_text = on_final_text

        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION")

        if not self.speech_key or not self.region:
            raise RuntimeError("Azure Speech credentials missing")

        # 🔹 Speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.region
        )

        # 🔥 Auto language detect (Hindi + Hinglish + English)
        self.auto_lang_config = languageconfig.AutoDetectSourceLanguageConfig(
            languages=["hi-IN", "en-IN", "en-US"]
        )

        # 🔹 Audio format (Twilio → Azure STT compatible)
        self.audio_format = speechsdk.audio.AudioStreamFormat(
            samples_per_second=16000,
            bits_per_sample=16,
            channels=1
        )

        self.push_stream = speechsdk.audio.PushAudioInputStream(
            self.audio_format
        )

        self.audio_config = speechsdk.audio.AudioConfig(
            stream=self.push_stream
        )

        # 🔥 IMPORTANT: auto_detect_source_language_config
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config,
            auto_detect_source_language_config=self.auto_lang_config
        )

        self._wire_events()
        self.recognizer.start_continuous_recognition()

    def _wire_events(self):

        # Partial (live words)
        self.recognizer.recognizing.connect(
            lambda evt: print(f"🟡 PARTIAL: {evt.result.text}")
        )

        # Final recognized text
        def recognized(evt):
            if evt.result.text:
                print(f"🟢 FINAL: {evt.result.text}")
                self.on_final_text(evt.result.text)

        self.recognizer.recognized.connect(recognized)

        self.recognizer.session_stopped.connect(
            lambda evt: print("🛑 Azure session stopped")
        )

    def push_audio(self, pcm_bytes: bytes):
        self.push_stream.write(pcm_bytes)

    def close(self):
        self.push_stream.close()
        self.recognizer.stop_continuous_recognition()
