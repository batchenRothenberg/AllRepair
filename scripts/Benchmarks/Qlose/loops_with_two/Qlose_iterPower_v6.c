
int iterPower(int base, int exp){
    int result = 1;
    while(exp==1){
		result *= base;
		exp -= 2;
    }
    return result;
}

int AllRepair_correct_iterPower(int base, int exp){
    int result = 1;
    while(exp>=1){
		result *= base;
		exp -= 1;
    }
    return result;
}

int main(){
	int base = nondet_int();
	int exp = nondet_int();
	int res1 = iterPower(base, exp);
	int res2 = AllRepair_correct_iterPower(base, exp);
	assert (res1 == res2);
}