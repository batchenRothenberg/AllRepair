
int multIA(int m, int n){
    int result = 0;
    for(int i=0; i<=n+1; i++){
    	    result += m;
    }
    return result;
}

int AllRepair_correct_multIA(int m, int n){
    int result = 0;
    for(int i=0; i<=n-1; i++){
    	    result += m;
    }
    return result;
}

int main(){
	int m = nondet_int();
	int n = nondet_int();
	int res1 = multIA(m, n);
	int res2 = AllRepair_correct_multIA(m, n);
	assert(res1 == res2);
}