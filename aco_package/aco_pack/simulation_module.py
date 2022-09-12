__all__ = ['simulation_city_data']

import random
import numpy as np


def simulation_city_data(city_num: int, max_index: int, limit_h: int, min_index=40):
    sim_cities = np.random.randint(min_index, max_index, size=(city_num, 2))
    # 窗体的height=600, 需要y轴的坐标小于600
    for sc in sim_cities:
        if sc[1] > limit_h:
            sc[1] = random.randint(min_index, limit_h)
    return sim_cities
