import java.io.*;
 
public class Main {
 
    private static final long[] A = new long[]{0, 1, 1, 1};
    private static final long[] I = new long[]{1, 0, 0, 1};
    private static final int MOD = 666013;
 
    public static void main(String[] args) throws IOException {
        BufferedReader bufferedReader = new BufferedReader(new FileReader("kfib.in"));
        int n = Integer.parseInt(bufferedReader.readLine());
 
        long[] result = computePower(n);
 
        BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter("kfib.out"));
        bufferedWriter.write(String.valueOf(result[1]));
 
        bufferedReader.close();
        bufferedWriter.close();
    }
 
    private static long[] computePower(int n) {
        if (n == 1)
            return A;
        if (n == 0)
            return I;
        if (n % 2 == 1) {
            long[] res = computePower((n - 1) / 2);
            return multiply(A, multiply(res, res));
        }
        long[] res = computePower(n / 2);
        return multiply(res, res);
    }
 
    private static long[] multiply(long[] A, long[] B) {
        long[] C = new long[4];
        C[0] = (A[0] * B[0] % MOD + A[1] * B[2] % MOD) % MOD;
        C[1] = (A[0] * B[1] % MOD + A[1] * B[3] % MOD) % MOD;
        C[2] = (A[2] * B[0] % MOD + A[3] * B[2] % MOD) % MOD;
        C[3] = (A[2] * B[1] % MOD + A[3] * B[3] % MOD) % MOD;
 
        return C;
    }
}
