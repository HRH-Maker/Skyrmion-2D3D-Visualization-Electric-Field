import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class SkyrmionPlotter:
    def __init__(self, skyrmion_model, electric_field):
        self.model = skyrmion_model
        self.field = electric_field
        self.fig = plt.figure(figsize=(18, 10))
        plt.subplots_adjust(left=0.1, bottom=0.4, right=0.9, top=0.9)

        # 子图1：仅自旋箭头
        self.ax2d = self.fig.add_subplot(121)
        # 子图2：3D自旋分布
        self.ax3d = self.fig.add_subplot(122, projection='3d')

        # 初始计算
        self.e_params = self.field.get_params()
        self.Sx, self.Sy, self.Sz = self.model.calculate_spin(self.e_params)
        self.dynamics = self.model.get_dynamics()

        # ---------------------- 2D图：仅自旋箭头 ----------------------
        self.ax2d.set_xlim(-5, 105)
        self.ax2d.set_ylim(-5, 105)
        self.ax2d.set_aspect('equal')
        self.ax2d.set_xlabel('X (nm)')
        self.ax2d.set_ylabel('Y (nm)')
        self.ax2d.set_title('Spin Arrow Distribution (Nael Skyrmion)')

        # 自旋箭头
        step = 4
        X_arrow = self.model.X[::step, ::step]
        Y_arrow = self.model.Y[::step, ::step]
        Sx_arrow = self.Sx[::step, ::step]
        Sy_arrow = self.Sy[::step, ::step]

        # 生成RGB颜色
        angles = np.arctan2(Sy_arrow, Sx_arrow)
        norm = plt.Normalize(angles.min(), angles.max())
        self.colors = plt.cm.hsv(norm(angles))[:, :, :3]

        # 绘制自旋箭头
        self.quiver = self.ax2d.quiver(
            X_arrow, Y_arrow,
            Sx_arrow, Sy_arrow,
            color=self.colors.reshape(-1, 3),
            scale=20,
            width=0.002,
            headwidth=5,
            headlength=6
        )

        # 轨迹线
        self.trajectory_plot = self.ax2d.plot(
            [], [], 'ro-', markersize=2, linewidth=1, label='Trajectory'
        )[0]
        self.ax2d.legend(loc='upper right')

        # ---------------------- 控件区域 ----------------------
        # 1. 电场强度滑块
        ax_strength = plt.axes([0.1, 0.32, 0.75, 0.03])
        self.slider_strength = Slider(
            ax=ax_strength, label='E-Field Strength (0~2)',
            valmin=0, valmax=2, valinit=0
        )

        # 2. 脉冲频率滑块
        ax_freq = plt.axes([0.1, 0.28, 0.75, 0.03])
        self.slider_freq = Slider(
            ax=ax_freq, label='Pulse Frequency (0~5 Hz)',
            valmin=0, valmax=5, valinit=self.field.pulse_freq
        )

        # 3. 脉冲振幅滑块
        ax_amp = plt.axes([0.1, 0.24, 0.75, 0.03])
        self.slider_amp = Slider(
            ax=ax_amp, label='Pulse Amplitude (0~2)',
            valmin=0, valmax=2, valinit=self.field.pulse_amp
        )

        # 4. 电场方向选择器
        ax_dir = plt.axes([0.1, 0.12, 0.15, 0.1])
        self.radio_dir = RadioButtons(
            ax=ax_dir, labels=list(self.field.directions.keys()), active=0
        )

        # 5. 脉冲类型选择器
        ax_pulse = plt.axes([0.3, 0.12, 0.15, 0.1])
        self.radio_pulse = RadioButtons(
            ax=ax_pulse, labels=self.field.pulse_types, active=1
        )

        # 6. 重置按钮
        ax_reset = plt.axes([0.5, 0.12, 0.1, 0.05])
        self.btn_reset = Button(ax_reset, 'Reset Time', color='lightgoldenrodyellow', 
                                hovercolor='0.975')

        # ---------------------- 绑定事件 ----------------------
        self.slider_strength.on_changed(self.update_params)
        self.slider_freq.on_changed(self.update_params)
        self.slider_amp.on_changed(self.update_params)
        self.radio_dir.on_clicked(self.update_direction)
        self.radio_pulse.on_clicked(self.update_pulse_type)
        self.btn_reset.on_clicked(self.reset_simulation)

        # 3D图初始化
        self.update_3d()

        # 启动动画
        self.animate()
        plt.show()

    # ---------------------- 补全缺失的方法 ----------------------
    def update_params(self, val):
        """更新电场参数"""
        self.field.set_strength(self.slider_strength.val)
        self.field.set_pulse_freq(self.slider_freq.val)
        self.field.set_pulse_amp(self.slider_amp.val)
        self.e_params = self.field.get_params()

    def update_direction(self, label):
        """更新电场方向"""
        self.field.set_direction(label)
        self.update_params(0)

    def update_pulse_type(self, label):
        """更新脉冲类型"""
        self.field.set_pulse_type(label)
        self.update_params(0)

    def reset_simulation(self, event):
        """重置模拟时间和轨迹"""
        self.model.reset_time()
        self.trajectory_plot.set_data([], [])
        self.ax2d.set_title('Spin Arrows | Reset Complete')

    def update_3d(self):
        """更新3D自旋图"""
        self.ax3d.clear()
        step = 5
        X, Y = self.model.X[::step, ::step], self.model.Y[::step, ::step]
        self.ax3d.quiver(
            X, Y, np.zeros_like(X),
            self.Sx[::step, ::step], self.Sy[::step, ::step], self.Sz[::step, ::step],
            color='blue', length=0.6, normalize=True
        )
        self.ax3d.set_xlabel('X (nm)')
        self.ax3d.set_ylabel('Y (nm)')
        self.ax3d.set_zlabel('Sz')
        self.ax3d.set_zlim(-1, 1)
        self.ax3d.view_init(elev=30, azim=45)
        self.ax3d.set_title(
            f'3D Spin | Pulse Type: {self.field.pulse_type} | '
            f'Freq: {self.field.pulse_freq:.1f}Hz'
        )

    def animate(self):
        """动画循环"""
        self.Sx, self.Sy, self.Sz = self.model.calculate_spin(self.e_params)
        self.dynamics = self.model.get_dynamics()

        # 更新2D自旋箭头
        step = 4
        X_arrow = self.model.X[::step, ::step]
        Y_arrow = self.model.Y[::step, ::step]
        Sx_arrow = self.Sx[::step, ::step]
        Sy_arrow = self.Sy[::step, ::step]

        # 更新颜色
        angles = np.arctan2(Sy_arrow, Sx_arrow)
        norm = plt.Normalize(angles.min(), angles.max())
        self.colors = plt.cm.hsv(norm(angles))[:, :, :3]
        self.quiver.set_UVC(Sx_arrow, Sy_arrow)
        self.quiver.set_color(self.colors.reshape(-1, 3))

        # 更新轨迹
        traj = self.dynamics["trajectory"]
        self.trajectory_plot.set_data(traj[:, 0], traj[:, 1])
        self.ax2d.set_title(
            f'Spin Arrows | Time: {self.dynamics["time"]:.2f}s | Center: {self.dynamics["center"].round(1)}'
        )

        # 更新3D图
        self.update_3d()

        self.fig.canvas.draw_idle()
        plt.pause(0.03)
        self.animate()