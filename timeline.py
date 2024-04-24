import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime

import matplotlib as mpl
print(mpl.get_cachedir())

plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文无法显示的问题
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def replace(lst):
    seen = []
    for i, item in enumerate(lst):
        if item in seen:
            lst[i] = ' '
        else:
            seen.append(item)
    return lst

def create_level(num):
    level = []
    for i in range(num, 0, -2):
        level.extend([i, -i])
    return level

def time_line(names, dates, tittle, dateFormat="%Y-%m-%d", levels=None):
    num = len(names)
    size = num
    level = create_level(num+4)

    dates = [datetime.strptime(d, dateFormat) for d in dates]
    if levels == None:
        # Choose some nice levels
        levels = np.tile(level,
                         int(np.ceil(len(dates)/6)))[:len(dates)]
    # Create figure and plot a stem plot with the date
    fig, ax = plt.subplots(figsize=(num*2.8, num*1.5), constrained_layout=True)
    # 标题
    ax.set_title(tittle, fontsize=size*2)

    # 添加线条, basefmt设置中线的颜色，linefmt设置线的颜色以及类型
    markerline, stemline, baseline = ax.stem(dates, levels,
                                             linefmt="C3-", basefmt="k-",
                                             )
    # 交点空心,zorder=3设置图层,mec="k"外黑 mfc="w"内白
    plt.setp(markerline, mec="k", mfc="w", zorder=3)

    # 通过将Y数据替换为零，将标记移到基线
    markerline.set_ydata(np.zeros(len(dates)))

    # 构造描述底部、顶部的array
    vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
    # 添加文字注释
    for d, l, r, va in zip(dates, levels, names, vert):
        ax.annotate(r, xy=(d, l), xytext=(-3, np.sign(l)*3),
                    textcoords="offset points", va=va, ha="right", fontsize=size)

    day = []
    for d in dates:
        day.append(d.__format__('%m-%d'))
    day = replace(day)

    for d, l, r, va in zip(dates, levels, day, vert):
        ax.annotate(r, xy=(d, 0), xytext=(-3, np.sign(l) * 3),
                    textcoords="offset points", va=va, ha="right", fontsize=size*0.75)
    plt.xticks(fontsize=size*0.75)

    ax.get_xaxis().set_major_locator(mdates.DayLocator(interval=1))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%m-%d\n"))
    # 逆时针30度，刻度右对齐
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    # 隐藏y轴线
    ax.get_yaxis().set_visible(False)
    # 隐藏左、上、右的边框
    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)
    # 边距仅设置y轴
    ax.margins(y=0.1)

    plt.ioff()
    plt.savefig('./picture/'+tittle+'.png')