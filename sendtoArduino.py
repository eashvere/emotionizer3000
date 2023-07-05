import time
import serial

mappings = {
    "neutral": 'n',
    "happy": 'h',
    "fear": 'f',
    "surprise": 'r',
    "sad": 's',
    "disgust": 'd',
    "angry": 'a'
}

ardu = serial.Serial('/dev/cu.usbmodem1101', 115200, timeout=0.1)

def send(str):
    #print("sent")
    #print(mappings[str].encode())
    ardu.write(mappings[str].encode())
    time.sleep(0.1)
    ardu.close()