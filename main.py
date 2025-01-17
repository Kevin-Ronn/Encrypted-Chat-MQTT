import base64
import random
import threading
import queue
import paho.mqtt.client as paho
from cryptography.fernet import Fernet

CLIENT_ID = f'movant-mqtt-{random.randint(0, 1000)}'
BROKER = 'broker.hivemq.com'
PORT = 1883
CHAT_ROOMS = {
    'python': 'movantchat/python'
}

def generate_key_from_passphrase(passphrase):
    if len(passphrase) < 32:
        passphrase = passphrase.ljust(32, '0')
    elif len(passphrase) > 32:
        passphrase = passphrase[:32]
    return base64.urlsafe_b64encode(bytes(passphrase, 'utf-8'))

class Chat:
    def __init__(self, username, room, passphrase):
        self.username = username
        self.room = room
        self.topic = CHAT_ROOMS[room]
        self.client = None
        self.input_queue = queue.Queue()
        self.running = True
        self.key = generate_key_from_passphrase(passphrase)
        self.fernet = Fernet(self.key)
        self.connect_mqtt()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker as {self.username}.")
            client.subscribe(self.topic)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            decrypted_message = self.fernet.decrypt(msg.payload).decode()
            print(f"\n[{msg.topic}] {decrypted_message}")
        except Exception as e:
            print(f"Error decrypting message: {e}")

    def connect_mqtt(self):
        self.client = paho.Client(CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(BROKER, PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to broker: {e}")

    def send_message(self, message):
        try:
            encrypted_message = self.fernet.encrypt(message.encode())
            self.client.publish(self.topic, encrypted_message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def run(self):
        print(f"Welcome to the chat, {self.username}! Type your messages below.")
        while self.running:
            try:
                message = input()
                if message.lower() == '/exit':
                    self.running = False
                    self.client.loop_stop()
                    self.client.disconnect()
                else:
                    formatted_message = f"{self.username}: {message}"
                    self.send_message(formatted_message)
            except KeyboardInterrupt:
                self.running = False
                print("\nExiting chat...")
                self.client.loop_stop()
                self.client.disconnect()

if __name__ == "__main__":
    print("Enter your username:")
    username = input().strip()
    print("Enter the chat room ('python'):")
    room = input().strip()
    if room not in CHAT_ROOMS:
        print("Invalid room. Exiting.")
        exit(1)
    print("Enter a passphrase for encryption:")
    passphrase = input().strip()

    chat = Chat(username, room, passphrase)
    chat.run()
