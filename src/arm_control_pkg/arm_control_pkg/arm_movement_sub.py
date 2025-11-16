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

        # 如果正在做任務，阻擋新任務（stop 除外）
        if command not in ["stop"]:
            if self.task_thread and self.task_thread.is_alive():
                self.get_logger().info("手臂正在執行任務，請稍後再試")
                return

        # =====================================================================
        # catch
        # =====================================================================
        if command == "catch":
            self.stop_event.clear()

            def run_catch():
                self.arm_auto_controller.catch(
                    should_cancel=lambda: self.stop_event.is_set()
                )
                if not self.stop_event.is_set():
                    self.get_logger().info("catch 任務完成")

            self.task_thread = threading.Thread(target=run_catch)
            self.task_thread.start()

        # =====================================================================
        # catch2（新增完成訊息）
        # =====================================================================
        elif command == "catch2":
            self.stop_event.clear()

            def run_catch2():
                self.arm_auto_controller.catch2(
                    should_cancel=lambda: self.stop_event.is_set()
                )
                if not self.stop_event.is_set():  # 確保不是 stop 強制中斷
                    self.get_logger().info("catch2 任務完成")

            self.task_thread = threading.Thread(target=run_catch2)
            self.task_thread.start()

        # =====================================================================
        # stop
        # =====================================================================
        elif command == "stop":
            self.get_logger().info("收到停止指令")
            self.stop_event.set()

            if self.task_thread and self.task_thread.is_alive():
                self.task_thread.join()

            self.get_logger().info("任務已停止，手臂回到初始位置")
            self.arm_auto_controller.init_pose()
