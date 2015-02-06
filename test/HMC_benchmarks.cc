#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
//#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <time.h>

//#include <stdlib>
#include "BNN_regression.cuh"


using namespace std;
//float* getData(string);

int main() {

  // cout << "In HMC_Z2.cc" <<endl;
  int nBurn = 0;
  int nOut = 200;
  int nRep = 1;

  int L = 100;
  int dim = 6;

  int H = 10;

  string filename = "data/Z2mass.dat";
  //  float* data = getData(dataFile);
  //int evts = 100;
  string line;
  ifstream datafile(filename.c_str());
  if(!datafile){
    cout << "ERROR: data file not found" << endl;
  }
  

  int nTrain = 2000;
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
  cout << "x = " << x[0] << "\t" << x[1]  << "\t" <<  x[2] << endl;
  cout << x[3] << "\t" << x[4]  << "\t" <<  x[5] << endl;
  cout << "t[0] = " << t[0] << endl;

  string outFile = "results/bench_3_14.txt";
  string timeFile = "benchmark_3_14_no_wrap.txt";
  clock_t start, end;

  //  start = clock();
  BNN_regression BNN(L, nOut, nRep, nBurn, H, dim, x, w, t, outFile);
  start = clock();
  BNN.run();
  end = clock();
  
  ofstream of;
  of.open(timeFile.c_str());
  of << "I\tH\tL\tnTrain\tnOut\ttime\n";
  of << dim << "\t" << H << "\t" << L <<"\t" << nTrain << "\t" << nOut << "\t" <<  double(end-start)/CLOCKS_PER_SEC << endl;

  of.close();
  cout << "results written to " << timeFile << endl;
  cout << "execution time of BNN() = " << double(end-start)/CLOCKS_PER_SEC << " seconds" << endl;

  return 0;
}
