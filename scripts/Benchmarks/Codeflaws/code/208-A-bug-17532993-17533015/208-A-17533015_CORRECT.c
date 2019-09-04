extern char INPUT1[500];
extern char CORRECT_RES1[500];

#include<stdio.h>
#include<string.h>

int AllRepair_correct_main(int argc, char *argv[]){
    char dj[500],original[500];
    //scanf("%s",dj);
    strcpy(dj,INPUT1);
    int i,j,n=strlen(dj),flag=1;
    j=0;
    for(i=0;i<n;){
        if(dj[i]=='W'&&dj[i+1]=='U'&&dj[i+2]=='B'){
            i+=3;
            if(flag==0){
                original[j]=32;
                j++;
                flag=1;
            }
        }
        else{
            original[j]=dj[i];
            j++;
            i++;
            flag=0;
        }
    }
    original[j]='\0';
    //printf("%s\n",original);
    strcpy(CORRECT_RES1,original);
    return 0;
}
