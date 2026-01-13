import audioop
import base64

def pcm16k_to_twilio(pcm_16k: bytes) -> str:
    # 16kHz → 8kHz
    pcm_8k, _ = audioop.ratecv(pcm_16k, 2, 1, 16000, 8000, None)

    # PCM → μ-law
    mulaw = audioop.lin2ulaw(pcm_8k, 2)

    return base64.b64encode(mulaw).decode("utf-8")
