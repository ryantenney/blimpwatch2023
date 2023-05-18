import socket
import time
from twilio.rest import Client

from config import *

# Time of the last sent message
last_message_time = 0

# Setup Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_twilio_message(body):
    global last_message_time
    current_time = time.time()
    # Check if an hour has passed
    if current_time - last_message_time >= 3600:
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )
        last_message_time = current_time

def parse_message(message):
    fields = message.split(',')
    if len(fields) > 4 and fields[4] in TARGET_HEX_MODE_S_CODES:
        return fields[4]
    return None

def main():
    while True:
        try:
            # Connect to the PiAware server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((PIAWARE_SERVER, PIAWARE_PORT))

            # Buffer to store incoming data
            data_buffer = ""

            while True:
                received_data = sock.recv(4096).decode('utf-8')
                data_buffer += received_data

                while "\n" in data_buffer:
                    line, data_buffer = data_buffer.split("\n", 1)
                    hex_code = parse_message(line)
                    if hex_code is not None:
                        msg = f"Aircraft with Hex Mode-S Code {hex_code} detected!\n" \
                               f"View on ADSB Exchange https://globe.adsbexchange.com/?icao={hex_code}"
                        send_twilio_message(msg)


        except socket.error as e:
            print(f"Socket error: {e}")
            print("Reconnecting in 5 seconds...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()

