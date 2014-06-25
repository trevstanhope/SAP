import serial
BAUD = 9600
DEVICE = '/dev/ttyS0'
arduino = serial.Serial(DEVICE, BAUD)

while True:
    try:
        command = raw_input('Enter Command: ')
        arduino.write(command)
    except Exception:
        break
