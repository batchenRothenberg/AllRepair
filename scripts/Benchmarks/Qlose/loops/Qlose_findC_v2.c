#define N 7

int FindC(char s[], char c, int k){
  for(int i=1; i <= k; i++){
    if (s[i]==c){
      return 1;
	}
  }
  return 0;
}

int AllRepair_correct_FindC(char s[], char c, int k){
  for(int i=0; i <= k; i++){
    if (s[i]==c){
      return 1;
	}
  }
  return 0;
}

int main(){
	char s[N];
	char c = nondet_char();
	int k = nondet_int();
	__CPROVER_assume(k >= 0);
	__CPROVER_assume(k < N);	
	int res1 = FindC(s, c, k);
	int res2 = AllRepair_correct_FindC(s, c, k);
	assert (res1 == res2);
}
	
	
	