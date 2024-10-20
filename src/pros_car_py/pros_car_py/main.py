import os
import curses
import threading
import rclpy
from pros_car_py.joint_config import JOINT_UPDATES_POSITIVE, JOINT_UPDATES_NEGATIVE
from pros_car_py.car_controller import CarController
from pros_car_py.arm_controller import ArmController


class KeyboardController:
    """鍵盤控制邏輯，專注於定義按鍵與控制行為的對應"""

    def __init__(self, stdscr, car_controller, arm_controller, default_vel=10):
        self.stdscr = stdscr
        self.last_key = None
        self.car_controller = car_controller
        self.arm_controller = arm_controller

        self.vel = float(os.getenv("WHEEL_SPEED", default_vel))

        curses.noecho()
        curses.raw()
        self.stdscr.keypad(False)

        self.mode = None

    def run_mode(self):
        """在特定模式下運行鍵盤控制邏輯"""
        self.stdscr.clear()
        self.stdscr.nodelay(False)
        while True:
            self.display_mode_info()
            c = self.stdscr.getch()
            if c == ord("q"):
                break
            self.handle_key_input(chr(c))

    def display_mode_info(self):
        """顯示當前模式的信息和控制說明"""
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Current mode: {self.mode}")
        self.stdscr.addstr(1, 0, "Controls:")
        # 這裡可以根據不同的模式顯示不同的控制說明
        if self.mode == "Car Control":
            self.stdscr.addstr(2, 0, "Use arrow keys to control the car")
        elif self.mode == "Arm Control":
            self.stdscr.addstr(2, 0, "Use number keys to control arm joints")
        elif self.mode == "Combined Control":
            self.stdscr.addstr(2, 0, "Use both car and arm controls")
        self.stdscr.addstr(4, 0, "Press 'q' to return to main menu")
        if self.last_key:
            self.stdscr.addstr(6, 0, f"Last key pressed: {self.last_key}")
        self.stdscr.refresh()

    def handle_key_input(self, c):
        """處理鍵盤輸入"""
        # 根據不同的模式處理不同的按鍵
        if self.mode == "Car Control":
            self.car_controller.manual_control(c)
        elif self.mode == "Arm Control":
            # 處理機械臂控制的按鍵
            pass
        elif self.mode == "Combined Control":
            # 處理組合控制的按鍵
            pass
        self.last_key = c
        self.display_mode_info()  # 更新顯示


def main():
    rclpy.init()
    stdscr = curses.initscr()

    car_controller = CarController()
    arm_controller = ArmController()
    keyboard_controller = KeyboardController(stdscr, car_controller, arm_controller, default_vel=10)

    try:
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Select a mode:")
            stdscr.addstr(1, 0, "1. Car Control")
            stdscr.addstr(2, 0, "2. Arm Control")
            stdscr.addstr(3, 0, "3. Combined Control")
            stdscr.addstr(4, 0, "q. Quit")
            stdscr.refresh()

            choice = stdscr.getch()
            if choice == ord('q'):
                break
            elif choice in [ord('1'), ord('2'), ord('3')]:
                mode = {ord('1'): "Car Control", ord('2'): "Arm Control", ord('3'): "Combined Control"}[choice]
                keyboard_controller.mode = mode
                keyboard_controller.run_mode()
    finally:
        curses.endwin()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
