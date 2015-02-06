/*!*
  general outline of main function for probability
  distributions.

  started 21/2/2013 by Michelle E. Perry

  to aid in programming rest of BNN elements.
**/
#include <fstream>
#include <iostream>
#include <time.h>
#include <string>
#include "HMC_dist.h"

using namespace std;

int main() {
  //int nSample = 100000;

  //float eps = 0.05;
  int L = 100;
  int dim = 2;
  int nOut = 50000;
  int nRep = 10;
  int nBurn = 50000;
  /* We want to keep many of these parameter sets, so store in array */
  //vector<vector<float> > Q(nSample);
  vector<float> q(dim);
  vector<float> q0(dim);  
;
  /** Construct type of HMC object we want (probDist, BNN_classify, BNN_function) **/
  HMC_dist HMC(L,dim,nOut,nRep,nBurn);
  string outFile = "results/2D_10_5_2013.txt";

  HMC.run(outFile);
  
  return 0;
}
