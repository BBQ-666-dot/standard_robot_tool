import matplotlib
matplotlib.use("Agg")
import matplotlib.axes as maxes


class RealTimePlot_2D():
    def __init__(self, ax:maxes.Axes):
        self.ax = ax
        self.title = ''
        self.x_label = ''
        self.y_label = ''

    def UpdatePlot(self,x_axis_data:list,y_axis_data:list,y_labels:list) -> None:
        '''
        绘制图像函数:
        x_axis_data: x轴数据
        y_axis_data: y轴数据列表([y1,y2,y3,...]),包含多个曲线图y轴数据，每个y代表一个曲线图的y轴数据
        y_labels: 每个曲线图的名称列表，数量和y_axis_data一致
        '''
        self.ax.cla()
        for i,y in enumerate(y_axis_data):
            self.ax.plot(x_axis_data, y, label=y_labels[i])
        
        self.ax.set_title(self.title, fontsize=10)  # 添加标题
        self.ax.set_xlabel(self.x_label, fontsize=10)  # 添加X轴标签
        self.ax.set_ylabel(self.y_label, fontsize=10)  # 添加Y轴标签
        self.ax.legend(loc='upper right')  # 添加图例
        self.ax.grid(True)  # 添加网格线
        return None



class RealTimeGraph_3D:
    def __init__(self, ax:maxes.Axes):
        self.ax = ax
    
    def UpdatePlot(self, ax_rotated:dict) -> None:
        self.ax.cla()
        # 绘制初始姿态方向轴
        self.ax.quiver(0, 0, 0, 1, 0, 0, color='r', length=1, normalize=True, alpha=0.5)  # X轴
        self.ax.quiver(0, 0, 0, 0, 1, 0, color='g', length=1, normalize=True, alpha=0.5)  # Y轴
        self.ax.quiver(0, 0, 0, 0, 0, 1, color='b', length=1, normalize=True, alpha=0.5)  # Z轴
        
        # 绘制姿态方向轴
        x_rotated = ax_rotated['x']
        y_rotated = ax_rotated['y']
        z_rotated = ax_rotated['z']
        self.ax.quiver(0, 0, 0, x_rotated[0], x_rotated[1], x_rotated[2], color='r', length=1.5, normalize=True)  # X轴
        self.ax.quiver(0, 0, 0, y_rotated[0], y_rotated[1], y_rotated[2], color='g', length=1.5, normalize=True)  # Y轴
        self.ax.quiver(0, 0, 0, z_rotated[0], z_rotated[1], z_rotated[2], color='b', length=1.5, normalize=True)  # Z轴
        
        # # 绘制初始姿态方向轴
        # self.ax.plot([0, 1], [0, 0], [0, 0], color='r', alpha=0.5)  # X轴
        # self.ax.plot([0, 0], [0, 1], [0, 0], color='g', alpha=0.5)  # Y轴
        # self.ax.plot([0, 0], [0, 0], [0, 1], color='b', alpha=0.5)  # Z轴
        
        # # 绘制姿态方向轴
        # x_rotated = ax_rotated['x']
        # y_rotated = ax_rotated['y']
        # z_rotated = ax_rotated['z']
        # self.ax.plot([0, x_rotated[0]], [0, x_rotated[1]], [0, x_rotated[2]], color='r')  # X轴
        # self.ax.plot([0, y_rotated[0]], [0, y_rotated[1]], [0, y_rotated[2]], color='g')  # Y轴
        # self.ax.plot([0, z_rotated[0]], [0, z_rotated[1]], [0, z_rotated[2]], color='b')  # Z轴
        
        # 设置坐标轴范围
        self.ax.set_xlim([-1, 1])
        self.ax.set_ylim([-1, 1])
        self.ax.set_zlim([-1, 1])
        
        self.ax.set_title("IMU Pos", fontsize=10)  # 添加标题
        