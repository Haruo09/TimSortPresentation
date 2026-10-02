# benchmark timsort

from scripts.core import run_single_complexity
from scripts.plotting import plot_complexity

data = run_single_complexity("timsort")
plot_complexity("timsort", data, "docs/benchmark_timsort.png")

