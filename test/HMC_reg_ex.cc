#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
//#include <cstdlib>
#include <cstdio>
#include <cmath>
//#include <stdlib>
#include "BNN_regression.cuh"


using namespace std;
//float* getData(string);

int main() {

  cout << "In HMC_reg_ex.cc" <<endl;
  int nBurn = 100;
  int nOut = 100;
  int nRep = 10;

  int L = 100;
  int dim = 2;

  int H = 8;

  string filename = "data/train.dat";
  //  float* data = getData(dataFile);
  //int evts = 100;
  string line;
  ifstream datafile(filename.c_str());
  if(!datafile){
    cout << "ERROR: data file not found" << endl;
  }
  

  int nTrain = 1000;
  vector<float> x(dim*nTrain);
  // cout << "data array memory allocated." << endl;
  int row = 0;
  int ind = -10;

  string dummy;
  getline(datafile, dummy);
  vector<float> t(nTrain);
  vector<float> w(nTrain);
  // cout << "t and w allocated." << endl;
  //int nOut = 5000;
  //int nRep = 20;
  //int nBurn = 5000;
  //! parsing data file and storing training events

  while(datafile.good() && row < nTrain){
    getline(datafile,line);
    stringstream ss(stringstream::in | stringstream::out);
    ss << line;
    for(int j=0; j<dim;j++) {
      ind = (dim)*row+j;
      ss >> x[ind];
    }
    ss >> t[row];
    w[row] = 1;
    row++;
  }
  datafile.close();
  cout << "data copied into array" << endl;
  cout << "x[0] = " << x[0] << "\t x[1] = " << x[1] << endl;
  cout << "t[0] = " << t[0] << endl;

  string outFile = "results/reg_12_9_13.txt";

  BNN_regression BNN(L, nOut, nRep, nBurn, H, dim, x, w, t, outFile);
  BNN.run();

}
