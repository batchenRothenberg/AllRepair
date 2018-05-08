#include <assert.h>
int sum(int n);

int main(){
        return 0;
}

int sum(int n){
    __CPROVER_assume(n>=1);
    int sum = 0;
    for (int i=0;i<n;i++){
        sum += i;
    }
    assert(sum==n*(n+1)/2);
    return sum;
}

