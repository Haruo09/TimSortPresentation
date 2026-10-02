# bettertimsort benchmark

from scripts.core import run_single_complexity
from scripts.plotting import plot_complexity

data = run_single_complexity("bettertimsort")
plot_complexity("bettertimsort", data, "docs/benchmark_bettertimsort.png")
