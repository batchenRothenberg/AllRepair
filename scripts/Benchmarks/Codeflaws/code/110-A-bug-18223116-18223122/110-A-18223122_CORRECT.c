extern char INPUT1[100];
extern int CORRECT_RES1;

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int AllRepair_correct_main(int argc, char *argv[]) {
	int i,j,n,dem=0;
	char s[100];
	//gets(s);
	strcpy(s,INPUT1);
	for(i=0;s[i] != NULL;i++){
		if((s[i] == '4') || (s[i] == '7')){
			dem++;
		}
	}
	if((dem == 4) || (dem == 7))
	//printf("YES");
	CORRECT_RES1 = 1;
	else
	//printf("NO");
	CORRECT_RES1 = 0;
	return 0;
}
