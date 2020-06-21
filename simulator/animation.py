import random
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


all_ind_hou = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2}
all_hou_sto = {0: [0, 1, 1], 1: [0, 1, 1], 2: [0, 1, 1]}
all_ind_wor = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
sto_ind = {0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1: [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]}
itb = {1: [(4, 2), (4, 1), (4, 0), (3, 0), (2, 0), (1, 0), (1, 1)]}

geo_hou = [(0.030494381790816316, 0.7263274273474801), (0.9674588828672945, 0.9763037695534934),
           (0.6635960434493701, 0.35634519115900853)]
geo_sto = [(0.6737728216491834, 0.11383240112943716), (0.2737728216491834, 0.81383240112943716)]
geo_wor = [(0.4897435154301719, 0.5274856155785992)]




colors = {0: "#3F88C5", 3: "#151515", 1: "#A63D40", 4: "#5000FA", 2: "#90A959", 5: "#008080"}


fig, ax = plt.subplots(figsize=(12, 12))

sto_sizes_dic = {k: len(v) for k, v in sto_ind.items()}

scale_houses = 100*pd.Series(all_ind_hou).value_counts().sort_index().values  # Size of each house
scale_workplaces = 100*pd.Series(all_ind_wor).value_counts().sort_index().values  # Size of each house
scale_stores = 100*pd.Series(sto_sizes_dic).value_counts().sort_index().values  # Size of each house

ax.scatter(np.array(geo_hou)[:, 0], np.array(geo_hou)[:, 1], c="#989C94", s=scale_houses, label="House",
           alpha=0.25, edgecolors='none')
ax.scatter(np.array(geo_wor)[:, 0], np.array(geo_wor)[:, 1], c="#593C8F", s=scale_workplaces, label="Workplace",
           alpha=0.25, edgecolors='none')
ax.scatter(np.array(geo_sto)[:, 0], np.array(geo_sto)[:, 1], c="#FFCB47", s=scale_stores, label="Store",
           alpha=0.25, edgecolors='none')

for x, y in geo_hou:
    ax.text(x-0.005, y+0.02, 'H')
for x, y in geo_wor:
    ax.text(x-0.005, y+0.02, 'W')
for x, y in geo_sto:
    ax.text(x-0.005, y+0.01, 'S')

ax.legend()
ax.grid(True)

scat = ax.scatter([], [], s=60)


def c_r(noise):
    return (random.random()-0.5) / noise


def place(dep, arr, t_step, noise, nb_step):
    return tuple(dep + np.subtract(arr, dep) * t_step / nb_step + (c_r(noise), c_r(noise)))


def get_loc_house_to_work(n_indiv_arg, work_indices_arg, noise, t_step, nb_step):
    result = []
    for ind in range(n_indiv_arg):
        if ind in work_indices_arg:
            w = all_ind_wor[ind]
            geo_h = geo_hou[ind]
            geo_w = geo_wor[w]
            blocks = [geo_h] + [((0.5+u)/10, (0.5+v)/10) for u, v in itb[ind]] + [geo_w]
            nb_links = len(blocks) - 1
            nb_block_step = nb_step/nb_links
            dep = blocks[math.floor(t_step/nb_block_step)]
            arr = blocks[math.floor(t_step/nb_block_step)+1]
            result.append(place(dep, arr, t_step, noise, nb_block_step))
        else:
            h = all_ind_hou[ind]
            result.append((geo_hou[h][0] + c_r(noise), geo_hou[h][1] + c_r(noise)))
    return result


def get_loc_work_to_house(n_indiv_arg, work_indices_arg, noise, t_step, nb_step):
    result = []
    for ind in range(n_indiv_arg):
        if ind in work_indices_arg:
            w = all_ind_wor[ind]
            geo_h = geo_hou[ind]
            geo_w = geo_wor[w]
            blocks = [geo_w] + list(reversed([((0.5+u)/10, (0.5+v)/10) for u, v in itb[ind]])) + [geo_h]
            nb_links = len(blocks) - 1
            nb_block_step = nb_step/nb_links
            dep = blocks[math.floor(t_step/nb_block_step)]
            arr = blocks[math.floor(t_step/nb_block_step)+1]
            result.append(place(dep, arr, t_step, noise, nb_block_step))
        else:
            h = all_ind_hou[ind]
            result.append((geo_hou[h][0] + c_r(noise), geo_hou[h][1] + c_r(noise)))
    return result


def get_loc_house_to_store(n_indiv_arg, store_indices_arg, noise, t_step, nb_step):
    result = []
    for ind in range(n_indiv_arg):
        if ind in [u[0] for u in store_indices_arg]:
            ind = next(s_ind[1][0] for s_ind in enumerate(store_indices_arg) if s_ind[1][0] == ind)
            s = next(s_ind[1][1] for s_ind in enumerate(store_indices_arg) if s_ind[1][0] == ind)
            result.append(place(geo_hou[all_ind_hou[ind]], geo_sto[store_indices_arg[s][1]], t_step, noise, nb_step))
        else:
            h = all_ind_hou[ind]
            result.append((geo_hou[h][0] + c_r(noise), geo_hou[h][1] + c_r(noise)))
    return result


def get_loc_store_to_house(n_indiv_arg, store_indices_arg, noise, t_step, nb_step):
    result = []
    for ind in range(n_indiv_arg):
        if ind in [u[0] for u in store_indices_arg]:
            ind = next(s_ind[1][0] for s_ind in enumerate(store_indices_arg) if s_ind[1][0] == ind)
            s = next(s_ind[1][1] for s_ind in enumerate(store_indices_arg) if s_ind[1][0] == ind)
            result.append(place(geo_sto[store_indices_arg[s][1]], geo_hou[all_ind_hou[ind]], t_step, noise, nb_step))
        else:
            h = all_ind_hou[ind]
            result.append((geo_hou[h][0] + c_r(noise), geo_hou[h][1] + c_r(noise)))
    return result


def get_loc_around_store(n_indiv_arg, store_indices_arg, noise):
    result = []
    for ind in range(n_indiv_arg):
        if ind in [u[0] for u in store_indices_arg]:
            s = [u[1] for u in store_indices_arg if u[0] == ind][0]
            result.append((geo_sto[s][0] + c_r(noise), geo_sto[s][1] + c_r(noise)))
    return result


def get_loc_around_house(n_indiv_arg, noise):
    result = []
    for ind in range(n_indiv_arg):
        h = all_ind_hou[ind]
        result.append((geo_hou[h][0] + c_r(noise), geo_hou[h][1] + c_r(noise)))
    return result


def get_loc_around_work(n_indiv_arg, work_indices_arg, noise):
    result = []
    for ind in range(n_indiv_arg):
        if ind in work_indices_arg:
            w = all_ind_wor[ind]
            result.append((geo_wor[w][0] + c_r(noise), geo_wor[w][1] + c_r(noise)))
    return result


def init_plot():
    scat.set_offsets([])
    return scat,


ind_work = [1]
ind_sto = [(1, 0), (6, 1), (2, 0)]

sig = 100
dt = 100
sta_k = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
ind_colors = np.array([colors[v] for k, v in sta_k.items()])

a = int(0.1*dt)
b = int(0.3*dt)
c = int(0.5*dt)
d = int(0.7*dt)
e = int(1.7*dt)
f = int(1.9*dt)
g = int(2.9*dt)


def update(frame):
    if frame < a:
        scat.set_offsets(np.array(get_loc_house_to_store(len(all_ind_hou), ind_sto, sig, frame, a)))
    elif frame < b:
        scat.set_offsets(np.array(get_loc_around_store(len(all_ind_hou), ind_sto, 0.5 * sig)))
    elif frame < c:
        scat.set_offsets(np.array(get_loc_store_to_house(len(all_ind_hou), ind_sto, sig, frame - b, c - b)))
    elif frame < d:
        scat.set_offsets(np.array(get_loc_around_house(len(all_ind_hou), 0.5 * sig)))
    elif frame < e:
        scat.set_offsets(np.array(get_loc_house_to_work(len(all_ind_hou), ind_work, sig, frame-d, e-d)))
    elif frame < f:
        scat.set_offsets(np.array(get_loc_around_work(len(all_ind_hou), ind_work, sig)))
    elif frame < g:
        scat.set_offsets(np.array(get_loc_work_to_house(len(all_ind_hou), ind_work, sig, frame-f, g-f)))
    scat.set_sizes(np.array([20]*len(all_ind_hou)))
    scat.set_color(ind_colors)
    return scat,


ani = FuncAnimation(fig, update, frames=g, interval=50, init_func=init_plot, blit=True)
plt.show()
