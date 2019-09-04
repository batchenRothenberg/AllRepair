extern int INPUT1;
extern int BUGGY_RES1;

#include<stdio.h>
int AllRepair_buggy_main(int argc, char *argv[])
{
    int arr[10]={2,7,2,3,3,3,2,5,1,2};
    int n;
    //scanf("%d",&n);
    n = INPUT1;
    int r=n%10;
    n=n/10;
    int ans=arr[n]*arr[r];
    //printf("%d\n",ans);
    BUGGY_RES1 = ans;
    return 0;
}
