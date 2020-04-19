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
    if grid_size * grid_size >= stats_arg.shape[0]:
        raise AssertionError("Raise the number of runs (--nrun parameter) to draw examples")
    # Maybe I did overthink this but I was looking into the most uncommon runs
    # Prefered a kmeans over a set of pairwise kolmogorov smirnov tests
    kmeans = KMeans(n_clusters=grid_size * grid_size, random_state=0)
    kmeans.fit(stats_arg[:, :, 0])
    chosen_run, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, stats_arg[:, :, 0])
    run_id = 0
    for axes_row in axes:
        for ax in axes_row:
            set_ax_run_population_state_daily(ax, stats_arg, chosen_run[run_id], x_tick)
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.set_title("Run n°" + str(chosen_run[run_id]))
            run_id += 1
    axes[grid_size-1][0].set_xlabel('Days since innoculation')
    axes[grid_size-1][0].set_ylabel('Total population')
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


def set_ax_population_state_daily(ax, stats_arg, x_tick=10):
    n_day_arg = stats_arg.shape[0]
    n_individual_arg = 1.1 * np.max(stats_arg)
    dead_serie = [stats_arg[i][3] for i in range(n_day_arg)]

    healthy_serie = [stats_arg[i][0] for i in range(n_day_arg)]

    infected_serie = [stats_arg[i][1] for i in range(n_day_arg)]
    infected_serie_stacked = [stats_arg[i][0] + stats_arg[i][3] for i in range(n_day_arg)]

    hospital_serie = [stats_arg[i][2] for i in range(n_day_arg)]
    hospital_serie_stacked = [stats_arg[i][0] + stats_arg[i][1] + stats_arg[i][3] for i in
                              range(n_day_arg)]

    immune_serie = [stats_arg[i][4] for i in range(n_day_arg)]
    immune_serie_stacked = [stats_arg[i][0] + stats_arg[i][1] + stats_arg[i][2] + stats_arg[i][3]
                            for i in range(n_day_arg)]

    indices = np.arange(n_day_arg)
    width = 0.7

    p1 = ax.bar(indices, dead_serie, width, color="#151515")
    p2 = ax.bar(indices, healthy_serie, width, bottom=dead_serie, color="#3F88C5")
    p3 = ax.bar(indices, infected_serie, width, bottom=infected_serie_stacked, color="#A63D40")
    p4 = ax.bar(indices, hospital_serie, width, bottom=hospital_serie_stacked, color="#5000FA")
    p5 = ax.bar(indices, immune_serie, width, bottom=immune_serie_stacked, color="#90A959")

    ax.set_ylabel('Total population')
    ax.set_xlabel('Days since innoculation')
    ax.set_title('Pandemic evolution')
    ax.set_xticks(np.arange(0, n_day_arg, int(n_day_arg / x_tick)),
                  tuple([(str(int(i * n_day_arg / x_tick))) for i in range(x_tick)]))

    ax.set_yticks(np.arange(0, n_individual_arg, (n_individual_arg / 15)))
    ax.legend((p1[0], p2[0], p3[0], p4[0], p5[0]), ('Dead', 'Healthy', 'Infected', 'Hospitalized', 'Immune'),
              framealpha=0.35)


def set_ax_mean_population_state_daily(ax, stats_arg, x_tick):
    stats_mean = np.mean(stats_arg, axis=0)
    set_ax_population_state_daily(ax, stats_mean, x_tick)


def set_ax_run_population_state_daily(ax, stats_arg, run_id, x_tick):
    stats_run = stats_arg[run_id]
    set_ax_population_state_daily(ax, stats_run, x_tick)


def set_ax_specific_population_state_daily(ax, stats_arg, x_tick=10, style="P"):
    n_day_arg = stats_arg.shape[1]
    type_state = 0
    plot_color = "#3F88C5"
    name_state = "Healthy"
    if style == 'I':
        type_state = 1
        plot_color = "#A63D40"
        name_state = "Infected"
    if style == 'P':
        type_state = 2
        plot_color = "#5000FA"
        name_state = "Hospitalized"
    if style == 'D':
        type_state = 3
        plot_color = "#151515"
        name_state = "Dead"
    if style == 'M':
        type_state = 4
        plot_color = "#90A959"
        name_state = "Immune"

    stats_mean_arg = np.mean(stats_arg, axis=0)
    stats_err_arg = stats.sem(stats_arg, axis=0)
    serie = [stats_mean_arg[i][type_state] for i in range(n_day_arg)]
    err = [stats_err_arg[i][type_state] for i in range(n_day_arg)]
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


def set_ax_new_daily_cases(ax, stats_arg, x_tick=10):
    n_day_arg = stats_arg.shape[1]
    stats_mean_arg = np.mean(stats_arg, axis=0)
    stats_err_arg = stats.sem(stats_arg, axis=0)
    new_cases_serie = [stats_mean_arg[i][5] for i in range(n_day_arg)]
    err = [stats_err_arg[i][5] for i in range(n_day_arg)]

    indices = np.arange(n_day_arg)
    width = 0.6

    p1 = ax.bar(indices, new_cases_serie, width, yerr=err, align='center', alpha=0.5, ecolor="#808080", color="#44A1A0")

    ax.set_ylabel('New cases')
    ax.set_xlabel('Days since innoculation')
    ax.set_title('New infected cases evolution')
    ax.set_xticks(np.arange(0, n_day_arg, int(n_day_arg / x_tick)), tuple([(str(int(i * n_day_arg / x_tick)))
                                                                           for i in range(x_tick)]))
    ax.set_yticks(np.arange(0, int(max(new_cases_serie) * 1.1), int(max(new_cases_serie) / 10)))
    ax.legend((p1[0],), ('New cases',))


def chose_draw_plot(args_arg, stats_arg):
    if args_arg.population_state:
        draw_population_state_daily(stats_arg)
    elif args_arg.new_cases:
        draw_new_daily_cases(stats_arg)
    elif args_arg.hospitalized_cases:
        draw_specific_population_state_daily(stats_arg)
    elif args_arg.summary:
        draw_summary(stats_arg)
    elif args_arg.examples:
        draw_examples(stats_arg)
    else:
        draw_population_state_daily(stats_arg)
