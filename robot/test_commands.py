import serial
BAUD = 9600
DEVICE = '/dev/ttyS0'
arduino = serial.Serial(DEVICE, BAUD, timeout=None)

while True:
    try:
        command = raw_input('Enter Command: ')
        arduino.write(command)
	resp = arduino.readline()
	print resp
    except Exception:
        break
