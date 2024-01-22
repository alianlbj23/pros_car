import os

SERIAL_DEV_DEFAULT = os.getenv('SERIAL_DEV_DEFAULT', '/dev/usb_rear_wheel')  # replace with your default value
SERIAL_DEV_FORWARD_DEFAULT = os.getenv('SERIAL_DEV_FORWARD_DEFAULT', '/dev/usb_front_wheel')  # replace with your default value
# ARM_SERIAL_PORT_DEFAULT = '/dev/ttyUSB0'  # replace with your default value
ARM_SERIAL_PORT_DEFAULT = os.getenv('ARM_SERIAL_PORT', '/dev/ttyUSB0')
WHEEL_SPEED = os.getenv('WHEEL_SPEED')
# SERIAL_BACK_DEFAULT = os.getenv('SERIAL_BACK_DEFAULT', '/dev/ttyUSB0')  # replace with your default value
# SERIAL_FRONT_DEFAULT = os.getenv('SERIAL_FRONT_DEFAULT', '/dev/ttyUSB1')  # replace with your default value
