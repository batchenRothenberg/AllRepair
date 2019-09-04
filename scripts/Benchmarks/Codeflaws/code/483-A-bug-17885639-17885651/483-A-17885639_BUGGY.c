extern long long int INPUT1;
extern long long int INPUT2;
extern long long int BUGGY_RES1;
extern long long int BUGGY_RES2;
extern long long int BUGGY_RES3;

#include <stdio.h>
int AllRepair_buggy_main(int argc, char *argv[])
{
    long long int l, r, i;
    //scanf("%lld %lld", &l, &r);
    l = INPUT1;
    r = INPUT2;
    if(r-l==1)
        //printf("-1\n");
	{BUGGY_RES1=-1; BUGGY_RES2=-1; BUGGY_RES3=-1;}
    else if(r-l==2)
    {
        if(l%2==1)
            //printf("-1\n");
	    {BUGGY_RES1=-1; BUGGY_RES2=-1; BUGGY_RES3=-1;}
        else 
            //printf("%lld %lld %lld\n", l, l+1, r);
	    {BUGGY_RES1=l; BUGGY_RES2=l+1; BUGGY_RES3=r;}
    }
    else
    {
        if(l%2==1)
            //printf("%lld %lld %lld\n", l+1, l+2, l+3);
    	    {BUGGY_RES1=l+1; BUGGY_RES2=l+2; BUGGY_RES3=l+3;}
        else
            //printf("%lld %lld %lld\n", l, l+1, l+2);
	    {BUGGY_RES1=l; BUGGY_RES2=l+1; BUGGY_RES3=l+2;}
    }
    return 0;
}
