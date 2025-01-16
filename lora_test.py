import serial
import time

# Configure the serial connection to the LoRa module
lora_serial = serial.Serial(
    port='/dev/serial0',  # UART port on Raspberry Pi
    baudrate=115200,
    timeout=1
)

def send_command(command):
    """Send AT command to the LoRa module and return the response."""
    lora_serial.write((command + "\r\n").encode())  # Append \r\n to the command
    time.sleep(0.2)  # Wait for the LoRa module to process
    response = lora_serial.read_all().decode()
    return response

def configure_lora():
    """Configure the LoRa module."""
    print("Configuring LoRa module...")
    print("Response:", send_command("AT"))           # Test communication
    print("Response:", send_command("AT+RESET"))     # Reset the module
    print("Response:", send_command("AT+ADDRESS=50"))  # Set receiver address
    print("Response:", send_command("AT+NETWORKID=6"))  # Set network ID
    print("Response:", send_command("AT+BAND=915000000"))  # Set frequency band
    print("Response:", send_command("AT+PARAMETER=9,7,1,12"))  # Set parameters
    print("Response:", send_command("AT+PARAMETER?"))  # Verify parameters
    print("LoRa module configured.")

def receive_lora_data():
    """Receive and process LoRa data."""
    buffer = ""
    while True:
        try:
            if lora_serial.in_waiting > 0:
                # Read available data
                incoming_data = lora_serial.read(lora_serial.in_waiting).decode(errors="ignore")
                buffer += incoming_data

                # Check for complete messages based on newline delimiter
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)  # Split at the first newline
                    line = line.strip()  # Remove leading/trailing whitespace
                    if line:  # Ensure it's not an empty line
                        process_lora_data(line)  # Process the complete line
        except Exception as e:
            print(f"Error in receiving LoRa data: {e}")


def process_lora_data(raw_data):
    """Extract and process the received LoRa data."""
    try:
        # Example: +RCV=50,35,TEMP=24.4C,PRESS=960.2Pa,ALT=451.2m,-99,40
        payload_start = raw_data.find(",") + 1
        payload = raw_data[payload_start:]
        print(payload.strip())
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    try:
        configure_lora()
        print("Waiting for LoRa data...")
        receive_lora_data()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        lora_serial.close()
