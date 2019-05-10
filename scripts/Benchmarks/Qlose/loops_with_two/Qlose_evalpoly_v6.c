#define N 7


int pow(int x, int i){
	int res = 1;
	for (int j=-1; j<i; j++){
		res = res * x;
	}
	return res;
}

int AllRepair_correct_pow(int x, int i){
	int res = 1;
	for (int j=0; j<i; j++){
		res = res * x;
	}
	return res;
}

int evalPoly(int p[], int n, int x){
    int num = 0;
    int i = 1;
    while (i <= n - 1){
        num += p[i]*pow(x,i) ;
        i = i + 1;
    }
    return num;
}

int AllRepair_correct_evalPoly(int p[], int n, int x){
    int num = 0;
    int i = 0;
    while (i <= n - 1){
        num += p[i]*AllRepair_correct_pow(x,i) ;
        i = i + 1;
    }
    return num;
}

int main() {
	int p[N];
	int x = nondet_int();
	int res1 = evalPoly(p, N, x);
	int res2 = AllRepair_correct_evalPoly(p, N, x);
	assert (res1 == res2);
}
