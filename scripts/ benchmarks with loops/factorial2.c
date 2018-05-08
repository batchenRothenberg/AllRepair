#include <stdio.h>
#include <assert.h>

int fact(int x);
int mult(int x,int y);
int fact_correct(int x);

int main(int argc, char* argv[]){
	int n;
     __CPROVER_assume(n>=0);
	int res= fact(n);
	int res2= fact_correct(n);
	assert(res==res2);
	return 0;
}

int fact(int x){
	int res=1;
	for (int i=2 ; i<x; i=1+i){
		res = mult(res,i);
	}
	return res;
}

int mult(int x,int y){
	int res=0;
	for (int i=1 ; i<=y; i=1+i){
		res -= x;
	}
	return res;
}

int fact_correct(int x){
	int res=1;
	for (int i=2 ; i<=x; i=1+i){
		res *=i;
	}
	return res;
}
