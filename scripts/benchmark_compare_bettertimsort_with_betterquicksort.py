from scripts.core import run_comparison
from scripts.plotting import plot_comparison

comp_data = run_comparison("bettertimsort", "betterquicksort")
plot_comparison("bettertimsort", "betterquicksort", comp_data, "docs/bettertimsort_vs_betterquicksort.png")
