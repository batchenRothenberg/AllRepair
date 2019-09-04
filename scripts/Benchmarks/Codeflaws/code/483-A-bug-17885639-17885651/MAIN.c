long long int INPUT1;
long long int INPUT2;
long long int BUGGY_RES1;
long long int CORRECT_RES1;
long long int BUGGY_RES2;
long long int CORRECT_RES2;
long long int BUGGY_RES3;
long long int CORRECT_RES3;

extern int AllRepair_buggy_main(int argc, char *argv[]);
extern int AllRepair_correct_main(int argc, char *argv[]);

#include <assert.h>
#include <string.h>

int main(int argc, char *argv[])
{
  INPUT1 = nondet();
  INPUT2 = nondet();
  AllRepair_buggy_main(argc, argv);
  AllRepair_correct_main(argc, argv);
  assert(BUGGY_RES1==CORRECT_RES1);
  assert(BUGGY_RES2==CORRECT_RES2);
  assert(BUGGY_RES3==CORRECT_RES3);
}
