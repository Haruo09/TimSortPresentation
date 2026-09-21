#include "timsort.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MIN_MERGE 32
#define MIN_GALLOP 7

typedef struct {
    int base;
    int len;
} Run;

static int calcMinRun(int n) {
    int r = 0;
    while (n >= MIN_MERGE) {
        r |= (n & 1);
        n >>= 1;
    }
    return n + r;
}

// Scans for natural runs; reverses strictly descending runs in O(n)
static int countRunAndMakeAscending(int *restrict arr, int lo, int hi) {
    if (lo >= hi - 1)
        return hi - lo;

    int runHi = lo + 1;
    if (arr[runHi] < arr[lo]) {
        while (runHi < hi && arr[runHi] < arr[runHi - 1])
            runHi++;
        int left = lo, right = runHi - 1;
        while (left < right) {
            int temp = arr[left];
            arr[left++] = arr[right];
            arr[right--] = temp;
        }
    } else {
        while (runHi < hi && arr[runHi] >= arr[runHi - 1])
            runHi++;
    }
    return runHi - lo;
}

// Binary insertion sort with block moves via memmove
static void binaryInsertionSort(int *restrict arr, int lo, int hi, int start) {
    if (start <= lo)
        start = lo + 1;
    for (; start <= hi; start++) {
        int pivot = arr[start];
        int l = lo, r = start;
        while (l < r) {
            int mid = l + ((r - l) >> 1);
            if (pivot < arr[mid])
                r = mid;
            else
                l = mid + 1;
        }
        int n = start - l;
        if (n > 0) {
            memmove(&arr[l + 1], &arr[l], n * sizeof(int));
        }
        arr[l] = pivot;
    }
}

// Exponential search: finds insertion index for key in sorted array a[0..len-1]
static int gallopLeft(int key, const int *restrict a, int len, int hint) {
    int lastOfs = 0, ofs = 1;
    if (key > a[hint]) {
        int maxOfs = len - hint;
        while (ofs < maxOfs && key > a[hint + ofs]) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;
        lastOfs += hint;
        ofs += hint;
    } else {
        int maxOfs = hint + 1;
        while (ofs < maxOfs && key <= a[hint - ofs]) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;
        int tmp = lastOfs;
        lastOfs = hint - ofs;
        ofs = hint - tmp;
    }
    lastOfs++;
    while (lastOfs < ofs) {
        int m = lastOfs + ((ofs - lastOfs) >> 1);
        if (key > a[m])
            lastOfs = m + 1;
        else
            ofs = m;
    }
    return ofs;
}

static int gallopRight(int key, const int *restrict a, int len, int hint) {
    int lastOfs = 0, ofs = 1;
    if (key < a[hint]) {
        int maxOfs = hint + 1;
        while (ofs < maxOfs && key < a[hint - ofs]) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;
        int tmp = lastOfs;
        lastOfs = hint - ofs;
        ofs = hint - tmp;
    } else {
        int maxOfs = len - hint;
        while (ofs < maxOfs && key >= a[hint + ofs]) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;
        lastOfs += hint;
        ofs += hint;
    }
    lastOfs++;
    while (lastOfs < ofs) {
        int m = lastOfs + ((ofs - lastOfs) >> 1);
        if (key < a[m])
            ofs = m;
        else
            lastOfs = m + 1;
    }
    return ofs;
}

// Low-to-high merge (copies left run to temp)
static void mergeLo(int *restrict arr, int base1, int len1, int base2, int len2,
                    int *restrict temp) {
    memcpy(temp, &arr[base1], len1 * sizeof(int));
    int i = 0, j = base2, k = base1;
    int rem1 = len1, rem2 = len2;

    while (rem1 > 0 && rem2 > 0) {
        int count1 = 0, count2 = 0;
        do {
            if (arr[j] < temp[i]) {
                arr[k++] = arr[j++];
                rem2--;
                count2++;
                count1 = 0;
                if (rem2 == 0)
                    break;
            } else {
                arr[k++] = temp[i++];
                rem1--;
                count1++;
                count2 = 0;
                if (rem1 == 0)
                    break;
            }
        } while ((count1 | count2) < MIN_GALLOP);

        if (rem1 == 0 || rem2 == 0)
            break;

        // Galloping mode
        do {
            count1 = gallopRight(arr[j], &temp[i], rem1, 0);
            if (count1 > 0) {
                memcpy(&arr[k], &temp[i], count1 * sizeof(int));
                k += count1;
                i += count1;
                rem1 -= count1;
                if (rem1 == 0)
                    break;
            }
            arr[k++] = arr[j++];
            rem2--;
            if (rem2 == 0)
                break;

            count2 = gallopLeft(temp[i], &arr[j], rem2, 0);
            if (count2 > 0) {
                memmove(&arr[k], &arr[j], count2 * sizeof(int));
                k += count2;
                j += count2;
                rem2 -= count2;
                if (rem2 == 0)
                    break;
            }
            arr[k++] = temp[i++];
            rem1--;
            if (rem1 == 0)
                break;
        } while (count1 >= MIN_GALLOP || count2 >= MIN_GALLOP);
    }

    if (rem1 > 0) {
        memcpy(&arr[k], &temp[i], rem1 * sizeof(int));
    }
}

// High-to-low merge (copies right run to temp)
static void mergeHi(int *restrict arr, int base1, int len1, int base2, int len2,
                    int *restrict temp) {
    memcpy(temp, &arr[base2], len2 * sizeof(int));
    int i = base1 + len1 - 1, j = len2 - 1, k = base2 + len2 - 1;
    int rem1 = len1, rem2 = len2;

    while (rem1 > 0 && rem2 > 0) {
        int count1 = 0, count2 = 0;
        do {
            if (temp[j] < arr[i]) {
                arr[k--] = arr[i--];
                rem1--;
                count1++;
                count2 = 0;
                if (rem1 == 0)
                    break;
            } else {
                arr[k--] = temp[j--];
                rem2--;
                count2++;
                count1 = 0;
                if (rem2 == 0)
                    break;
            }
        } while ((count1 | count2) < MIN_GALLOP);

        if (rem1 == 0 || rem2 == 0)
            break;

        // Galloping mode
        do {
            count1 = rem1 - gallopRight(temp[j], &arr[base1], rem1, rem1 - 1);
            if (count1 > 0) {
                k -= count1;
                i -= count1;
                rem1 -= count1;
                memmove(&arr[k + 1], &arr[i + 1], count1 * sizeof(int));
                if (rem1 == 0)
                    break;
            }
            arr[k--] = temp[j--];
            rem2--;
            if (rem2 == 0)
                break;

            count2 = (j + 1) - gallopLeft(arr[i], temp, rem2, j);
            if (count2 > 0) {
                k -= count2;
                j -= count2;
                rem2 -= count2;
                memcpy(&arr[k + 1], &temp[j + 1], count2 * sizeof(int));
                if (rem2 == 0)
                    break;
            }
            arr[k--] = arr[i--];
            rem1--;
            if (rem1 == 0)
                break;
        } while (count1 >= MIN_GALLOP || count2 >= MIN_GALLOP);
    }

    if (rem2 > 0) {
        memcpy(&arr[base1], temp, rem2 * sizeof(int));
    }
}

static void mergeAt(int *restrict arr, Run stack[], int *stackSize, int i, int *restrict temp) {
    int base1 = stack[i].base;
    int len1 = stack[i].len;
    int base2 = stack[i + 1].base;
    int len2 = stack[i + 1].len;

    stack[i].len = len1 + len2;

    if (i == *stackSize - 3) {
        stack[i + 1] = stack[i + 2];
    }
    (*stackSize)--;

    // 1. Trim leading elements from run 1 that are already <= min(run 2)
    int k = gallopRight(arr[base2], &arr[base1], len1, 0);
    base1 += k;
    len1 -= k;
    if (len1 == 0)
        return;

    // 2. Trim trailing elements from run 2 that are already >= max(run 1)
    len2 = gallopLeft(arr[base1 + len1 - 1], &arr[base2], len2, len2 - 1);
    if (len2 == 0)
        return;

    // 3. Select optimal merge direction
    if (len1 <= len2) {
        mergeLo(arr, base1, len1, base2, len2, temp);
    } else {
        mergeHi(arr, base1, len1, base2, len2, temp);
    }
}

static void collapse(int *restrict arr, Run stack[], int *stackSize, int *restrict temp) {
    while (*stackSize > 1) {
        int n = *stackSize - 2;
        if (n > 0 && stack[n - 1].len <= stack[n].len + stack[n + 1].len) {
            if (stack[n - 1].len < stack[n + 1].len)
                n--;
            mergeAt(arr, stack, stackSize, n, temp);
        } else if (stack[n].len <= stack[n + 1].len) {
            mergeAt(arr, stack, stackSize, n, temp);
        } else {
            break;
        }
    }
}

static void forceCollapse(int *restrict arr, Run stack[], int *stackSize, int *restrict temp) {
    while (*stackSize > 1) {
        int n = *stackSize - 2;
        if (n > 0 && stack[n - 1].len < stack[n + 1].len)
            n--;
        mergeAt(arr, stack, stackSize, n, temp);
    }
}

void peakTimSortAlgo(int *arr, int n) {
    if (!arr || n < 2)
        return;

    int minRun = calcMinRun(n);

    // Temp buffer capped at n/2 elements
    int *temp = (int *)malloc((n / 2 + 1) * sizeof(int));
    if (!temp) {
        fprintf(stderr, "Memory allocation failed in peakTimSortAlgo()\n");
        return;
    }

    Run runStack[85];
    int stackSize = 0;
    int lo = 0;

    while (lo < n) {
        int runLen = countRunAndMakeAscending(arr, lo, n);

        if (runLen < minRun) {
            int forceLen = (n - lo < minRun) ? (n - lo) : minRun;
            binaryInsertionSort(arr, lo, lo + forceLen - 1, lo + runLen);
            runLen = forceLen;
        }

        runStack[stackSize].base = lo;
        runStack[stackSize].len = runLen;
        stackSize++;

        collapse(arr, runStack, &stackSize, temp);
        lo += runLen;
    }

    forceCollapse(arr, runStack, &stackSize, temp);
    free(temp);
}
