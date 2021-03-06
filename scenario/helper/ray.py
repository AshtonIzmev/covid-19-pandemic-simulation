import random

import psutil
import ray

from scenario.helper.scenario import get_zero_stats
from simulator.constants.keys import nrun_key, nday_key
from simulator.helper.dynamic import merge_run_stat
from simulator.helper.plot import print_progress_bar
from scenario.helper.progressbar import ProgressBar


def launch_parallel_run(params, env_dic, fun, ncpu, display_progress=True):
    if ncpu < 0:
        num_cpus = max(psutil.cpu_count(logical=False) - ncpu, 1)
    elif ncpu == 0:
        num_cpus = 1
    else:
        num_cpus = min(ncpu, psutil.cpu_count(logical=False))
    ray.init(num_cpus=num_cpus)
    pb = ProgressBar(params[nrun_key]*params[nday_key])
    actor = pb.actor
    stats = get_zero_stats(params)
    ray_params = ray.put(params)
    ray_env_dic = ray.put(env_dic)
    stats_l = []
    for run_id in range(params[nrun_key]):
        stats_l.append(fun.remote(ray_env_dic, ray_params, run_id, random.randint(0, 10000), actor))
    pb.print_until_done()
    for run_id, run_stats in ray.get(stats_l):
        merge_run_stat(stats, run_stats, run_id)
    return stats


def launch_run(params, env_dic, fun, ncpu, display_progress=True):
    stats = get_zero_stats(params)
    stats_l = []
    for run_id in range(params[nrun_key]):
        if display_progress:
            print_progress_bar(run_id, params[nrun_key], prefix='Progress:', suffix='Complete', length=50)
        stats_l.append(fun(env_dic, params, run_id))
    for run_id, run_stats in stats_l:
        merge_run_stat(stats, run_stats, run_id)
    return stats

