import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading


class ArmMovement(Node):
    def __init__(self, arm_auto_controller):
        super().__init__("arm_movement_node")

        self.subscription = self.create_subscription(
            String, "arm_auto_control_signal", self.listener_callback, 10
        )

        self.arm_auto_controller = arm_auto_controller
        self.task_thread = None
        self.stop_event = threading.Event()

    def listener_callback(self, msg):
        """監聽來自其他節點的自動手臂控制指令"""
        command = msg.data
        self.get_logger().info(f"收到自動手臂控制指令: {command}")

        # 根據接收到的指令執行對應的自動手臂控制方法
        if command == "catch":
            if self.task_thread and self.task_thread.is_alive():
                self.get_logger().info("手臂正在執行任務，請稍後再試")
                return

            self.stop_event.clear()
            self.task_thread = threading.Thread(
                target=self.arm_auto_controller.catch,
                kwargs={'should_cancel': lambda: self.stop_event.is_set()}
            )
            self.task_thread.start()

        elif command == "stop":
            self.get_logger().info("收到停止指令")
            self.stop_event.set()
            if self.task_thread and self.task_thread.is_alive():
                self.task_thread.join()
            self.get_logger().info("任務已停止，手臂回到初始位置")
            self.arm_auto_controller.init_pose()
