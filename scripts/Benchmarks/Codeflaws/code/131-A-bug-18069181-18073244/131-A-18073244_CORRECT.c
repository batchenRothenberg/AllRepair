extern char INPUT1[100];
extern char CORRECT_RES1[100];

#include<string.h>
#include<stdio.h>
#include<ctype.h>
int AllRepair_correct_main(int argc, char *argv[]){
	int x,i,y=0;
	char str[100];
	//scanf("%s",str);
	strcpy(str,INPUT1);
	for(x=0;str[x];x++)
	if(str[x]<=122&&str[x]>=97)
		y++;
		
	if(y==1){
		if(str[0]<=122&&str[0]>=97){
		str[0]=toupper(str[0]);
		for(i=1;str[i];i++){
		str[i]=tolower(str[i]);}
		//printf("%s",str);}
		strcpy(CORRECT_RES1,str);}
	else
		//printf("%s",str);}
		strcpy(CORRECT_RES1,str);}
	else
		if(y==0){
		for(i=0;str[i];i++){
		str[i]=tolower(str[i]);}
		//printf("%s",str);}
		strcpy(CORRECT_RES1,str);}
		
		else{
			//printf("%s",str);}
			strcpy(CORRECT_RES1,str);}
		return 0;}
