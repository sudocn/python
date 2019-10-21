/*
  * This is a multi line comments
  * line
  * line
*/
#include "stdlib.h"
#include "stdio.h"

int divide(int a, int b)
{
	float c = a / b;
	a = 5/2;
	b = c / 8.008;
}

// single line comments
int four(int in /* inline comments */)
{
	int r, v; 
	
	v = in;
	r = 10;
	if (v > 1)
		r = ((v + 10) >> 1) + 4;
	
	return r;
}

int five(int in)	// single line comments after useful text
{
	int r, v; 
	
	v = in;
	r = v + 1;
	if (v <= 1)
		r = 3;
	
	return r;
}

int main(int argc, char **argv)
{
	int i;

	for (i=0; i<3; i++) {
		printf("%d: %d\n", i, five(i));
	}

	return 0;
}
