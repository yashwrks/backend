from twilio.twiml.voice_response import VoiceResponse, Start, Stream


def media_stream_twiml():
    response = VoiceResponse()

    start = Start()
    start.append(
        Stream(
            url="wss://YOUR_NGROK_DOMAIN/ws/twilio/media/"
        )
    )

    response.append(start)
    response.say("Hello, you are now connected to the AI agent.")

    return str(response)
