class ElectricField:
    def __init__(self):
        # 静态电场参数
        self.strength = 0.0
        self.direction = (1, 0)
        self.directions = {
            "x+": (1, 0),
            "x-": (-1, 0),
            "y+": (0, 1),
            "y-": (0, -1),
            "xy+": (1, 1),
            "xy-": (-1, -1)
        }
        # 时变脉冲电场参数
        self.pulse_type = "sin"  # square/sin/dc
        self.pulse_types = ["dc", "sin", "square"]
        self.pulse_freq = 2.0  # 脉冲频率
        self.pulse_amp = 1.0   # 脉冲振幅

    def set_strength(self, value):
        self.strength = value

    def set_direction(self, dir_name):
        if dir_name in self.directions:
            self.direction = self.directions[dir_name]

    def set_pulse_type(self, p_type):
        if p_type in self.pulse_types:
            self.pulse_type = p_type

    def set_pulse_freq(self, freq):
        self.pulse_freq = freq

    def set_pulse_amp(self, amp):
        self.pulse_amp = amp

    def get_params(self):
        """返回所有电场参数"""
        return (self.strength, self.direction, self.pulse_type, 
                self.pulse_freq, self.pulse_amp)