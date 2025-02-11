import base64

with open("baka~.wav", "rb") as audio_file:
    encoded = base64.b64encode(audio_file.read())
    print(encoded.decode())