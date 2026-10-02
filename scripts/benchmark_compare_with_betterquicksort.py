# timsort vs betterquicksort

from scripts.core import run_comparison
from scripts.plotting import plot_comparison

comp_data = run_comparison("timsort", "betterquicksort")
plot_comparison("timsort", "betterquicksort", comp_data, "docs/timsort_vs_betterquicksort.png")
