#include "utils.h"
#include <stdio.h>

// função apenas para imprimir o array na tela
void printArray(int *arr, int n) {
    for (int i = 0; i < n; i++)
        printf("%d ", arr[i]);
    printf("\n");
}
