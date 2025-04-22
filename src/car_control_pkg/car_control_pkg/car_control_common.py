import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped, Twist
from nav_msgs.msg import Path
from car_control_pkg.utils import get_action_mapping, parse_control_signal
import copy
from car_control_pkg.nav2_utils import cal_distance
from car_control_pkg.action_config import ACTION_MAPPINGS, ACTION_TO_PARA_01

import serial


class CarControlPublishers:
    """Class to manage common car control publishers and methods"""
    uart = serial.Serial(
        port="/dev/ttyAMA0",
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    def calculate_crc(data):
        crc = 0
        for byte in data:
            crc ^= byte
        return crc

    @staticmethod
    def create_publishers(node):
        """Create and return common publishers for car control"""
        rear_wheel_pub = node.create_publisher(
            Float32MultiArray, "car_C_rear_wheel", 10
        )
        front_wheel_pub = node.create_publisher(
            Float32MultiArray, "car_C_front_wheel", 10
        )

        return rear_wheel_pub, front_wheel_pub

    @staticmethod
    def create_control_subscription(node, callback):
        """Create subscription for car control signals"""
        return node.create_subscription(String, "car_control_signal", callback, 10)

    @staticmethod
    def publish_control(node, action, rear_wheel_pub, front_wheel_pub=None):
        """
        If the action is a string, it will be converted to a velocity array using the action mapping.
        If the action is a list, it will be used as the velocity array directly.
        """
        if not isinstance(action, str):
            vel = [action[0],action[1],action[0],action[1]]

        else:
            vel = get_action_mapping(action)

        dir_code = ACTION_TO_PARA_01.get(action, 0xDD)
        rpm = int(max(abs(v) for v in vel))
        rpm = min(max(rpm, 0), 300)
        upper_speed = (rpm >> 8) & 0xFF
        lower_speed = rpm & 0xFF

        data = bytearray([0xA1, dir_code, upper_speed, lower_speed])
        crc = CarControlPublishers.calculate_crc(data)
        data.append(crc)
        data.append(0x0A)

        CarControlPublishers.uart.write(data)
        print(f"[UART] Sent: {data.hex()}")



class BaseCarControlNode(Node):
    """Base class for car control nodes providing common functionality"""

    def __init__(self, node_name, enable_nav_subscribers=False):
        super().__init__(node_name)

        # Create common publishers
        self.rear_wheel_pub, self.front_wheel_pub = (
            CarControlPublishers.create_publishers(self)
        )

        # Create subscription to control signals
        self.subscription = CarControlPublishers.create_control_subscription(
            self, self.key_callback
        )

        # Navigation data storage
        self.latest_amcl_pose = None
        self.latest_goal_pose = None
        self.latest_global_plan = None
        self.latest_camera_depth = None
        self.latest_yolo_info = None
        self.latest_cmd_vel = None

        # Create navigation data subscribers if enabled
        if enable_nav_subscribers:
            self._create_navigation_subscribers()

    def _create_navigation_subscribers(self):
        """Create all subscribers needed for navigation"""
        self.amcl_sub = self.create_subscription(
            PoseWithCovarianceStamped, "/amcl_pose", self._amcl_callback, 10
        )

        self.goal_pose_sub = self.create_subscription(
            PoseStamped, "/goal_pose", self._goal_pose_callback, 10
        )

        self.plan_sub = self.create_subscription(
            Path, "/received_global_plan", self._global_plan_callback, 1
        )

        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.camera_depth_sub = self.create_subscription(
            Float32MultiArray,
            "/camera/x_multi_depth_values",
            self._camera_depth_callback,
            10,
        )

        self.yolo_sub = self.create_subscription(
            Float32MultiArray, "/yolo/target_info", self._yolo_callback, 10
        )

        self.get_logger().info("Navigation subscribers created")

    # Callback methods for navigation data
    def _amcl_callback(self, msg):
        """Store latest AMCL pose"""
        self.latest_amcl_pose = msg

    def _goal_pose_callback(self, msg):
        """Store latest AMCL pose"""
        self.latest_goal_pose = msg

    def _global_plan_callback(self, msg):
        """Store latest global plan"""
        self.latest_global_plan = msg

    def _camera_depth_callback(self, msg):
        """Store latest camera depth data"""
        self.latest_camera_depth = list(msg.data)

    def _yolo_callback(self, msg):
        """Store latest YOLO target info"""
        self.latest_yolo_info = list(msg.data)

    def get_goal_pose(self):
        """Get goal position or None if unavailable"""
        if self.latest_goal_pose is None:
            return None

        try:
            return self.latest_goal_pose.pose.position
        except AttributeError:
            # Handle cases where the message structure is unexpected
            self.get_logger().warn("Goal pose has unexpected structure")
            return None

    # Helper methods for navigation data access
    def get_car_position_and_orientation(self):
        """
        Get current car position and orientation

        Returns:
            Tuple containing (position, orientation) or (None, None) if data unavailable
        """
        if self.latest_amcl_pose:
            position = self.latest_amcl_pose.pose.pose.position
            orientation = self.latest_amcl_pose.pose.pose.orientation
            return position, orientation
        return None, None

    def cmd_vel_callback(self, msg: Twist):
        wheel_distance = 0.5
        max_speed = 30.0
        min_speed = -30.0
        v = msg.linear.x
        omega = msg.angular.z

        v_left = v - (wheel_distance / 2.0) * omega
        v_right = v + (wheel_distance / 2.0) * omega

        v_left = max(min_speed, min(max_speed, v_left))
        v_right = max(min_speed, min(max_speed, v_right))

        speed_msg = Float32MultiArray()
        speed_msg.data = [v_left, v_right]
        self.latest_cmd_vel = [v_left, v_right]


    def get_cmd_vel_data(self):
        return self.latest_cmd_vel

    def get_path_points(self, include_orientation=True):
        path_points = []

        plan_to_use = self.latest_global_plan
        if plan_to_use and plan_to_use.poses:
            for pose in plan_to_use.poses:
                pos = pose.pose.position
                if include_orientation:
                    # Return both position and orientation data
                    orient = pose.pose.orientation
                    path_points.append(
                        {
                            "position": [pos.x, pos.y, pos.z],
                            "orientation": [orient.x, orient.y, orient.z, orient.w],
                        }
                    )
                else:
                    path_points.append([pos.x, pos.y])
        return path_points

    # Common methods for all car control nodes
    def key_callback(self, msg):
        """Parse control signal and delegate to handle_command"""
        mode, command = parse_control_signal(msg.data)  # Parse signal
        if mode is None or command is None:
            return

        # Call the handle_command method that derived classes implement
        self.handle_command(mode, command)

    def publish_control(self, action):
        """Common method to publish control actions"""
        CarControlPublishers.publish_control(
            self, action, self.rear_wheel_pub, self.front_wheel_pub
        )

    # If you inherit from this class, you must implement this method
    def handle_command(self, mode, command):
        """Handle parsed commands - to be implemented by subclasses"""
        # Default implementation does nothing
        pass
