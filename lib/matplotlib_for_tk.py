import matplotlib
matplotlib.use("Agg")
import matplotlib.axes as maxes
import matplotlib.pyplot as plt
import numpy as np

import theme

# 中文字体
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


def _style_2d(ax:maxes.Axes) -> None:
    '''2D 深色样式'''
    ax.set_facecolor(theme.CARD)
    for spine in ax.spines.values():
        spine.set_color(theme.BORDER)
    ax.tick_params(colors=theme.FG_DIM, labelsize=8)
    ax.grid(True, color=theme.BORDER, alpha=0.45, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.title.set_color(theme.FG)


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
        _style_2d(self.ax)

        if len(x_axis_data) == 0:
            # 没有数据时显示提示
            self.ax.text(0.5, 0.5, "等待数据 / Waiting for data",
                         transform=self.ax.transAxes, ha="center", va="center",
                         color=theme.FG_DIM, fontsize=12)
        else:
            for i, y in enumerate(y_axis_data):
                color = theme.LINE_COLORS[i % len(theme.LINE_COLORS)]
                label = y_labels[i] if i < len(y_labels) else ''
                self.ax.plot(x_axis_data, y, label=label, color=color,
                             linewidth=1.4)
            if len(y_labels) > 0:
                legend = self.ax.legend(loc='upper right', fontsize=8,
                                        facecolor=theme.CARD_HI,
                                        edgecolor=theme.BORDER,
                                        framealpha=0.95)
                legend.get_frame().set_facecolor(theme.CARD_HI)
                legend.get_frame().set_edgecolor(theme.BORDER)
                legend.get_frame().set_alpha(0.95)
                for text in legend.get_texts():
                    text.set_color(theme.FG)

        self.ax.set_title(self.title, fontsize=10, pad=6)  # 添加标题
        self.ax.set_xlabel(self.x_label, fontsize=9, color=theme.FG_DIM)  # 添加X轴标签
        self.ax.set_ylabel(self.y_label, fontsize=9, color=theme.FG_DIM)  # 添加Y轴标签
        return None


class RealTimeGraph_3D:
    def __init__(self, ax:maxes.Axes):
        self.ax = ax

    def UpdatePlot(self, ax_rotated:dict) -> None:
        ax = self.ax
        ax.cla()
        ax.set_facecolor(theme.CARD)
        ax.set_axis_off()

        # 参考球面圈
        t = np.linspace(0, 2 * np.pi, 72)
        c, s, z = np.cos(t), np.sin(t), np.zeros_like(t)
        for xs, ys, zs in ((c, s, z), (c, z, s), (z, c, s)):
            ax.plot(xs, ys, zs, color=theme.BORDER, linewidth=0.7, alpha=0.8)

        # 世界参考轴(虚线)
        lim = 1.25
        for i in range(3):
            vec = [0.0, 0.0, 0.0]
            vec[i] = lim
            ax.plot((-vec[0], vec[0]), (-vec[1], vec[1]), (-vec[2], vec[2]),
                    color=theme.BORDER, linewidth=0.7, linestyle="--", alpha=0.7)

        # 姿态坐标轴
        colors = {"x": "#ff6b6b", "y": "#51cf66", "z": "#4dabf7"}
        for key in ("x", "y", "z"):
            v = ax_rotated[key]
            ax.quiver(0, 0, 0, v[0], v[1], v[2], color=colors[key],
                      linewidth=2.2, arrow_length_ratio=0.16)

        # 设置坐标轴范围
        ax.set_xlim([-1.15, 1.15])
        ax.set_ylim([-1.15, 1.15])
        ax.set_zlim([-1.15, 1.15])
        try:
            ax.set_box_aspect((1, 1, 1))
        except Exception:
            pass
        ax.view_init(elev=22, azim=-58)

        ax.set_title("IMU 姿态", fontsize=10, color=theme.FG, pad=-2)
