extern char INPUT1[210];
extern char CORRECT_RES1[210];

#include<stdio.h>
#include<string.h>

int AllRepair_correct_main(int argc, char *argv[])
{
    char arry[210], ans[210];
    int len, i, j;

    //gets(arry);
    strcpy(arry,INPUT1);

    len = strlen(arry);

    for(i=0, j=0; i<len;) {
        if(arry[i]=='W' && arry[i+1]=='U' && arry[i+2]=='B') {
            i+=3;
            if(j!=0 && ans[j-1]!=' ') ans[j++] = ' ';
        }
        else {
            ans[j] = arry[i];
            j++;
            i++;
        }
    }
    ans[j] = '\0';
    //printf(ans);
    strcpy(CORRECT_RES1,ans);

    return 0;
}
