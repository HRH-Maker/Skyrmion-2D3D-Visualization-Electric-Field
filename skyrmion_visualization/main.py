from core.skyrmion_model import NaelSkyrmion
from core.electric_field import ElectricField
from visualization.plotter import SkyrmionPlotter

def main():
    # 初始化斯格明子模型
    skyrmion = NaelSkyrmion(
        grid_size=100,
        skyrmion_radius=6,
        center=(50, 50),
        DMI=0.8
    )
    
    # 初始化电场调控器
    e_field = ElectricField()
    
    # 初始化可视化（自动启动动画）
    plotter = SkyrmionPlotter(skyrmion, e_field)

if __name__ == "__main__":
    main()