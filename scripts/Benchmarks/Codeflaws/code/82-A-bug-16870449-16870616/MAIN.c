long long int INPUT1;
char BUGGY_RES1[10];
char CORRECT_RES1[10];

extern int AllRepair_buggy_main(int argc, char *argv[]);
extern int AllRepair_correct_main(int argc, char *argv[]);

#include <assert.h>
#include <string.h>

int main(int argc, char *argv[])
{
  INPUT1 = nondet();
  AllRepair_buggy_main(argc, argv);
  AllRepair_correct_main(argc, argv);
  assert(strcmp(BUGGY_RES1,CORRECT_RES1)==0);
}
