#include <stdio.h>
#include <assert.h>

int f(int x, int y);

int main(int argc, char* argv[]){
	return f(2,3);
}

int sum(int w, int t){
	return w+t;
}

int f(int x, int y){
	__CPROVER_assume(x>=-1000 && x<=1000 && y>=-1000 && y<=1000);
	int z;
	if (x+y>8){
		z = sum(x,y);
	}else{
		z = 9;
	}
	while (x>0){
		z+=x;
		x-=3;
	}
	if (z>=9) z--; //should be >9 or z++
	assert(z>8);
	return z;
}
