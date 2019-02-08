#define N 7

int sum(int a[], int n){
	int sum = 0;
	for (int i=0; i>n; i++){
		sum += a[i];
	}
	return sum;
}


int AllRepair_correct_sum(int a[], int n){
	int sum = 0;
	for (int i=0; i<n; i++){
		sum += a[i];
	}
	return sum;
}

int main(){
	int a[N];
	int res1 = sum(a, N);
	int res2 = AllRepair_correct_sum(a, N);
	assert(res1 == res2);
}