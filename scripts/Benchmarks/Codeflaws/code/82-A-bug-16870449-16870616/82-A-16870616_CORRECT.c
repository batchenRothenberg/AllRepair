extern long long int INPUT1;
extern char CORRECT_RES1[10];

#include<stdio.h>
#include<stdlib.h>
#include <string.h>

int AllRepair_correct_main(int argc, char *argv[])
{
	long long int n,sum=0,i=1;
	//scanf("%lld",&n);
	//scanf("%lld",&n);
	n = INPUT1;
	i=1;
	while(1)
	{
		sum=sum+ (5*i);
		
		if(sum>=n)
		{
        break;
		}
		i*=2;
	}
	n=n-sum+ (5*i);
	long long int p=n%i;
	n=n/i;
	if(p!=0)
	   n=n+1;
	
	if(n==1)
	   //printf("Sheldon\n");
	   strcpy(CORRECT_RES1,"Sheldon\n");
	if(n==2)
	   //printf("Leonard\n");
	   strcpy(CORRECT_RES1,"Leonard\n");
	if(n==3)
	   //printf("Penny\n");
	   strcpy(CORRECT_RES1,"Penny\n");
	 if(n==4)
	   //printf("Rajesh\n");
	   strcpy(CORRECT_RES1,"Rajesh\n");
	 if(n==5)
	   //printf("Howard\n");
	   strcpy(CORRECT_RES1,"Howard\n");
	 return 0;  
}
