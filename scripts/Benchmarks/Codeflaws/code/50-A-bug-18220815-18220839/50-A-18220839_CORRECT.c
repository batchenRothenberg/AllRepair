extern int INPUT1;
extern int INPUT2;
extern int CORRECT_RES1;

#include <stdio.h>
#include <stdlib.h>
int m,n,area;
int AllRepair_correct_main(int argc, char *argv[])
{
   //scanf("%d %d",&m,&n);
   m = INPUT1;
   n = INPUT2;
   if (1<=m&&m<=n&&n<=16){
    area =m*n;
    //printf("%d",area/2);
    CORRECT_RES1 = area/2;
   }
    return 0;
}
