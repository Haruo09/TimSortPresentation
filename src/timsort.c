#include "timsort.h"

// define o tamanho de cada run como 32
#define RUN 32

// macro que define o valor mínimo
#define MIN(a, b) (((a) < (b)) ? (a) : (b))

// o insertion sort ordena fatias pequenas do array
static void insertionSort(int arr[], int left, int right) {

    // começa do segundo elemento até o final
    for (int i = left + 1; i <= right; i++) {
        int t = arr[i]; // valor atual
        int j = i - 1;  // índice do elemento anterior

        while (j >= left && t < arr[j]) { // enquanto estiver dentro do array, e o
                                          // valor atual for menor que o anterior
            arr[j + 1] = arr[j];          // copia o valor maior para a casa da direita
            j--;                          // caminha pra trás pra analisar o resto
        }
        arr[j + 1] = t; // aumenta o valor de j (já que j estava como left-1 depois
                        // do while), e coloca o 't' na posição que sobrou
    }
}

// pega dois sub-arrays que estão ordenados e une eles
static void merge(int arr[], int l, int m, int r) {

    // calcula o tamanho dos sub-arrays len1 e len2
    int len1 = m - l + 1, len2 = r - m;

    // cria arrays temporários
    int left[len1], right[len2];

    // copia os dados para os arrays temporários
    for (int i = 0; i < len1; i++)
        left[i] = arr[l + i];
    for (int i = 0; i < len2; i++)
        right[i] = arr[m + 1 + i];

    int i = 0; // índice array esquerda
    int j = 0; // índice array direita
    int k = l; // posição no array original

    // compara os elementos dos array temporários e devolve o menor pro original
    while (i < len1 && j < len2) {

        if (left[i] <= right[j]) {
            arr[k] = left[i];
            i++;
        } else {
            arr[k] = right[j];
            j++;
        }
        k++;
    }

    // se acabou o array da direita, copia os elementos restantes da esquerda
    while (i < len1) {
        arr[k] = left[i];
        k++;
        i++;
    }

    // se acabou o array da esquerda, copia os elementos restantes da direita
    while (j < len2) {
        arr[k] = right[j];
        k++;
        j++;
    }
}

void timSortAlgo(int arr[], int n) {

    // quebra o array em blocos de tamanho RUN (32)
    for (int i = 0; i < n; i += RUN)
        // chama o insertion para ordenar cada bloco
        insertionSort(arr, i, MIN((i + 31), (n - 1)));

    // junta os blocos
    for (int s = RUN; s < n; s = 2 * s) { // s é o tamanho do bloco sendo fundido,
                                          // que vão aumentando de 32 em 32

        for (int left = 0; left < n;
             left += 2 * s) { // percorre o array, combinando os blocos de tamanho s

            int mid = left + s - 1; // encontra o meio da fusão (fim do primeiro
                                    // bloco)

            if (mid >= n - 1)
                continue; // se o meio passou do limite do array original, não tem bloco
                          // da direita pra fundir, entãp pula pro próximo passo

            int right = MIN((left + 2 * s - 1),
                            (n - 1)); // encontra o final da fusão, o limite sendo o final do bloco
                                      // da direita ou o final real do array (o que for menor)

            merge(arr, left, mid, right); // funde a parte esquerda com a direita
        }
    }
}
