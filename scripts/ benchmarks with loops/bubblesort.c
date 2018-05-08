
#include <stdbool.h>
#include <stdlib.h>

void check(int a[], int n);	  
void bubble_sort( int a[], int n );
//void bubble_sort();

int main(){
     int n;
     __CPROVER_assume(n>=0 && n<=100);
     int a[n];
     bubble_sort(a,n);
}

void bubble_sort(int a[], int n) {
  //int n=5;
  //__CPROVER_assume(n>=0 && n<=100);
  //int a[5];
  bool swapped = true;
  while ( swapped ) {
    swapped = false;
    int i = 1;
    while ( i <= n ) { 
      if ( a[i - 1] > a[i] ) { 
        int t = a[i];
        a[i] = a[i - 1];
        a[i-1] = t;
        swapped = true;
      }
      i = i + 1;
    }
  }
  check(a,n);
}

void check(int a[], int n){
   for (int i=0; i<n-1; i++){
      assert (a[i]<=a[i+1]);
   }
}
//assert( forall ( int x, int y ) :: ( 0 <= x && x < y && y < n ) ==> ( a[x] <= a[y] ) );
