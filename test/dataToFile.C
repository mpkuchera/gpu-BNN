#include <fstream>
#include <iostream>
#include <string>
#include <map>
//#include <vector>

#include <TTree.h>
#include <TBranch.h>
#include <TFile.h>


using namespace std;



int main() {

  string ofname="ppZZ_data.txt";
  string paramFile="data/vars.txt";
  //int numParams=73;
  int numParams = 15;

  TFile *f = new TFile("data/ppZZ.root","READ");
  TTree *t = (TTree*)f->Get("Events");
 

  ifstream pFile(paramFile.c_str());
  if(!pFile) {
    printf("cannot open param file\n");
    // exit();
  }
  printf("varsFile open\n");
  string vars[numParams];
  for(int i=0;i<numParams;i++) {
    pFile >> vars[i];
  }
  pFile.close();

  for(int i=0;i<numParams;i++){
    cout << "\"" << vars[i] << "\"" << endl;
    }
  char test;
  cin >> test;
  //CL* c = new CL();

  //cout<<"Created a CL"<<endl;
  
  //map<string,TBranch*> branchMap;
  /* for(int i=0; i<numParams; i++) {
    branchMap[vars[i]] = t->GetBranch(vars[i].c_str());
    } */
  int numEvts = t->GetEntries();
  int everyNiter = 10;
  //numEvts = 100000;
  int storedEvts = (int)numEvts/everyNiter;
  //numParams = 1;
  //numEvts = 100000;
  map<string,Float_t*> V;
  for(int i=0;i<numParams;i++) {
    V[vars[i]] = new Float_t[storedEvts];
  }
  //Float_t temp;

  for(int i=0; i<numParams; i++) {
    for(int j=0,k=0; k<numEvts; j=j++,k=k+everyNiter) {
      t->SetBranchAddress(vars[i].c_str(),&(V[vars[i]][j]));
      t->GetEntry(k);
      // V[vars[i]][j]= temp;
      if(k%10000 == 0) {
	cout << vars[i] << "\t" << "Evt " << k << " of " << numEvts << endl;
      }
    }

  }

  ofstream of(ofname.c_str());
  for(int i=0;i<numParams;i++){
    of << vars[i] << "\t";
    }
  of << endl;
  for(int i=0;i<storedEvts;i++) {
    for(int j=0; j<numParams; j++) {
      of << V[vars[j]][i] << "\t";
    }
    of << endl;
  }
  return 0;
}
