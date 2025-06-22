import pyfirmata
import time

board = pyfirmata.Arduino('COM3')
pin9 = board.get_pin('d:9:s')
iter8 = pyfirmata.util.Iterator(board)
iter8.start()

for angle in range(0, 181, 30):
    pin9.write(angle)
    time.sleep(1)

board.exit()
