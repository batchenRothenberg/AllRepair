int INPUT1;
int BUGGY_RES1;
int CORRECT_RES1;
int BUGGY_RES2;
int CORRECT_RES2;

extern int AllRepair_buggy_main(int argc, char *argv[]);
extern int AllRepair_correct_main(int argc, char *argv[]);

#include <assert.h>
#include <string.h>

int main(int argc, char *argv[])
{
  INPUT1 = nondet();
  AllRepair_buggy_main(argc, argv);
  AllRepair_correct_main(argc, argv);
  assert(BUGGY_RES1==CORRECT_RES1);
  assert(BUGGY_RES2==CORRECT_RES2);
}
