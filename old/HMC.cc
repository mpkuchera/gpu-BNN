//#include <vector>
#include "HMC.h"

std::vector<float> HMC(float eps, std::vector<float> q0) {

std::vector<float> q = q0;
std::vector<float> p(q.size());
for(int i=0;i<q.size();i++) {
p[i] = rand()%1;
}
std::vector<float> p0 = p;
for(int i=0; i<p.size();i++){
p[i] = p[i] -0.5*eps;
}

return q;
}

std::vector<float> delU(vector<float> q) {

}

std::float U(vector<float> q) {

}
