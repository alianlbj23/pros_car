# car_control_pkg/action_config.py

vel = 50.0
vel_slow = 5.0
rotate_vel = 50.0
rotate_vel_slow = 3.0
rotate_vel_median = 5.0

ACTION_MAPPINGS = {
    "FORWARD": [vel, vel, vel, vel],
    "FORWARD_SLOW": [vel_slow, vel_slow, vel_slow, vel_slow],
    "LEFT_FRONT": [rotate_vel, rotate_vel * 1.2, rotate_vel, rotate_vel * 1.2],
    "COUNTERCLOCKWISE_ROTATION": [-rotate_vel, rotate_vel, -rotate_vel, rotate_vel],
    "COUNTERCLOCKWISE_ROTATION_SLOW": [-rotate_vel_slow, rotate_vel_slow, -rotate_vel_slow, rotate_vel_slow],
    "COUNTERCLOCKWISE_ROTATION_MEDIAN": [-rotate_vel_median, rotate_vel_median, -rotate_vel_median, rotate_vel_median],
    "BACKWARD": [-vel, -vel, -vel, -vel],
    "BACKWARD_SLOW": [-vel_slow, -vel_slow, -vel_slow, -vel_slow],
    "CLOCKWISE_ROTATION": [rotate_vel, -rotate_vel, rotate_vel, -rotate_vel],
    "CLOCKWISE_ROTATION_SLOW": [rotate_vel_slow, -rotate_vel_slow, rotate_vel_slow, -rotate_vel_slow],
    "CLOCKWISE_ROTATION_MEDIAN": [rotate_vel_median, -rotate_vel_median, rotate_vel_median, -rotate_vel_median],
    "RIGHT_FRONT": [rotate_vel * 1.2, rotate_vel, rotate_vel * 1.2, rotate_vel],
    "RIGHT_SHIFT": [rotate_vel, -rotate_vel, -rotate_vel, rotate_vel],
    "LEFT_SHIFT": [-rotate_vel, rotate_vel, rotate_vel, -rotate_vel],
    "LEFT_BACK": [-rotate_vel, -rotate_vel * 1.2, -rotate_vel, -rotate_vel * 1.2],
    "RIGHT_BACK": [rotate_vel * 1.2, rotate_vel, rotate_vel * 1.2, rotate_vel],
    "STOP": [0.0, 0.0, 0.0, 0.0],
}

ACTION_TO_PARA_01 = {
    "FORWARD": 0x11,
    "FORWARD_SLOW": 0x11,
    "BACKWARD": 0x22,
    "BACKWARD_SLOW": 0x22,
    "CLOCKWISE_ROTATION": 0x33,
    "CLOCKWISE_ROTATION_SLOW": 0x33,
    "CLOCKWISE_ROTATION_MEDIAN": 0x33,
    "COUNTERCLOCKWISE_ROTATION": 0x44,
    "COUNTERCLOCKWISE_ROTATION_SLOW": 0x44,
    "COUNTERCLOCKWISE_ROTATION_MEDIAN": 0x44,
    "RIGHT_SHIFT": 0x55,
    "LEFT_SHIFT": 0x66,
    "RIGHT_FRONT": 0x77,
    "LEFT_FRONT": 0x88,
    "LEFT_BACK": 0x99,
    "RIGHT_BACK": 0xAA,
    "STOP": 0xDD,
}
