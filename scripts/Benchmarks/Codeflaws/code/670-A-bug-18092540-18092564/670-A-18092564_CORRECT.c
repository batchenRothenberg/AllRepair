extern int INPUT1;
extern int CORRECT_RES1;
extern int CORRECT_RES2;

#include<stdio.h>

int AllRepair_correct_main(int argc, char *argv[]){
	int n,a,b;
	//scanf("%d",&n);
	n = INPUT1;
	if((n>=1)&&(n<=1000000)){
		a=n/7;
		b=n%7;
		if(b==0){
			a=a*2;
			b=a;
			//printf("%d %d",a,b);
			CORRECT_RES1 = a;
			CORRECT_RES2 = b;
		}
		else if(b==1){
			a=a*2;
			b=a+1;
			//printf("%d %d",a,b);
			CORRECT_RES1 = a;
			CORRECT_RES2 = b;
		}
		else if((b==2)||(b==3)||(b==4)||(b==5)){
			a=a*2;
			b=a+2;
			//printf("%d %d",a,b);
			CORRECT_RES1 = a;
			CORRECT_RES2 = b;
		}
		else if(b==6){
			a=a*2;
			b=a+2;
			//printf("%d %d",a+1,b);
			CORRECT_RES1 = a+1;
			CORRECT_RES2 = b;
		}
	}
return 0;
}
