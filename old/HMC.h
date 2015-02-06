#include <vector>

#ifndef HMC_H
#define HMC_H
std::vector<float> HMC(float eps, std::vector<float> q);
std::vector<float> delU(std::vector<float> q);
float U(std::vector<float> q);
#endif
