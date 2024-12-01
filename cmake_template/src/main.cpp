#include "multi.h"
#include "add.h"
#include "sum.h"
#include<iostream>

int main(int argc, const char** argv) {
    int a =10;
    int b =20;
    int ab[2]={10,30};
    std::cout << add(a,b)<<std::endl;
    std::cout<< sum(ab,2) <<std::endl;
    std::cout<< multi(a,b) <<std::endl;

}