extern int INPUT1;
extern int INPUT2;
extern int CORRECT_RES1;

#include<stdio.h>
int AllRepair_correct_main(int argc, char *argv[])
{
    int a1,a2,c=0;
    //scanf("%d %d",&a1,&a2);
    a1 = INPUT1;
    a2 = INPUT2;
    if(a1==1 && a2==1)
        c=0;
    else
    {
    while(a1>0 && a2>0)
    {
        if(a1<=a2)
        {
            a1=a1+1;
            a2=a2-2;
        }
        else if(a1>a2)
        {
            a1=a1-2;
            a2=a2+1;
        }
        c++;
    }
    }
    //printf("\n%d",c);
    CORRECT_RES1 = c;
    return 0;
}
