import matplotlib.pyplot as plt
import numpy as np


# Print iterations progress
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress_bar (iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end ="\r"):
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


def draw_population_state_daily(stats_arg, n_days_arg, n_individuals_arg):
    fig, ax = plt.subplots(figsize=(15, 10))

    healthy_serie = [stats_arg[i][0] for i in range(n_days_arg)]
    infected_serie = [stats_arg[i][1] for i in range(n_days_arg)]
    dead_serie = [stats_arg[i][2] for i in range(n_days_arg)]
    dead_serie_stacked = [stats_arg[i][0] + stats_arg[i][1] for i in range(n_days_arg)]
    immune_serie = [stats_arg[i][3] for i in range(n_days_arg)]
    immune_serie_stacked = [stats_arg[i][0] + stats_arg[i][1] + stats_arg[i][2] for i in range(n_days_arg)]

    indices = np.arange(n_days_arg)
    width = 0.6

    p1 = plt.bar(indices, healthy_serie, width, color="#3F88C5")
    p2 = plt.bar(indices, infected_serie, width, bottom=healthy_serie, color="#A63D40")
    p3 = plt.bar(indices, dead_serie, width, bottom=dead_serie_stacked, color="#151515")
    p4 = plt.bar(indices, immune_serie, width, bottom=immune_serie_stacked, color="#90A959")

    plt.ylabel('Population')
    plt.title('Pandemic evolution')
    plt.xticks(np.arange(0, n_days_arg, int(n_days_arg/10)), tuple([('Day ' + str(10*i))
                                                                    for i in range(int(n_days_arg/10))]))
    plt.yticks(np.arange(0, n_individuals_arg, n_individuals_arg/25))
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('Healthy', 'Infected', 'Dead', 'Immune'))

    plt.show()


def draw_new_daily_cases(stats_arg, n_days_arg):
    fig, ax = plt.subplots(figsize=(15, 10))

    healthy_serie = [stats_arg[i][0] for i in range(n_days_arg)]
    new_cases_serie = list([j-i for (i,j) in zip(healthy_serie[1:], healthy_serie[:-1] )])

    indices = np.arange(n_days_arg-1)
    width = 0.6

    p1 = plt.bar(indices, new_cases_serie, width, color="#44A1A0")

    plt.ylabel('Population')
    plt.title('New infected cases evolution')
    plt.xticks(np.arange(0, n_days_arg-1, int(n_days_arg/10)), tuple([('Day ' + str(10*i))
                                                                      for i in range(int(n_days_arg/10))]))
    plt.yticks(np.arange(0, int(max(new_cases_serie)*1.1), 5))
    plt.legend((p1[0],), ('New cases',))
    plt.show()

