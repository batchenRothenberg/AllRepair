extern int INPUT1;
extern int INPUT2;
extern int INPUT3;
extern int BUGGY_RES1;

#include <stdio.h>
#include <stdlib.h>

int AllRepair_buggy_main(int argc, char *argv[])
{
    int a, b,c, ans[8], i, d;
    //scanf("%d", &a);
    a = INPUT1;
    //scanf("%d", &b);
    b = INPUT2;
    //scanf("%d", &c);
    c = INPUT3;
    ans[1]=a+(b*c);
    ans[2]=a*(b+c);
    ans[3]=a*b*c;
    ans[4]=(a+b)*c;
    ans[5]=a+b+c;
    d=ans[1];
    ans[0]=0;
    for(i=0; i!=5; i++)
    {

        if(d<ans[i])
        {
            d=ans[i];
        }
    }
    //printf("%d",d);
    BUGGY_RES1 = d;
    return 0;
}
