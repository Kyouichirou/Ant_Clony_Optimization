__all__ = ['travel_start']
__version__ = 1.0
__author__ = 'HLA'
__homepage__ = 'https://github.com/Kyouichirou'
__license__ = 'MIT'

from .tsp_module import TSP
from .simulation_module import simulation_city_data


def travel_start(city_num=50, max_iter=300):
    # 演示窗体的大小
    window_width = 1200
    window_height = 900
    # 获取模拟的城市坐标
    sim_cities = simulation_city_data(city_num=city_num,
                                      max_index=int(window_width * 0.95),
                                      limit_h=int(window_height * 0.95)
                                      )
    tsp = TSP(sim_cities, max_iter)
    tsp.show_main_window(width=window_width, height=window_height)
