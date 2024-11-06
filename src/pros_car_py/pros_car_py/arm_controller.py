# return 角度一律 radians
import math
from rclpy.node import Node
from pros_car_py.car_models import DeviceDataTypeEnum
import numpy as np
import time
class ArmController():
    """
    A class to control a robotic arm.

    This class provides methods to update joint positions, reset the arm, and publish the current arm position.
    It handles individual and multiple joint updates with angle limits, and allows resetting the arm to default positions.

    Attributes:
        _init_joint_pos (list[float]): A list of initial joint angles (in radians).
        joint_pos (list[float]): A list of current joint angles (in radians).
        joint_trajectory_publisher_ (Publisher): ROS2 publisher for publishing the arm's joint trajectory.

    Methods:
        clamp(value, min_value, max_value):
            Clamps a value between a minimum and maximum limit.
        set_joint_position(joint_index, target_angle, lower_limit, upper_limit):
            Sets a specific joint to a target angle with specified limits.
        set_multiple_joint_positions(joint_positions):
            Sets multiple joints to target angles with specified limits.
        publish_arm_position():
            Publishes the current joint angles of the robotic arm.
        reset_arm():
            Resets all joints of the robotic arm to their default positions.
    """

    def __init__(self, ros_communicator, ik_solver, num_joints = 4):
        self.ros_communicator = ros_communicator
        self.ik_solver = ik_solver
        self.num_joints = num_joints
        self.joint_pos = []
        self.set_all_joint_positions(0.0)
        

    def manual_control(self, key):
        if key == 'b': # Reset arm
            self.reset_arm(all_angle_degrees = 90.0)
        elif key == 'j':
            self.adjust_joint_angle(joint_id = 0, delta_angle = 10, min_angle=0, max_angle=180)
        elif key == 'l':
            self.adjust_joint_angle(joint_id = 0, delta_angle = -10, min_angle=0, max_angle=180)
        elif key == 'k':
            self.adjust_joint_angle(joint_id = 1, delta_angle = 10, min_angle=0, max_angle=120)
        elif key == 'i':
            self.adjust_joint_angle(joint_id = 1, delta_angle = -10, min_angle=0, max_angle=120)
        elif key == 'y':
            self.adjust_joint_angle(joint_id = 2, delta_angle = -10, min_angle=0, max_angle=150)
        elif key == 'h':
            self.adjust_joint_angle(joint_id = 2, delta_angle = 10, min_angle=0, max_angle=150)
        elif key == 'm':
            self.adjust_joint_angle(joint_id = 3, delta_angle = 10, min_angle=50, max_angle=180)
        elif key == 'n':
            self.adjust_joint_angle(joint_id = 3, delta_angle = -10, min_angle=50, max_angle=180)
        elif key == 'u':
            self.adjust_joint_angle(joint_id = 4, delta_angle = 10, min_angle=10, max_angle=70)
        elif key == 'o':
            self.adjust_joint_angle(joint_id = 4, delta_angle = -10, min_angle=10, max_angle=70)
        elif key == 'q':
            return True
        self.update_action(self.joint_pos)
        
    def auto_control(self, key=None, mode="auto_arm_control"):
        if key == "q":
            self.reset_arm(all_angle_degrees = 90.0)
            self.update_action(self.joint_pos)
            self.ik_solver.stop_simulation()
            return True
        else:
            if mode == "auto_arm_control":
                target_position = [0.3, -0.2, 0.2]
                self.ik_solver.createWorld(GUI=True)
                base_position = self.ik_solver.get_base_position()
                target_position = [
                    base_position[0] + target_position[0], 
                    base_position[1] + target_position[1], 
                    base_position[2] + target_position[2]
                ]
                self.ik_solver.setJointPosition([1.57, 1.57, 1.57, 1.57, 1.57])
                # 只取得關節角度
                # joint_angle = self.ik_solver.solveInversePositionKinematics(target_position)
                # self.update_action(joint_angle)
                # self.ik_solver.stop_simulation()

                # 取得漸進角度
                # joint_angles_in_degrees = self.ik_solver.moveTowardsTarget(target_position)
                # for i in joint_angles_in_degrees:
                #     joint_angle = self.set_all_joint_angles(i)
                #     self.update_action(joint_angle)
                #     time.sleep(0.1)

                # 隨機波動
                joint_angle_sequences = self.ik_solver.random_wave(num_moves=5, steps=50)  # 獲取隨機波動角度序列
                for joint_angles in joint_angle_sequences:
                    self.ik_solver.setJointPosition(joint_angles)
                    joint_angle = self.set_all_joint_angles(joint_angles)
                    self.update_action(joint_angle)
                    time.sleep(0.1)

            self.ik_solver.stop_simulation()
            return True


    
    def set_all_joint_angles(self, angles_degrees):
        """
        Sets all joints to the specified angles in degrees.

        Args:
            angles_degrees (list[float]): A list of angles in degrees for each joint.
        
        Example:
            >>> self.set_all_joint_angles([30, 45, 90, 60])
        """
        # 確保提供的角度數量與關節數一致
        if len(angles_degrees) != self.num_joints:
            raise ValueError("The number of angles provided does not match the number of joints.")
        
        # 將每個角度設置到對應的關節
        for i, angle in enumerate(angles_degrees):
            self.joint_pos[i] = angle
        
        # 更新機器人位置
        return self.joint_pos

        
    def update_action(self, joint_pos):
        self.ros_communicator.publish_robot_arm_angle(joint_pos)
        
    def clamp(self, value, min_value, max_value):
        """
        Clamps a value within a specified range.

        Args:
            value (float): The value to be clamped.
            min_value (float): The lower limit of the range.
            max_value (float): The upper limit of the range.

        Returns:
            float: The clamped value.

        Example:
            >>> self.clamp(5, 0, 10)
            5

            >>> self.clamp(15, 0, 10)
            10
        """
        return max(min_value, min(value, max_value))

    def set_joint_position(self, joint_index, target_angle, lower_limit, upper_limit):
        """
        Sets a specific joint to a target angle with specified limits.

        Args:
            joint_index (int): The index of the joint to update.
            target_angle (float): The target angle for the joint (in degrees).
            lower_limit (float): The lower limit for the joint's angle (in degrees).
            upper_limit (float): The upper limit for the joint's angle (in degrees).

        Example:
            Set Joint 0 to 30 degrees, within the range -90 to 90 degrees:
            >>> self.set_joint_position(0, 30, -90, 90)

            Set Joint 1 to -20 degrees, within the range -45 to 45 degrees:
            >>> self.set_joint_position(1, -20, -45, 45)
        """
        self.joint_pos[joint_index] = self.clamp(
            math.radians(target_angle),
            math.radians(lower_limit),
            math.radians(upper_limit),
        )

    def set_multiple_joint_positions(self, joint_configs):
        """
        Sets multiple joints to specific target angles.

        Args:
            joint_configs (list[dict]): A list of joint configurations, where each configuration is a dictionary containing:
                - joint_id: The index of the joint
                - angle: Target angle in degrees
                - limits: (Optional) Tuple of (min_angle, max_angle) in degrees. 
                         Defaults to (-90, 90) if not specified.

        Example:
            joint_configs = [
                {
                    "joint_id": 0,
                    "angle": 30,
                    # 使用默認限制 (-90, 90)
                },
                {
                    "joint_id": 1,
                    "angle": -20,
                    "limits": (-45, 45)    # 自定義限制
                },
                {
                    "joint_id": 2,
                    "angle": 90,
                    "limits": (0, 180)     # 自定義限制
                }
            ]
            >>> self.set_multiple_joint_positions(joint_configs)
        """
        DEFAULT_LIMITS = (-90, 90)  # 預設角度限制
        
        for config in joint_configs:
            joint_id = config["joint_id"]
            target_angle = config["angle"]
            # 如果沒有設定 limits，使用預設值
            min_angle, max_angle = config.get("limits", DEFAULT_LIMITS)
            
            self.set_joint_position(
                joint_index=joint_id,
                target_angle=target_angle,
                lower_limit=min_angle,
                upper_limit=max_angle
            )

    def set_all_joint_positions(self, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        self.joint_pos = [angle_radians] * self.num_joints
        
    def reset_arm(self, all_angle_degrees = 90.0):
        """
        Resets the robotic arm to the default position (all angles set to 0).

        This method resets the positions of all joints to their initial values, and the result can be
        published using the `publish_arm_position()` method.

        Example:
            >>> self.reset_arm()
            >>> self.publish_arm_position()
        """
        joint_configs = [
            {
                "joint_id": 0,
                "angle": 90,
            },
            {
                "joint_id": 1,
                "angle": 30,
                "limits": (-45, 45)
            },
            {
                "joint_id": 2,
                "angle": 160,
                "limits": (0, 180)
            },
            {
                "joint_id": 3,
                "angle": 180,
                "limits": (50, 180)
            },
            {
                "joint_id": 4,
                "angle": 10,
                "limits": (10, 70)
            }
        ]
        self.set_multiple_joint_positions(joint_configs)

    def adjust_joint_angle(self, joint_id, delta_angle, min_angle=-90, max_angle=90):
        """
        Adjusts a joint angle by adding or subtracting from its current position.

        Args:
            joint_id (int): The index of the joint to adjust (0-based index)
            delta_angle (float): The angle to add (positive) or subtract (negative) in degrees
            min_angle (float): Minimum allowed angle in degrees (default: -90)
            max_angle (float): Maximum allowed angle in degrees (default: 90)

        Example:
            # Increase joint 0's angle by 10 degrees with default limits (-90 to 90)
            >>> self.adjust_joint_angle(0, 10)
            
            # Decrease joint 1's angle by 5 degrees with custom limits
            >>> self.adjust_joint_angle(1, -5, min_angle=-45, max_angle=45)
            
            # Adjust joint 2 with asymmetric limits
            >>> self.adjust_joint_angle(2, 10, min_angle=0, max_angle=180)
        """
        if joint_id >= self.num_joints:
            return
        
        # 獲取當前角度（轉換為度數）
        current_angle = math.degrees(self.joint_pos[joint_id])
        
        # 計算新角度
        new_angle = current_angle + delta_angle
        
        # 更新角度
        self.set_joint_position(
            joint_index=joint_id,
            target_angle=new_angle,
            lower_limit=min_angle,
            upper_limit=max_angle
        )
