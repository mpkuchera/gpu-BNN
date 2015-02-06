#include <iostream>
//#include <stdlib>
#include "HMC.h"

using namespace std;

int main() {
  int nSample = 1000;
  float eps = 0.01;
  int dim = 1;
  vector<vector<float> > Q(nSample);
  vector<float> q(dim);
  cout << "before q define" << endl;
  for(int i=0;i<dim; i++){  
    cout << "i = " << i << endl << endl;
    cout << rand()/float(RAND_MAX) << endl;
    q[i] = rand()/float(RAND_MAX);
    cout << "i = " << i << endl << endl;
  }
 cout << "after q define" << endl;
  Q[0] = q;
  cout << "before nSample loop" << endl << endl;
  for(int i=1; i<nSample; i++){
    if(i%100 == 0 || i==1){
      cout << "i = " << i << endl;
    }   
    Q[i] = HMC(eps, Q[i-1]);

  }

  return 0;
}
