import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ArmMovement(Node):
    def __init__(self, arm_auto_controller):
        super().__init__("arm_movement_node")

        self.subscription = self.create_subscription(
            String, "arm_auto_control_signal", self.listener_callback, 10
        )

        self.arm_auto_controller = arm_auto_controller

    def listener_callback(self, msg):
        """監聽來自其他節點的自動手臂控制指令"""
        command = msg.data
        self.get_logger().info(f"收到自動手臂控制指令: {command}")

        # 根據接收到的指令執行對應的自動手臂控制方法
        if command == "catch":
            self.arm_auto_controller.catch()
        elif command == "wave":
            self.arm_auto_controller.wave()
