__all__ = ['TSP']

import os
import sys
import math
import pprint
import ctypes
import threading
import numpy as np
import tkinter as tk
from functools import reduce
from .ant_module import Ant
from .constants_module import RHO, Q
from .chart_module import show_chart


# @description: 旅行商问题的蚁群算法处理


class TSP:
    def __init__(self, sim_cities, iter_max: int):
        # 配置参数
        self._city_num = len(sim_cities)
        # 蚂蚁数设置为城市数的1.5倍
        self._ant_num = int(1.5 * self._city_num)
        # 模拟城市坐标
        self._sim_cities = sim_cities
        # 信息素矩阵
        self._pheromone_graph = None
        # 城市间距离矩阵
        self._distance_graph = np.ones((self._city_num, self._city_num))
        # 绘制图表的圆点大小
        self._radius = 5
        # 绘制路径发生变化次数
        self._path_draw_times = 0
        # 最佳路径
        self._best_path = None
        # tkinter窗体
        self._window = None
        # 用于控制最小距离的获取, 设置一个非常大的数
        self._min_distance = 0
        # 累计迭代次数
        self._iter_times = 0
        # 迭代了多少次后仍无法获取到更小的值
        self._iter_max = iter_max
        self._iter_max_times = iter_max
        # 控制执行
        self._is_running = False
        # 注意和Lock(同步锁的差异), lock是阻塞型的锁
        self._lock = threading.RLock()
        # 节点坐标
        self._nodes_coordinate = None
        # 蚂蚁群
        self._ant_objs = None
        # 计算城市之间的距离
        self._cal_distance_all_cities()
        # 每次绘制都变换线条颜色
        self._lines_color = (
            '#000000',
            '#0000FF',
            '#00CD00',
            '#9A32CD',
            '#FFC125',
            '#FF6A6A',
            '#B03060'
        )
        # 迭代次数-最小距离绘图
        self._chart_data = None
        # 迭代完成
        self._iter_finished = False

    def _cal_distance_all_cities(self):
        for i in range(self._city_num):
            for j in range(self._city_num):
                # 城市距离, 三角函数 a ^ 2 + b ^ 2 = c ^ 2, d = c ^ 1/2
                # power(data, 次幂) == **符号, 如果输出结果是整数, 则是整数
                # math.power(), 默认转为浮点数, 不管结果是否为整数
                tmp_distance = math.sqrt((self._sim_cities[i][0] - self._sim_cities[j][0]) ** 2 + (
                        self._sim_cities[i][1] - self._sim_cities[j][1]) ** 2)
                self._distance_graph[i][j] = tmp_distance

    # 调整窗体的内容
    # 更改标题
    def _set_title(self, s):
        self._window.title(s)

    # 将节点按order顺序连线
    def _draw_line(self, order_paths):
        # 删除所有的线条
        # Delete each of the items given by the first (and only) value of args (this should be an item id or tag).
        self._canvas.delete("line")
        '''
        def test(x, y) :            
            print(str(x) + '-' + str(y))
            return y

        reduce(test, [1,2,3,4,5], 5)
        打印内容:
            5-1
            1-2
            2-3
            3-4
            4-5
        通过reduce的方式, 实现各个城市坐标的绘制
        '''
        # 每次绘制图都采用不一样的颜色, 方便查看图的变化
        color = self._lines_color[self._path_draw_times % len(self._lines_color)]

        def _draw(index_a, index_b):
            node_a, node_b = self._nodes_coordinate[index_a], self._nodes_coordinate[index_b]
            # Draw a line. Returns the item id.
            # https://tkdocs.com/shipman/create_line.html
            self._canvas.create_line(node_a,
                                     node_b,
                                     # 颜色
                                     fill=color,
                                     # 类型
                                     tags="line"
                                     )
            return index_b

        # reduce(func, iter_objs, initial_value)
        reduce(_draw, order_paths, order_paths[-1])
        # 更新画布
        self._canvas.update()

    # 清除画布
    def _clear_canvas(self):
        for item in self._canvas.find_all():
            self._canvas.delete(item)

    def _draw_coordinate(self):
        # 在画布上随机初始坐标
        # 生成节点圆，半径为self._radius
        # https://blog.csdn.net/dhjabc_1/article/details/105449496
        # 注意绘制的坐标的位置y轴反方向的, 因为tkinker的坐标轴的中心是在屏幕的左上角, 所以Y轴是向下的
        self._nodes_coordinate = []
        for city in self._sim_cities:
            x, y = city
            # 保存各个城市的位置坐标 -> 用于后续的路线的绘制
            # canvas.create_line() 不支持numpy.array数据类型, 转为常规的元组坐标
            self._nodes_coordinate.append((x, y))
            self._canvas.create_oval(x - self._radius,
                                     y - self._radius,
                                     x + self._radius,
                                     y + self._radius,
                                     fill="#ffd700",
                                     outline="#000000",
                                     tags="node"
                                     )
            self._canvas.create_text(x, y - 10, text=f'({x}, {y})', fill='black')

    # 改变执行的状态
    def _change_running_state(self, mode: bool):
        self._lock.acquire()
        self._is_running = mode
        self._lock.release()

    # 初始化
    def _initial(self, event):
        print('aco init')
        self._change_running_state(False)
        # 清除掉当前画布的内容
        self._clear_canvas()
        # 绘制初始化各个城市的坐标
        self._draw_coordinate()
        # 初始化城市之间的信息素
        self._pheromone_graph = np.ones((self._city_num, self._city_num))
        # 初始化蚁群
        self._ant_objs = [Ant(index, self._city_num, self._pheromone_graph, self._distance_graph) for index in
                          range(self._ant_num)]
        # 初始化迭代次数, 绘制路径次数, 迭代次数, 最小距离
        self._iter_times = 1
        self._path_draw_times = 1
        self._min_distance = 1 << 31
        self._iter_max = self._iter_max_times
        self._chart_data = []
        self._iter_finished = False

    # 退出程序
    def _quit(self, event):
        self._change_running_state(False)
        self._window.destroy()
        print("aco exit")
        sys.exit()

    # 停止搜索
    def _pause(self, event):
        print('aco pause')
        self._change_running_state(False)

    def _ant_action(self):
        while self._is_running:
            # 蚁群爬行
            is_need_draw = False
            avg_dis = []
            for ant in self._ant_objs:
                # 搜索其中的一条路径
                if not ant.search_path():
                    # 假如在爬行中出现错误
                    return
                # 爬完, 获取蚂蚁走过的路径
                dis = ant.total_distance
                avg_dis.append(dis)
                # 对比每次的路径的变化
                if dis < self._min_distance:
                    is_need_draw = True
                    self._min_distance = dis
                    # 将路径deep_copy到最佳路径保存, 不是直接"="
                    self._best_path = [e for e in ant.visited_path]
            self._chart_data.append((self._iter_times, self._min_distance, np.mean(avg_dis)))
            print(
                f"iter times：{self._iter_times}; "
                f"current best distance：{self._min_distance}; "
                f"current max_iter: {self._iter_max}")
            # 重新绘制新的线路图
            title = f"tsp-aco:, iter times: {self._iter_times}; " \
                    f"current best distance：{self._min_distance}; " \
                    f"current max_iter: {self._iter_max}"
            if is_need_draw:
                self._draw_line(self._best_path)
                title = title + f'; draw times: {self._path_draw_times}'
                self._path_draw_times += 1
                self._iter_max = self._iter_max_times
            else:
                # 阈值, 当最小值一直没有更小的值出现, 迭代300次后退出迭代
                self._iter_max -= 1
                if self._iter_max == 0:
                    print(f'the best path, {self._min_distance}:\n' + '->'.join(
                        str(e) for e in self._best_path) + '\ncities coordinate:\n')
                    self._set_title(
                        f'TSP-ACO Demo: iteration has finished, '
                        f'the best distance: {self._min_distance}(draw times:{self._path_draw_times});'
                        f' iter times: {self._iter_times}')
                    pprint.pprint(self._sim_cities)
                    self._iter_finished = True
                    return
            # 爬行完一次后, 更新信息素
            self._update_pheromone_graph()
            # 设置标题
            self._set_title(title)
            self._iter_times += 1
        else:
            self._set_title('ant has paused')

    # 开始搜索(关键部分)
    def _search_path(self, event):
        # 开启线程
        # 关键节点, 这里在多模块调用执行, 如果不单独开启线程, tkinter界面会出现卡死的问题
        if not self._is_running:
            print('aco start')
            self._change_running_state(True)
            th = threading.Thread(target=self._ant_action)
            # 线程守护, 主程序退出, 子线程同时退出
            th.daemon = True
            th.start()

    # 更新信息素(关键部分)
    def _update_pheromone_graph(self):
        # 获取每只蚂蚁在其路径上留下的信息素
        # 初始的信息素的分布设置为 1, 这里的设置不能为1, 因为信息素的分布已经发生改变, 临时的变量存储需要初始为0
        tmp_pheromone = np.zeros((self._city_num, self._city_num))
        for ant in self._ant_objs:
            for i in range(1, self._city_num):
                start, end = ant.visited_path[i - 1], ant.visited_path[i]
                # 在路径上的每两个相邻城市间留下信息素，与路径总距离反比, 距离越远, 信息素浓度越低
                tmp_pheromone[start][end] += Q / ant.total_distance
                tmp_pheromone[end][start] = tmp_pheromone[start][end]
        # 更新全部城市路径信息浓度的分布
        self._pheromone_graph = self._pheromone_graph * RHO + tmp_pheromone
        for ant in self._ant_objs:
            ant.ant_pheromone = self._pheromone_graph

    def _canvas_init(self, width, height):
        # 初始化tk画布
        # http://c.biancheng.net/tkinter/canvas-widget.html
        # https://tkinter-docs.readthedocs.io/en/latest/widgets/canvas.html
        self._canvas = tk.Canvas(
            self._window,
            width=width,
            height=height,
            bg="#EBEBEB",
            xscrollincrement=1,
            yscrollincrement=1
        )
        self._canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self._set_title("TSP-ACO Demo_@HLA, GitHub: https://github.com/Kyouichirou")
        # 设置底部的状态栏
        statusbar = tk.Label(self._window,
                             text=">>> i:init; s:start; p:pause; q:quit; c: show chart",
                             bd=1,
                             relief=tk.SUNKEN,
                             anchor=tk.W
                             )
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        print('canvas init')

    def _show_iteration(self, event):
        if self._iter_finished and self._chart_data:
            show_chart(self._chart_data)

    def _bind_events(self):
        # 绑定键盘事件
        # 注意这里: 涉及到线程的问题
        # 注意和如上提及的搜索路径中的线程, 之间的关系
        # 假如在if __name__ 下(同一文件下), 执行程序, 不会受到任何的影响, 但是在多模块下执行有问题, bind_event会导致程序出现卡死的问题, 不管用lock还是rlock
        # 回调函数, 返回一个event
        # ------------------------- #
        # 退出
        self._window.bind("q", self._quit)
        # 初始化
        self._window.bind("i", self._initial)
        # 开始
        self._window.bind("s", self._search_path)
        # 暂停
        self._window.bind("p", self._pause)
        # 显示迭代的图
        self._window.bind('c', self._show_iteration)

    # 窗体居中显示
    def _center_window(self, width: int, height: int):
        screenwidth = self._window.winfo_screenwidth()
        screenheight = self._window.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self._window.geometry(size)
        self._window.update()

    # tk窗体
    def show_main_window(self, width: int, height: int):
        ant_app_id = "ant_aco_tsp"
        self._window = tk.Tk()
        #  设置展示的程序图标, 任务栏 & 程序界面
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ant_app_id)
        ico_path = os.getcwd() + r'\aco_pack\ant.ico'
        self._window.wm_iconbitmap(ico_path)
        # 画布初始化
        self._canvas_init(width, height)
        # 初始化
        self._bind_events()
        self._initial(None)
        # 禁止窗体调节缩放
        self._window.minsize(width=width + 10, height=height + 10)
        self._window.maxsize(width=width + 25, height=height + 25)
        # 调节窗体出现在屏幕的位置
        self._center_window(int(width * 1.2), int(height * 1.1))
        self._window.mainloop()
