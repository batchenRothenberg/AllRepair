extern int INPUT1;
extern int BUGGY_RES1;

#include<stdio.h>
//#include<conio.h>

int AllRepair_buggy_main(int argc, char *argv[])
{
    int n;

    //scanf("%d",&n);
    n = INPUT1;

    if(n<2)
    {
        //printf("NO");
	BUGGY_RES1 = 0;
    }
    else
    {
        if(n<=100)
        {
        if(n%2==0) {
        //printf("YES");
	BUGGY_RES1 = 1;
	}
        else {
        //printf("NO");
	BUGGY_RES1 = 0;
	}
        }
        
        else {
        //printf("NO");
	BUGGY_RES1 = 0;
	}
    }

return 0;

}
