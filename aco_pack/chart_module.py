__all__ = ['show_chart']

import seaborn
import pandas as pd
import matplotlib.pyplot as plt


def show_chart(data):
    cols = ['iteration_times', 'min_distance', 'avg_distance']
    data = pd.DataFrame(data=data, columns=cols)
    # 绘制两条折线, 都以迭代次数为x轴
    # 设置为index的项将默认作为x轴
    data.set_index('iteration_times', inplace=True)
    # 设置图的大小
    plt.figure(figsize=(9, 6))
    # 折线图
    seaborn.lineplot(data=data)
    # 设置y轴的名称
    plt.ylabel('distance')
    # 设置标题
    plt.title('aco-iteration')
    plt.show()
