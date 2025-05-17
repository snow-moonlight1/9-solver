import base64

# 确保这里的文件名与实际文件名大小写一致
with open("baka~.WAV", "rb") as audio_file:
    encoded = base64.b64encode(audio_file.read())
    data = encoded.decode()
    
    with open("audio_data.py", "w", encoding="utf-8") as f:
        f.write(f"AUDIO_DATA = '''{data}'''\n")
    
    print("音频数据已更新至audio_data.py")