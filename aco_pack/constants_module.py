# constant
# 参考a: https://zhuanlan.zhihu.com/p/137408401
# 参考b: https://www.cnblogs.com/zhaoke271828/p/14585443.html
# 参考c: https://zhuanlan.zhihu.com/p/140418005
# 参考d: https://codeleading.com/article/54156353979/
# 参考c: https://www.cnblogs.com/bokeyuancj/p/11798635.html
# 参考e: https://blog.csdn.net/zuochao_2013/article/details/71872950
# 涉及关键问题, 如何确定参数的最优(较优)值?

# 启发函数重要程度因子, 0-5
BETA = 2.0
# 信息素重要程度因子, 0-5
ALPHA = 1.0
# 信息素, 10-1000
Q = 100.0
# 挥发系数, 0.1-0.99
RHO = 0.5
