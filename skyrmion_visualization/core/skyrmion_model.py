import numpy as np

class NaelSkyrmion:
    def __init__(self, grid_size=100, skyrmion_radius=6, center=(50, 50), DMI=0.8):
        self.grid_size = grid_size
        self.r0 = skyrmion_radius
        self.center = np.array(center)
        self.DMI = DMI
        self.x = np.linspace(0, grid_size-1, grid_size)
        self.y = np.linspace(0, grid_size-1, grid_size)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        self.trajectory = [self.center.copy()]
        self.velocity = np.array([0.0, 0.0])
        self.rotation_freq = 0.0
        self.time = 0.0  # 时间变量，用于时变电场

    def calculate_spin(self, e_field_params):
        """
        计算自旋分布（支持时变电场）
        :param e_field_params: 电场参数 (strength, direction, pulse_type, pulse_freq, pulse_amp)
        """
        strength, direction, pulse_type, pulse_freq, pulse_amp = e_field_params
        self.time += 0.01  # 时间步长

        # 时变脉冲电场计算
        if pulse_type == "square":  # 方波脉冲
            e_t = strength * pulse_amp * np.sign(np.sin(pulse_freq * self.time))
        elif pulse_type == "sin":  # 正弦脉冲
            e_t = strength * pulse_amp * np.sin(pulse_freq * self.time)
        else:  # 直流（无脉冲）
            e_t = strength

        # 电场诱导的位移（放大系数30，效果显著）
        dx = e_t * direction[0] * 30
        dy = e_t * direction[1] * 30
        self.center = np.array([50, 50]) + np.array([dx, dy])
        self.trajectory.append(self.center.copy())
        if len(self.trajectory) > 50:  # 保留最近50个轨迹点
            self.trajectory.pop(0)

        # 极坐标计算
        r = np.sqrt((self.X - self.center[0])**2 + (self.Y - self.center[1])**2)
        theta = np.arctan2(self.Y - self.center[1], self.X - self.center[0])

        # 电场诱导的自旋旋转（角度放大到4π）
        rotate_angle = e_t * 4 * np.pi
        r_deformed = r * (1 + e_t * 0.5 * np.cos(theta))  # 形变

        # 奈尔型自旋分布
        Sz = -np.tanh((r_deformed - self.r0) / 1.0)
        Sx = np.sin(theta + rotate_angle) * np.sqrt(1 - Sz**2)
        Sy = -np.cos(theta + rotate_angle) * np.sqrt(1 - Sz**2)

        # 动力学参数
        self.velocity = np.array([dx, dy]) * 0.8
        self.rotation_freq = e_t * self.DMI * 20

        # 归一化
        norm = np.sqrt(Sx**2 + Sy**2 + Sz**2)
        return Sx/norm, Sy/norm, Sz/norm

    def get_dynamics(self):
        return {
            "center": self.center,
            "velocity": self.velocity,
            "rotation_freq": self.rotation_freq,
            "trajectory": np.array(self.trajectory),
            "time": self.time
        }

    def reset_time(self):
        """重置时间（重新开始脉冲）"""
        self.time = 0.0
        self.trajectory = [self.center.copy()]