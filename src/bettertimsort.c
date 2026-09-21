#include "timsort.h"
#include <stdio.h>
#include <stdlib.h>

#define MIN_MERGE 32

// Structure representing a identified run on the merge stack
typedef struct {
    int base;
    int len;
} Run;

// Dynamic minRun computation: ensures N / minRun is a power of 2 (or close)
static int calcMinRun(int n) {
    int r = 0;
    while (n >= MIN_MERGE) {
        r |= (n & 1);
        n >>= 1;
    }
    return n + r;
}

// Scans for natural runs. Reverses strictly descending runs in O(n) time.
static int countRunAndMakeAscending(int *arr, int lo, int hi) {
    if (lo >= hi - 1) {
        return hi - lo;
    }

    int runHi = lo + 1;
    if (arr[runHi] < arr[lo]) {
        // Strictly descending run -> scan to end
        while (runHi < hi && arr[runHi] < arr[runHi - 1]) {
            runHi++;
        }
        // Reverse run in-place to ascending
        int left = lo;
        int right = runHi - 1;
        while (left < right) {
            int temp = arr[left];
            arr[left] = arr[right];
            arr[right] = temp;
            left++;
            right--;
        }
    } else {
        // Non-descending run -> scan to end
        while (runHi < hi && arr[runHi] >= arr[runHi - 1]) {
            runHi++;
        }
    }
    return runHi - lo;
}

// Insertion sort for boosting short runs up to minRun length
static void insertionSort(int *arr, int left, int right) {
    for (int i = left + 1; i <= right; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= left && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

// Optimized merge routine using pre-allocated single temporary buffer
static void merge(int *arr, int l, int m, int r, int *temp) {
    int len1 = m - l + 1;

    // Copy only the left sub-array into temp buffer
    for (int i = 0; i < len1; i++) {
        temp[i] = arr[l + i];
    }

    int i = 0;     // Index in temp (left sub-array)
    int j = m + 1; // Index in arr (right sub-array)
    int k = l;     // Target index in original array

    while (i < len1 && j <= r) {
        if (temp[i] <= arr[j]) {
            arr[k++] = temp[i++];
        } else {
            arr[k++] = arr[j++];
        }
    }

    // Copy remaining elements from temp (if any)
    while (i < len1) {
        arr[k++] = temp[i++];
    }
    // Remaining elements in arr[j..r] are already in their correct positions
}

// Merges run i and i+1 on the run stack
static void mergeAt(int *arr, Run stack[], int *stackSize, int i, int *temp) {
    int base1 = stack[i].base;
    int len1 = stack[i].len;
    int len2 = stack[i + 1].len;

    stack[i].len = len1 + len2;

    if (i == *stackSize - 3) {
        stack[i + 1] = stack[i + 2];
    }
    (*stackSize)--;

    merge(arr, base1, base1 + len1 - 1, base1 + len1 + len2 - 1, temp);
}

// Maintains TimSort stack balance invariants
static void collapse(int *arr, Run stack[], int *stackSize, int *temp) {
    while (*stackSize > 1) {
        int n = *stackSize - 2;
        if (n > 0 && stack[n - 1].len <= stack[n].len + stack[n + 1].len) {
            if (stack[n - 1].len < stack[n + 1].len) {
                n--;
            }
            mergeAt(arr, stack, stackSize, n, temp);
        } else if (stack[n].len <= stack[n + 1].len) {
            mergeAt(arr, stack, stackSize, n, temp);
        } else {
            break; // Invariants satisfied
        }
    }
}

// Collapses all remaining runs on the stack at the end
static void forceCollapse(int *arr, Run stack[], int *stackSize, int *temp) {
    while (*stackSize > 1) {
        int n = *stackSize - 2;
        if (n > 0 && stack[n - 1].len < stack[n + 1].len) {
            n--;
        }
        mergeAt(arr, stack, stackSize, n, temp);
    }
}

// Main TimSort entry point
void betterTimSortAlgo(int *arr, int n) {
    if (!arr || n < 2) {
        return;
    }

    int minRun = calcMinRun(n);

    // Single memory allocation for all merge operations
    int *temp = (int *)malloc(n * sizeof(int));
    if (!temp) {
        fprintf(stderr, "Memory allocation failed in timSortAlgo()\n");
        return;
    }

    Run runStack[85]; // Stack capacity suitable for arrays up to 2^64 elements
    int stackSize = 0;

    int lo = 0;
    while (lo < n) {
        // 1. Identify natural run
        int runLen = countRunAndMakeAscending(arr, lo, n);

        // 2. Extend short run to minRun using insertion sort
        if (runLen < minRun) {
            int forceLen = (n - lo < minRun) ? (n - lo) : minRun;
            insertionSort(arr, lo, lo + forceLen - 1);
            runLen = forceLen;
        }

        // 3. Push run to stack
        runStack[stackSize].base = lo;
        runStack[stackSize].len = runLen;
        stackSize++;

        // 4. Maintain stack invariants
        collapse(arr, runStack, &stackSize, temp);

        lo += runLen;
    }

    // 5. Final merge pass
    forceCollapse(arr, runStack, &stackSize, temp);

    // Free temporary memory buffer
    free(temp);
}
