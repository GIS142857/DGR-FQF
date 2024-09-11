from math import pi
import numpy as np
from scipy import integrate
import math
import inspect
from scipy.stats import gamma
from net_config import *


def calculate_interference_distance(transmitting_power_dBm, frequency_Hz, gain_t, gain_r, interference_threshold_W):
    # 常量定义
    c = 3e8  # 光速，米/秒
    dBm_to_W = lambda dBm: 10 ** (dBm / 10)
    print(dBm_to_W(12))
    # 计算发射功率（瓦特）
    transmitting_power_W = dBm_to_W(transmitting_power_dBm)

    # 计算波长（米）
    wavelength = c / frequency_Hz

    # 计算干扰距离（米）
    distance = (wavelength / (4 * math.pi)) * math.sqrt(
        (transmitting_power_W * gain_t * gain_r) / interference_threshold_W)

    return distance


# print(calculate_interference_distance(TRANSMITTING_POWER, FREQUENCY, GAIN_T, GAIN_R, INTERFERENCE_THRESHOLD))


def distance(pos1, pos2):
    sum = 0
    for i in range(len(pos1)):
        sum += (pos1[i] - pos2[i]) ** 2
    return sum ** 0.5


def ensure_generator(env, func, *args, **kwargs):
    if inspect.isgeneratorfunction(func):
        return func(*args, **kwargs)
    else:
        def _wrapper():
            func(*args, **kwargs)
            yield env.timeout(0)

        return _wrapper()


def trans_path_reverse(trans_path):
    str_list = map(str, trans_path)
    return '-'.join(str_list)


def find_all_paths(adj_table, start_node, end_node):
    """
    使用 DFS 找到从 start_node 到 end_node 的所有路径
    """

    def dfs(current_node, path):
        if current_node == end_node:
            all_paths.append(path)
            return
        for neighbor in adj_table[current_node]:
            dfs(neighbor, path + [neighbor])

    all_paths = []
    dfs(start_node, [start_node])
    return all_paths


def getPv(Pu, dist):
    return np.random.exponential(Pu / (dist ** ALPHA))


# 根据信噪比（SINR）计算比特错误率（BER）。
def get_BER_BPSK(SINR):
    def f(x):
        return np.exp(-(x ** 2))

    v, err = integrate.quad(f, math.sqrt(SINR), float('inf'))
    v = v * 2 / math.sqrt(pi)
    return 0.5 * v


# 接收信号功率 = 射频发射功率 + 发射端天线增益 – 路径损耗 – 障碍物衰减 + 接收端天线增益

# 信噪比 SNR = 10lg（ PS / PN ），其中：
# SNR：信噪比，单位是dB。
# PS：信号的有效功率。
# PN：噪声的有效功率。

# 信干噪比 SINR = 10lg[ PS /( PI + PN ) ]，其中：
# SINR：信干噪比，单位是dB。
# PS：信号的有效功率。
# PI：干扰信号的有效功率。
# PN：噪声的有效功率。

# 计算包错误率，d为距离。
def getPER(node_u, node_v, trans_power, noise_strength, interfere_dist, band_width):
    d = distance(node_u.pos, node_v.pos)
    if d != 0:
        Pu = 10 ** (trans_power / 10)  # dBm -> mW
        noise = (10 ** (noise_strength / 10)) * band_width  # noise power(mW)  dBm -> mW
        Pv = getPv(Pu, d)
        I = 0
        for d in interfere_dist:
            I += getPv(Pu, d)
        SINR = Pv / (noise + I)
        if SINR >= BETA:
            return True
        else:
            return False
    else:
        return True




def sample_u(N):
    if N < 2:
        return [0] * N
    # 生成 N 维标准正态分布的随机点
    point = np.random.normal(size=N)

    # 归一化，使其落在单位球面上
    point /= np.linalg.norm(point)

    # 超平面的法向量
    normal = np.ones(N)
    normal /= np.linalg.norm(normal)

    # 计算点在法向量方向上的投影
    projection = np.dot(point, normal) * normal

    # 投影到超平面
    point_on_hyperplane = point - projection

    # 归一化，使其落在交线上
    point_on_hyperplane /= np.linalg.norm(point_on_hyperplane)
    return point_on_hyperplane


def data_to_cdf(data_array):
    k, loc, scale = gamma.fit(data_array)
    return [k, loc, scale]
