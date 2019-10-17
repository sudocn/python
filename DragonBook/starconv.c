#include "stdlib.h"
#include "stdio.h"

int four(int in)
{
	int r, v; 
	
	v = in;
	r = 10;
	if (v > 1)
		r = ((v + 10) >> 1) + 4;
	
	return r;
}

int five(int in)
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
