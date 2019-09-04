char INPUT1[500];
char BUGGY_RES1[500];
char CORRECT_RES1[500];

extern int AllRepair_buggy_main(int argc, char *argv[]);
extern int AllRepair_correct_main(int argc, char *argv[]);

#include <assert.h>
#include <string.h>

int main(int argc, char *argv[])
{
  strcpy(INPUT1,nondet());
  AllRepair_buggy_main(argc, argv);
  AllRepair_correct_main(argc, argv);
  assert(strcmp(BUGGY_RES1,CORRECT_RES1)==0);
}
