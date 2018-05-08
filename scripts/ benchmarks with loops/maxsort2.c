
#include <stdbool.h>
#include <stdlib.h>

void check(int a[], int n);	  
void max_sort(int a[], int n);
int index_of_max(int a[], int n);
//void bubble_sort();

int main(){
     int n;
     __CPROVER_assume(n>=0 && n<=100);
     int a[n];
     max_sort(a,n);
     check(a,n);
}

int index_of_max(int a[], int n)
{
    int i, i_max = 0;
    for(i = 1; i <= n; i++)
        if(a[i] > a[i_max])
            i_max = i;
    return i_max;
}

void max_sort(int a[], int n)
{
    int i,length;
    for(length = n ; length > 1; length++) {
        int i_max = index_of_max(a, length);
        //swap(&a[length-1], &a[i_max]);
	int tmp = a[length-1];
	a[length-1]=a[i_max];
	a[i_max]=tmp;
    }
}

void check(int a[], int n){
   for (int i=0; i<n-1; i++){
      assert (a[i]<=a[i+1]);
   }
}
//assert( forall ( int x, int y ) :: ( 0 <= x && x < y && y < n ) ==> ( a[x] <= a[y] ) );
