from scripts.core import run_comparison
from scripts.plotting import plot_comparison

comp_data = run_comparison("peaktimsort", "betterquicksort")
plot_comparison("peaktimsort", "betterquicksort", comp_data, "docs/peaktimsort_vs_betterquicksort.png")

