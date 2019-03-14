#include "templateSrc.h"
#include <random>
#include <unistd.h>

Stub::Stub()
{
    std::random_device rd;
    std::mt19937 eng(rd());
    std::uniform_int_distribution<> distr(100000, 1000000);
    usleep(distr(eng));
}


Stub::~Stub()
{
}
