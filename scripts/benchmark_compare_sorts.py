# timsort_vs_quicksort

from scripts.core import run_comparison
from scripts.plotting import plot_comparison

comp_data = run_comparison("timsort", "quicksort")
plot_comparison("timsort", "quicksort", comp_data, "docs/timsort_vs_quicksort.png")
