#include <assert.h>
int sum(int* a, int n);

int main(){
    int n = nondet_int();
    int a[n];
    sum(a,n);
    return 0;
}

int sum(int* a, int n){
//    int n = nondet_int();
//    int a[n];
    int sum = 0;
    for (int i=0;i<=n;i=i+1){
        sum += a[i];
    }
    return sum;
}

