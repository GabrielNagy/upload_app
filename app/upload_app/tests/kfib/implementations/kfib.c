#include <stdio.h>
#include <string.h>
#define mod 666013
typedef long long ll;

void Multiply(ll A[2][2], ll B[2][2], ll C[2][2]) {
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            for (int k = 0; k < 2; k++) {
                C[i][j] = (C[i][j] + 1LL *A[i][k] * B[k][j]) % mod;
            }
        }
    }
}

ll Log_pow(ll p) {
    if (p == -1) return 0;
    ll Ans[2][2] = { {1, 0}, {0, 1} };
    ll Aux[2][2] = { {0, 0}, {0, 0} };
    ll Mat[2][2] = { {0, 1}, {1, 1} };
    while (p > 0) {
        if (p & 1LL) {
            memset(Aux, 0, sizeof(Aux));
            Multiply(Ans, Mat, Aux);
            memcpy(Ans, Aux, sizeof(Ans));
        }
        memset(Aux, 0, sizeof(Aux));
        Multiply(Mat, Mat, Aux);
        memcpy(Mat, Aux, sizeof(Mat));
        p = p >> 1LL;
    }
    return Ans[1][1];
}

int main() {
    FILE *fin = fopen("kfib.in", "r");
    FILE *fout = fopen("kfib.out", "w");
    ll n;
    fscanf(fin, "%lld", &n);
    ll ans = Log_pow(n - 1);
    fprintf(fout, "%lld", ans);
    fclose(fin);
    fclose(fout);
    return 0;
}
