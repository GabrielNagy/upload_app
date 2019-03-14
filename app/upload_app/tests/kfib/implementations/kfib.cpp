#include <fstream>
using namespace std;
 
ifstream fin("kfib.in");
ofstream fout("kfib.out");
 
const int MOD = 666013;
int Z[2][2],Sol[2][2],K;
 
void Multiply(int A[2][2], int B[2][2])
{
  long long C[2][2];
  for(int i = 0; i < 2; ++i)
    for(int j = 0; j < 2; ++j)
      {
          C[i][j] = 0;
          for(int k = 0; k < 2; ++k)
            C[i][j] += 1LL * A[i][k] * B[k][j];
          C[i][j] %= MOD;
      }
  for(int i = 0; i < 2; ++i)
    for(int j = 0; j < 2; ++j)
      A[i][j] = C[i][j];
}
 
 
int main()
{
    fin >> K;
    Z[0][1] = Z[1][0] = Z[1][1] = 1;
    Sol[0][1] = 1;
    while(K)
    {
      if(K%2 == 1)
        Multiply(Sol,Z);
      Multiply(Z,Z);
      K = K / 2;
    }
 
    fout << Sol[0][0] << "\n";
 
    return 0;
}
