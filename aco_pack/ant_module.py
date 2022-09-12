__all__ = ['Ant']

import random
from .constants_module import ALPHA, BETA


# @description: 蚂蚁模块

class Ant:
    def __init__(self, ant_id: int, city_num: int, pheromone_graph, distance_graph):
        # 蚂蚁的id
        self._ant_id = ant_id
        # 移动次数
        self._move_count = 0
        # 总距离
        self.total_distance = 0
        # 当前城市
        self._current_city = 0
        #  城市数量
        self._city_num = city_num
        # 城市距离图
        self._distance_graph = distance_graph
        # 信息素分布图
        self._pheromone_graph = pheromone_graph
        # 已访问路径
        self.visited_path = None
        # 访问的城市的状态
        self._visited_cities_state = None
        self._initial()

    # 初始数据
    def _initial(self):
        # 蚂蚁访问的路径
        self.visited_path = []
        # 当前路径的总距离
        self.total_distance = 0
        # 探索城市的状态, 初始化, 全部设置为False, 全部没有访问过
        self._visited_cities_state = [False] * self._city_num
        # 随机初始化出发的城市
        first_index = random.randint(0, self._city_num - 1)
        # 当前城市
        self._current_city = first_index
        self.visited_path.append(first_index)
        # 将出发的城市标记为访问过
        self._visited_cities_state[first_index] = True
        self._move_count = 1

    # 轮盘(关键部分)
    def _roulette_wheel_selection(self, total_prob, selected_city_prob) -> int:
        # 轮盘赌法跳出没有访问过的城市
        # https://zhuanlan.zhihu.com/p/140418005
        # 产生一个随机概率,0.0 - total_prob
        # 各个个体的选择概率和其适应度值成比例, 适应度越大, 选中概率也越大
        tmp_prob = random.uniform(0.0, total_prob)
        for i in range(self._city_num):
            # 没有访问过的城市
            if not self._visited_cities_state[i]:
                # 轮次相减
                tmp_prob -= selected_city_prob[i]
                if tmp_prob < 0.0:
                    return i
        return -1

    # 选择下一个城市(关键部分)
    def _get_next_city(self) -> int:
        next_city = -1
        # 存储去下个城市的概率
        selected_city_prob = [0.0] * self._city_num
        # 获取去下一个城市的概率
        for i in range(self._city_num):
            if not self._visited_cities_state[i]:
                try:
                    # 计算概率: 与信息素浓度成正比(越多的蚂蚁访问, 则优先访问该路径), 与距离成反比
                    # 启发函数ETA = 1 / distance
                    x = self._distance_graph[self._current_city][i]
                    selected_city_prob[i] = pow(self._pheromone_graph[self._current_city][i], ALPHA) * pow(
                        (1.0 / x), BETA)
                except ZeroDivisionError:
                    print(
                        f'warning, error on ant_id: {self._ant_id}; '
                        f'current city: {self._current_city}; city_index: {i}'
                    )
                    self.error_flag = True
                    return -1
        total_prob = sum(selected_city_prob)
        if total_prob > 0.0:
            next_city = self._roulette_wheel_selection(total_prob, selected_city_prob)
        # 假如没有取得下一城市
        if next_city == -1:
            # 随机生成的下一个城市的
            next_city = random.randint(0, self._city_num - 1)
            # 找出没有访问过的城市
            while self._visited_cities_state[next_city]:
                next_city = random.randint(0, self._city_num - 1)
        # 返回下一个城市序号
        return next_city

    # 计算路径总距离(关键部分)
    def _cal_total_distance(self):
        tmp_distance = 0.0
        start = 0
        for i in range(1, self._city_num):
            start, end = self.visited_path[i], self.visited_path[i - 1]
            tmp_distance += self._distance_graph[start][end]
        # 回程
        end = self.visited_path[0]
        tmp_distance += self._distance_graph[start][end]
        self.total_distance = tmp_distance

    # 移动
    def _move(self, next_city: int):
        self.visited_path.append(next_city)
        self._visited_cities_state[next_city] = True
        self.total_distance += self._distance_graph[self._current_city][next_city]
        self._current_city = next_city
        self._move_count += 1

    # 搜索路径
    def search_path(self) -> bool:
        # 初始化数据
        self._initial()
        # 搜素路径，遍历完所有城市为止
        while self._move_count < self._city_num:
            # 移动到下一个城市
            next_city = self._get_next_city()
            if next_city < 0:
                return False
            self._move(next_city)
        # 计算路径总长度
        self._cal_total_distance()
        return True
