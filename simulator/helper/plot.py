import datetime
import math
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

OUTPUT_DIR = os.environ.get("PANDEMIC_SIMULATION_OUTPUT_DIR", os.path.join("images", "output"))


def render(fig, show_plot, name, *scale_args):
    """Show the figure, or drop it in OUTPUT_DIR under a run-stamped name."""
    if show_plot:
        plt.show()
        return None
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    stamp = int(datetime.datetime.now().timestamp())
    suffix = "-".join(str(int(a)) for a in scale_args)
    path = os.path.join(OUTPUT_DIR, f"{stamp}-{name}-{suffix}.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def set_day_xticks(ax, n_day_arg, x_tick=10):
    """Put at most `x_tick` evenly spaced day labels on the x axis."""
    step = max(1, int(n_day_arg / x_tick))
    positions = np.arange(0, n_day_arg, step)[:x_tick]
    ax.set_xticks(positions)
    ax.set_xticklabels(tuple(str(int(p)) for p in positions))


def sem_or_zero(values, axis=0):
    """Standard error, or zeros when there is a single run to average over."""
    if values.shape[axis] < 2:
        return np.zeros(values.shape[1 - axis])
    return stats.sem(values, axis=axis)


def _scale(stats_arg, key='hea'):
    return stats_arg[key].shape[0], np.max(stats_arg[key])


def draw_population_state_daily(stats_arg, show_plot, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_mean_population_state_daily(ax, stats_arg, x_tick)
    return render(fig, show_plot, "pop", *_scale(stats_arg))


def draw_specific_population_state_daily(stats_arg, show_plot, x_tick=10, style="P"):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_specific_population_state_daily(ax, stats_arg, x_tick, style)
    return render(fig, show_plot, "style-" + style, *_scale(stats_arg))


def draw_lockdown_state_daily(stats_arg, show_plot, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_lockdown_state_daily(ax, stats_arg["loc"], x_tick)
    return render(fig, show_plot, "lock", *_scale(stats_arg))


def draw_new_daily_cases(stats_arg, show_plot, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_new_daily_cases(ax, stats_arg, x_tick)
    return render(fig, show_plot, "new", *_scale(stats_arg))


def draw_meta_simulation(death_stat_arg, show_plot):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_meta_simulation(ax, death_stat_arg)
    return render(fig, show_plot, "meta", *_scale(death_stat_arg, 'dea'))


def draw_summary(stats_arg, show_plot, x_tick=10):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 10))
    set_ax_mean_population_state_daily(ax1, stats_arg, x_tick)
    set_ax_new_daily_cases(ax2, stats_arg, x_tick)
    set_ax_specific_population_state_daily(ax3, stats_arg, x_tick)
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    ax2.set_title('')
    ax3.set_title('')
    return render(fig, show_plot, "summ", *_scale(stats_arg))


def draw_examples(stats_arg, show_plot, x_tick=10):
    grid_size = 3
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(16, 10))
    if grid_size * grid_size > stats_arg['hea'].shape[0]:
        raise AssertionError("Raise the number of runs (--nrun parameter) to draw examples")
    # Maybe I did overthink this but I was looking for the most uncommon runs
    # Prefered a kmeans over a set of pairwise kolmogorov smirnov tests
    kmeans = KMeans(n_clusters=grid_size * grid_size, random_state=0, n_init=10)
    kmeans.fit(stats_arg['hea'][:, :])
    chosen_runs, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, stats_arg['hea'][:, :])
    run_index = 0
    for axes_row in axes:
        for ax in axes_row:
            run_id = chosen_runs[run_index]
            death_pct = (100 * stats_arg['dea'][run_id][:][-1] / np.max(stats_arg['hea']))
            set_ax_run_population_state_daily(ax, stats_arg, run_id, x_tick)
            if run_index != grid_size - 1:
                ax.get_legend().remove()
            if run_index != 2 * grid_size:
                ax.set_xlabel("")
                ax.set_ylabel("")
            ax.set_title(f"Run n°{run_id} - Death percentage {death_pct:.2f} %")
            run_index += 1
    return render(fig, show_plot, "examples", *_scale(stats_arg))


def draw_r0_daily_evolution(stats_arg, show_plot, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    set_ax_r0(ax, stats_arg["R0d"], "R0 Daily", x_tick=x_tick)
    return render(fig, show_plot, "R0-daily", *_scale(stats_arg))


def draw_r0_evolution(stats_arg, show_plot, window_size=3, x_tick=10):
    fig, ax = plt.subplots(figsize=(15, 10))
    slid_new = np.array([np.convolve(sn, np.ones(window_size, dtype=int), 'valid') for sn in stats_arg["new"]])
    slid_con = np.array([rolling_max(sc, window_size) for sc in 1+stats_arg["con"]])
    set_ax_r0(ax, slid_new/slid_con, "2 weeks sliding R0", x_tick=x_tick)
    return render(fig, show_plot, "R0-evo", *_scale(stats_arg))


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
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


def set_ax_r0(ax, stats_r0, lib, x_tick=10):
    n_day_arg = stats_r0.shape[1]
    plot_color = "#3F88C5"
    name_state = lib

    stats_mean_arg = np.mean(stats_r0, axis=0)
    stats_err_arg = sem_or_zero(stats_r0)
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

    set_day_xticks(ax, n_day_arg, x_tick)
    ax.set_yticks(np.arange(min_s, math.ceil(max_s) + 1, 0.25))
    ax.legend((p[0], cst_1[0], ), (name_state, "Equilibrium",))


def set_ax_population_state_daily(ax, stats_arg, x_tick=10):
    n_day_arg = stats_arg['hea'].shape[0]
    if np.max(stats_arg['hea']) <= 0:
        raise ValueError("No healthy individual was ever recorded, there is nothing to plot. "
                         "Check that the simulation actually ran (--nind / --nday).")
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
    death_pct = 100 * dead_serie[-1] / np.max(stats_arg['hea'])
    ax.set_title(f'Average pandemic evolution - Death percentage {death_pct:.2f} %')
    set_day_xticks(ax, n_day_arg, x_tick)

    ax.set_yticks(np.arange(0, n_individual_arg, max(1, round(n_individual_arg / 15))))
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

    stats_mean_arg = np.mean(stats_arg[type_state], axis=0)
    stats_err_arg = sem_or_zero(stats_arg[type_state])
    serie = [stats_mean_arg[i] for i in range(n_day_arg)]
    err = [stats_err_arg[i] for i in range(n_day_arg)]
    indices = np.arange(n_day_arg)
    width = 0.6

    p = ax.bar(indices, serie, width, yerr=err, align='center', alpha=0.5, ecolor="#808080", color=plot_color)

    ax.set_ylabel(name_state + " population")
    ax.set_xlabel('Days since innoculation')
    ax.set_title('Pandemic evolution')

    set_day_xticks(ax, n_day_arg, x_tick)
    ax.set_yticks(np.arange(0, int(max(serie)*1.1), int(1+max(serie)/10)))
    ax.legend((p[0],), (name_state, ))


def set_ax_lockdown_state_daily(ax, stats_lock, x_tick=10):
    n_day_arg = stats_lock.shape[1]
    plot_color = "#3F88C5"
    name_state = "Lockdown state measure"

    stats_mean_arg = np.mean(stats_lock, axis=0)
    stats_err_arg = sem_or_zero(stats_lock)
    serie = [stats_mean_arg[i] for i in range(n_day_arg)]
    err = [stats_err_arg[i] for i in range(n_day_arg)]
    indices = np.arange(n_day_arg)

    p = ax.errorbar(indices, serie, yerr=err, ecolor="#808080", color=plot_color)

    ax.set_ylabel(name_state)
    ax.set_xlabel('Days since innoculation')
    ax.set_title(f'Lockdown evolution : Total area {sum(stats_mean_arg):.2f} units')

    max_s = int(max(serie))
    min_s = int(min(serie))

    set_day_xticks(ax, n_day_arg, x_tick)
    ax.set_yticks(np.arange(min_s-1, max_s+1, 1+int((max_s-min_s)/10)))
    ax.legend((p[0],), (name_state, ))


def set_ax_new_daily_cases(ax, stats_arg, x_tick=10):
    n_day_arg = stats_arg['new'].shape[1]
    stats_mean_arg = np.mean(stats_arg['new'], axis=0)
    stats_err_arg = sem_or_zero(stats_arg['new'])
    new_cases_serie = [stats_mean_arg[i] for i in range(n_day_arg)]
    err = [stats_err_arg[i] for i in range(n_day_arg)]

    indices = np.arange(n_day_arg)
    width = 0.6

    p1 = ax.bar(indices, new_cases_serie, width, yerr=err, align='center', alpha=0.5, ecolor="#808080", color="#44A1A0")

    ax.set_ylabel('New cases')
    ax.set_xlabel('Days since innoculation')
    ax.set_title('New infected cases evolution')
    set_day_xticks(ax, n_day_arg, x_tick)
    ax.set_yticks(np.arange(0, int(1+max(new_cases_serie) * 1.1), int(1+max(new_cases_serie) / 10)))
    ax.legend((p1[0],), ('New cases',))


def set_ax_meta_simulation(ax, death_stat_arg):
    n_variant_arg = death_stat_arg['dea'].shape[1]
    stats_mean_arg = np.mean(death_stat_arg['dea'], axis=0)
    stats_err_arg = sem_or_zero(death_stat_arg['dea'])
    death_serie = [stats_mean_arg[i] for i in range(n_variant_arg)]
    err = [stats_err_arg[i] for i in range(n_variant_arg)]

    indices = np.arange(n_variant_arg)
    width = 0.6

    p1 = ax.bar(indices, death_serie, width, yerr=err, align='center', alpha=0.5, ecolor="#808080", color="#44A1A0")

    bottom_y = int(min(death_serie) * 0.8)
    top_y = int(1+max(death_serie) * 1.2)

    ax.set_ylim(bottom=bottom_y, top=top_y)
    ax.set_ylabel('Total death')
    ax.set_xlabel('Variant parameter')
    ax.set_title('Total death / covid-19 variant type')
    ax.set_xticks(np.arange(0, n_variant_arg, 1))
    ax.set_xticklabels([round(s, 2) for s in np.arange(0.25, 1.75, 1.5 / n_variant_arg)])
    ax.set_yticks(np.arange(bottom_y, top_y, int(1+max(death_serie) / 10)))
    ax.legend((p1[0],), ('Death',))


DRAW_PREFIXES = (
    ("metasimu", draw_meta_simulation),
    ("R0d", draw_r0_daily_evolution),
    ("R0", lambda st, sp: draw_r0_evolution(st, sp, 14)),
    ("pop", draw_population_state_daily),
    ("new", draw_new_daily_cases),
    ("hos", lambda st, sp: draw_specific_population_state_daily(st, sp, style="P")),
    ("sum", draw_summary),
    ("loc", draw_lockdown_state_daily),
    ("ex", draw_examples),
)


def chose_draw_plot(draw_graph_arg, stats_arg, show_plot=False):
    """Draw every graph named on the command line, one drawer per --draw token."""
    drawn = []
    for token in draw_graph_arg or []:
        # Longest prefix wins: "R0d" must not also match the "R0" drawer.
        match = max((p for p in DRAW_PREFIXES if token.startswith(p[0])),
                    key=lambda p: len(p[0]), default=None)
        if match is None:
            raise KeyError(f"Unknown --draw value {token!r}, expected one of "
                           f"{[p[0] for p in DRAW_PREFIXES]}")
        if match[0] not in drawn:
            drawn.append(match[0])
            match[1](stats_arg, show_plot)
    return drawn


def contains_substring(substr_arg, list_arg):
    return any(i.startswith(substr_arg) for i in list_arg)


# https://stackoverflow.com/a/43335059/2166220
def rolling_max(a, window):
    def each_value():
        w = a[:window].copy()
        m = w.max()
        yield m
        i = 0
        j = window
        while j < len(a):
            old_value = w[i]
            new_value = w[i] = a[j]
            if new_value > m:
                m = new_value
            elif old_value == m:
                m = w.max()
            yield m
            i = (i + 1) % window
            j += 1
    return np.array(list(each_value()))
