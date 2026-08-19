# Changelog

## 0.3.0 — Modernisation

The project had not been touched since 2021 and no longer ran on a current
Python. This release brings it back to life, fixes the bugs that surfaced along
the way, and grows the test suite from "does it import" to "does it simulate
what it claims to".

### Results that change

Three fixes change simulation output. Anything published from scenarios 7, 8
or 10 will not reproduce exactly against this version.

- **Scenarios 7 and 8 — lockdown interpolation.** The six lockdown parameters
  were computed as `confined * u + (normal - confined) * u`, which simplifies to
  `normal * u`. With the lockdown fully on (`u = 0`) every infection
  probability was therefore **0**: the epidemic could not start at all until the
  first unlock step, and the confined regime was never actually simulated. Now
  `confined + (normal - confined) * u`, in the shared
  `scenario.helper.scenario.apply_unlock_progress`.
- **Scenario 10 — compounding genetic cost.** The four variant factors were
  initialised once outside the sweep and divided in place on every iteration, so
  under `restrict_genetic_cost` each step re-normalised the previous step's
  already-normalised values and all four decayed toward zero. They are now
  derived per variant by `get_variant_factors`.
- **Scenario 7 — `--extra` flag parsing.** The relock switch was read as
  `bool(value)` on an argparse string, so `--extra 0` turned relocking *on*.
  Booleans now go through `parse_bool`.

### Fixed

- `random.sample()` has rejected sets and dict views since Python 3.11, which
  made the environment builder — and therefore every entry point — fail
  immediately on any modern interpreter.
- Every plot raised `ZeroDivisionError` when a run was shorter than the tick
  count (`--nday 8`), and its x labels drifted away from the tick positions
  whenever `nday` was not a multiple of `x_tick`. Both are handled by the new
  `set_day_xticks`.
- `plt.savefig` assumed `images/output` existed; the directory is now created on
  demand, figures are closed after saving, and the location is configurable via
  `PANDEMIC_SIMULATION_OUTPUT_DIR`.
- `--draw R0d` also drew the sliding-R0 graph, and `--draw metasimu` was
  unreachable because it hung off an `elif` on the R0 branch. `--draw` now
  resolves each token to exactly one graph and rejects unknown names.
- `--ncpu -N` computed `cpu_count - (-N)`, asking ray for more cores than the
  machine has rather than leaving N free.
- Scenario 5 sent one extra progress tick per run, overshooting its own bar.
- Single-run plots showed no error bars: `scipy.stats.sem` returns `nan` for one
  sample. `sem_or_zero` returns zeros instead.
- `IDEA_K` (per-individual mortality rate) and `DEA_K` (countdown to the
  death roll) were the same string, `"individual_to_death_mapping"`.
- `animate_base_lockdown` accumulated its history in module-level lists and
  appended the live state dict by reference, so every day of the replay was a
  copy of the last one.
- `simulator/animation.py` built its figure and called `plt.show()` at import
  time, and `init_plot` passed an empty list where matplotlib wants an
  `(N, 2)` array.
- `python -m simulator.run` printed raw profiling arrays; profiling is now
  opt-in and belongs to `python -m simulator.run_benchmark`.
- `--scenario-id`'s help text read "Immunity bounds".
- `get_virus_simulation_t0` drew four sets of four periods per individual and
  kept one value from each, burning 12 random numbers out of every 16.

### Changed

- Packaging moved from `setup.py` to `pyproject.toml`. The declared
  dependencies were wrong: `sklearn` (the dead shim) instead of
  `scikit-learn`, `argparse` (stdlib since 2.7), `seaborn` (never imported),
  and no `ray`, `joblib`, `tqdm` or `psutil` despite all four being required.
- Travis CI replaced by GitHub Actions, testing 3.9 / 3.11 / 3.13.
- `ruff` added and the tree made clean under it; wildcard imports replaced by
  explicit ones throughout.
- Argument parsing extracted to `parser.parse_params`, shared by the three
  entry points, each of which now exposes a testable `main(argv)`.
- `--extra-scenario-params` is read through a typed `read_extra_params` that
  names what the scenario expected instead of raising `IndexError` later.
- Dead code removed: `build_2d_item_behavior`, `get_store_index`, `flatten`,
  and the unused `QUARANTINE_DAYS` parameter.

### Tests

- 305 tests, 99% coverage (was 63%).
- The scenario tests previously called `do_parallel_run.remote(...)` and
  asserted `len(stats_l) > 0`. A ray future only raises when awaited, so a
  scenario could fail on every single day and the test still passed. Every run
  now goes through `ray.get`, and the statistics are checked against model
  invariants: population conservation, monotone death toll, contagious ⊆
  infected, reproducibility under a fixed seed and environment.
- Assertions on exact RNG draws — which is what broke on the scipy upgrade —
  replaced by property and distribution assertions.
- New coverage for the argument parser, the statistics layer, the plot
  dispatch, the three CLI entry points, and the environment-model cache.
