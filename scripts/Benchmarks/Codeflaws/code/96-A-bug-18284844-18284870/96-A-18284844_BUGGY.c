extern char INPUT1[100];
extern int BUGGY_RES1;

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
/*
int main(int argc, char *argv[])
{ char s[100];
int count=1,i;
    scanf("%s",s);
    for(i=0;i<strlen(s)-1;i++){
     if(s[i]==s[i+1]){
        count++;
         if(count>=7){

                break;
            }
     }
     else {

        count=1;
     }

    }
    if(count<7){
        printf("NO");
    }
    else
        printf("YES");
    return 0;
}*/

int AllRepair_buggy_main(int argc, char *argv[]){
    int i,count=1;
    char s[100];
    //scanf("%s",s);
    strcpy(s,INPUT1);
    for(i=0;i<strlen(s)-1;i++){
        if(s[i]==s[i+1]){
            count++;
        }
        else {
                if(count>=7)
                 break;
               else {
                count=0;
               }
        }
    }

    if(count>=7)
        //printf("YES\n");
	BUGGY_RES1 = 1;
    else //printf("NO\n");
	BUGGY_RES1 = 0;
return 0;}

