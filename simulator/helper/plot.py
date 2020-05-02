import math

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min


def draw_population_state_daily(stats_arg, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_mean_population_state_daily(ax, stats_arg, x_tick)
    plt.show()


def draw_specific_population_state_daily(stats_arg, x_tick=10, style="P"):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_specific_population_state_daily(ax, stats_arg, x_tick, style)
    plt.show()


def draw_lockdown_state_daily(stats_arg, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_lockdown_state_daily(ax, stats_arg["loc"], x_tick)
    plt.show()


def draw_new_daily_cases(stats_arg, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_new_daily_cases(ax, stats_arg, x_tick)
    plt.show()


def draw_summary(stats_arg, x_tick=10):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 10))
    set_ax_mean_population_state_daily(ax1, stats_arg, x_tick)
    set_ax_new_daily_cases(ax2, stats_arg, x_tick)
    set_ax_specific_population_state_daily(ax3, stats_arg, x_tick)
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    ax2.set_title('')
    ax3.set_title('')
    plt.show()


def draw_examples(stats_arg, x_tick=10):
    grid_size = 3
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(16, 10))
    if grid_size * grid_size > stats_arg['hea'].shape[0]:
        raise AssertionError("Raise the number of runs (--nrun parameter) to draw examples")
    # Maybe I did overthink this but I was looking for the most uncommon runs
    # Prefered a kmeans over a set of pairwise kolmogorov smirnov tests
    kmeans = KMeans(n_clusters=grid_size * grid_size, random_state=0)
    kmeans.fit(stats_arg['hea'][:, :])
    chosen_runs, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, stats_arg['hea'][:, :])
    run_index = 0
    for axes_row in axes:
        for ax in axes_row:
            run_id = chosen_runs[run_index]
            death_pct = (100 * stats_arg['dea'][run_id][:][-1] / np.max(stats_arg['hea']))
            set_ax_run_population_state_daily(ax, stats_arg, run_id, x_tick)
            if run_index != grid_size-1:
                ax.legend("")
            if run_index != 2*grid_size:
                ax.set_xlabel("")
                ax.set_ylabel("")
            ax.set_title("Run n°%d - Death percentage %.2f %%" % (run_id, death_pct))
            run_index += 1
    plt.show()


def draw_r0_evolution(stats_arg, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_r0(ax, stats_arg["R0"], x_tick=10)
    plt.show()


# Print iterations progress
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end ="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


def set_ax_r0(ax, stats_r0, x_tick=10):
    n_day_arg = stats_r0.shape[1]
    plot_color = "#3F88C5"
    name_state = "R0"

    stats_mean_arg = np.mean(stats_r0, axis=0)
    stats_err_arg = stats.sem(stats_r0, axis=0)
    serie = [stats_mean_arg[i] for i in range(n_day_arg)]
    err = [stats_err_arg[i] for i in range(n_day_arg)]
    indices = np.arange(n_day_arg)

    p = ax.errorbar(indices, serie, yerr=err, ecolor="#808080", color=plot_color, linewidth=1.3)
    cst_1 = ax.plot(indices, [1 for _ in range(len(indices))], color="#DC143C")

    ax.set_ylabel(name_state)
    ax.set_xlabel('Days since innoculation')
    ax.set_title('Basic reproduction number evolution')

    max_s = int(max(serie))
    min_s = int(min(serie))

    ax.set_xticks(np.arange(0, n_day_arg, int(n_day_arg / x_tick)), tuple([(str(int(i * n_day_arg / x_tick)))
                                                                           for i in range(x_tick)]))
    ax.set_yticks(np.arange(min_s, math.ceil(max_s) + 1, 0.25))
    ax.legend((p[0], cst_1[0], ), (name_state, "Equilibre",))


def set_ax_population_state_daily(ax, stats_arg, x_tick=10):
    n_day_arg = stats_arg['hea'].shape[0]
    n_individual_arg = 1.1 * np.max(stats_arg['hea'])
    dead_serie = [stats_arg["dea"][i] for i in range(n_day_arg)]

    healthy_serie = [stats_arg["hea"][i] for i in range(n_day_arg)]

    infected_serie = [stats_arg["inf"][i] for i in range(n_day_arg)]
    infected_serie_stacked = [stats_arg["hea"][i] + stats_arg["dea"][i] for i in range(n_day_arg)]

    hospital_serie = [stats_arg["hos"][i] for i in range(n_day_arg)]
    hospital_serie_stacked = [stats_arg["hea"][i] + stats_arg["dea"][i] + stats_arg["inf"][i] for i in
                              range(n_day_arg)]

    immune_serie = [stats_arg["imm"][i] for i in range(n_day_arg)]
    immune_serie_stacked = [stats_arg["hea"][i] + stats_arg["dea"][i] + stats_arg["inf"][i] + stats_arg["hos"][i]
                            for i in range(n_day_arg)]

    isolated_serie = [stats_arg["iso"][i] for i in range(n_day_arg)]
    isolated_serie_stacked = [stats_arg["hea"][i] + stats_arg["dea"][i] + stats_arg["inf"][i] + stats_arg["imm"][i] +
                              stats_arg["hos"][i] for i in range(n_day_arg)]

    indices = np.arange(n_day_arg)
    width = 0.7

    p1 = ax.bar(indices, dead_serie, width, color="#151515")
    p2 = ax.bar(indices, healthy_serie, width, bottom=dead_serie, color="#3F88C5")
    p3 = ax.bar(indices, infected_serie, width, bottom=infected_serie_stacked, color="#A63D40")
    p4 = ax.bar(indices, hospital_serie, width, bottom=hospital_serie_stacked, color="#5000FA")
    p5 = ax.bar(indices, immune_serie, width, bottom=immune_serie_stacked, color="#90A959")
    p6 = ax.bar(indices, isolated_serie, width, bottom=isolated_serie_stacked, color="#008080")

    ax.set_ylabel('Total population')
    ax.set_xlabel('Days since innoculation')
    ax.set_title('Average pandemic evolution - Death percentage %.2f %%"' % (100*dead_serie[-1]/np.max(stats_arg['hea'])))
    ax.set_xticks(np.arange(0, n_day_arg, int(n_day_arg / x_tick)),
                  tuple([(str(int(i * n_day_arg / x_tick))) for i in range(x_tick)]))

    ax.set_yticks(np.arange(0, n_individual_arg, (n_individual_arg / 15)))
    ax.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0]),
              ('Dead', 'Healthy', 'Infected', 'Hospitalized', 'Immune', 'Isolated'),
              framealpha=0.35, loc="upper right")


def set_ax_mean_population_state_daily(ax, stats_arg, x_tick):
    stats_mean = {k: np.mean(v, axis=0) for k, v in stats_arg.items()}
    set_ax_population_state_daily(ax, stats_mean, x_tick)


def set_ax_run_population_state_daily(ax, stats_arg, run_id, x_tick):
    stats_run = {k: v[run_id] for k, v in stats_arg.items()}
    set_ax_population_state_daily(ax, stats_run, x_tick)


def set_ax_specific_population_state_daily(ax, stats_arg, x_tick=10, style="P"):
    n_day_arg = stats_arg['hea'].shape[1]
    type_state = "hea"
    plot_color = "#3F88C5"
    name_state = "Healthy"
    if style == 'I':
        type_state = "iso"
        plot_color = "#A63D40"
        name_state = "Infected"
    if style == 'P':
        type_state = "hos"
        plot_color = "#5000FA"
        name_state = "Hospitalized"
    if style == 'D':
        type_state = "dea"
        plot_color = "#151515"
        name_state = "Dead"
    if style == 'M':
        type_state = "imm"
        plot_color = "#90A959"
        name_state = "Immune"

    stats_mean_arg = {k: np.mean(v, axis=0) for k, v in stats_arg.items()}
    stats_err_arg = {k: stats.sem(v, axis=0) for k, v in stats_arg.items()}
    serie = [stats_mean_arg[type_state][i] for i in range(n_day_arg)]
    err = [stats_err_arg[type_state][i] for i in range(n_day_arg)]
    indices = np.arange(n_day_arg)
    width = 0.6

    p = ax.bar(indices, serie, width, yerr=err, align='center', alpha=0.5, ecolor="#808080", color=plot_color)

    ax.set_ylabel(name_state + " population")
    ax.set_xlabel('Days since innoculation')
    ax.set_title('Pandemic evolution')

    ax.set_xticks(np.arange(0, n_day_arg, int(n_day_arg / x_tick)), tuple([(str(int(i * n_day_arg / x_tick)))
                                                                           for i in range(x_tick)]))
    ax.set_yticks(np.arange(0, int(max(serie)*1.1), int(1+max(serie)/10)))
    ax.legend((p[0],), (name_state, ))


def set_ax_lockdown_state_daily(ax, stats_lock, x_tick=10):
    n_day_arg = stats_lock.shape[1]
    plot_color = "#3F88C5"
    name_state = "Lockdown state measure"

    stats_mean_arg = np.mean(stats_lock, axis=0)
    stats_err_arg = stats.sem(stats_lock, axis=0)
    serie = [stats_mean_arg[i] for i in range(n_day_arg)]
    err = [stats_err_arg[i] for i in range(n_day_arg)]
    indices = np.arange(n_day_arg)

    p = ax.errorbar(indices, serie, yerr=err, ecolor="#808080", color=plot_color)

    ax.set_ylabel(name_state)
    ax.set_xlabel('Days since innoculation')
    ax.set_title('Lockdown evolution : Total area %.2f units' % sum(stats_mean_arg))

    max_s = int(max(serie))
    min_s = int(min(serie))

    ax.set_xticks(np.arange(0, n_day_arg, int(n_day_arg / x_tick)), tuple([(str(int(i * n_day_arg / x_tick)))
                                                                           for i in range(x_tick)]))
    ax.set_yticks(np.arange(min_s-1, max_s+1, 1+int((max_s-min_s)/10)))
    ax.legend((p[0],), (name_state, ))


def set_ax_new_daily_cases(ax, stats_arg, x_tick=10):
    n_day_arg = stats_arg['new'].shape[1]
    stats_mean_arg = np.mean(stats_arg['new'], axis=0)
    stats_err_arg = stats.sem(stats_arg['new'], axis=0)
    new_cases_serie = [stats_mean_arg[i] for i in range(n_day_arg)]
    err = [stats_err_arg[i] for i in range(n_day_arg)]

    indices = np.arange(n_day_arg)
    width = 0.6

    p1 = ax.bar(indices, new_cases_serie, width, yerr=err, align='center', alpha=0.5, ecolor="#808080", color="#44A1A0")

    ax.set_ylabel('New cases')
    ax.set_xlabel('Days since innoculation')
    ax.set_title('New infected cases evolution')
    ax.set_xticks(np.arange(0, n_day_arg, int(n_day_arg / x_tick)), tuple([(str(int(i * n_day_arg / x_tick)))
                                                                           for i in range(x_tick)]))
    ax.set_yticks(np.arange(0, int(1+max(new_cases_serie) * 1.1), int(1+max(new_cases_serie) / 10)))
    ax.legend((p1[0],), ('New cases',))


def chose_draw_plot(draw_graph_arg, stats_arg):
    if draw_graph_arg:
        if contains_substring("pop", draw_graph_arg):
            draw_population_state_daily(stats_arg)
        if contains_substring("new", draw_graph_arg):
            draw_new_daily_cases(stats_arg)
        if contains_substring("hos", draw_graph_arg):
            draw_specific_population_state_daily(stats_arg, style="P")
        if contains_substring("sum", draw_graph_arg):
            draw_summary(stats_arg)
        if contains_substring("ex", draw_graph_arg):
            draw_examples(stats_arg)
        if contains_substring("loc", draw_graph_arg):
            draw_lockdown_state_daily(stats_arg)
        if contains_substring("R0", draw_graph_arg):
            draw_r0_evolution(stats_arg)


def contains_substring(substr_arg, list_arg):
    for i in list_arg:
        if i.startswith(substr_arg):
            return True
    return False
