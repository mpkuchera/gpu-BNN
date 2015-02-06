#include <cmath>
#include <cassert>
#include "HMC_base2.h"
#include "define_type.h"
#include <iostream>
#include <string>
#include <fstream>


// inline std::vector<HMC_type> HMC_base::calc_step(HMC_type* q){
//   HMC_type h = 0.01;
//   std::vector<HMC_type> qpm = q;
//   //std::vector<HMC_type> qm = q;
 
//   std::vector<HMC_type> eps(NP); 
//   HMC_type v;
//   HMC_type factor = 1e-1;
//   Uq0 = U(q);
//   HMC_type Uq = Uq0;
//   HMC_type h2 = 2*h;
//   HMC_type hh = h*h;
//   //std::cout << "eps = ";
//   for(int i=0;i<NP;i++){
//     qpm[i] += h;
//     // qm[i] -= h;
//     v = U(qpm) -2*Uq;
//     qpm[i] -= h2;
//     v += U(qpm);
//     v = fabs(v)/hh;
//     qpm[i] += h;
//     // v = fabs(U(qp) - 2*Uq + U(qm))/(h*h);
//     //std::cout << "Us: " << U(qp) << "\t" << U(qm) << "\t" << U(q) << std::endl;
//     //std::cout << "v = " << v << std::endl;
//     if(v == 0) {
//       std::cout << "!!!!!!!! v = 0 !!!!" << std::endl;
//     }
//     ///////TEST///////////
//     eps[i] = factor*sqrt(1.0/(v+0.0001));
//     //eps[i] = 0.05;
//     //std::cout << eps[i] << "\t";
//     if(eps[i] > 1) {
//       std::cout << "MAX EPS" << std::endl;
//       eps[i] = 1;
//     } 

//     if(eps[i] < 1e-6) {
//       // std::cout << "MIN EPS" << std::endl;
//       //eps[i] = 1e-6;
//     }
//     //qp[i] -= h;
//     //qm[i] += h;
//    //eps[i] = 0.05; //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//   }
//   //std::cout << std::endl;
//   return eps;

// };

//NOTE: can not inline this function
inline HMC_type* HMC_base::it(HMC_type* q0) {

  HMC_type eps[NP];
  //eps = calc_step(q0); /*!< Uq0 calculated in this function */
  std::cout << "HERE" << std::endl;
  Uq0 = U(q0);
  std::cout << "Uq0 = " <<  Uq0 << std::endl;
  
//!!!!!!!!!!!!!!!
   for(int i=0;i<NP;i++){
     eps[i] = 0.001;
   }
  //!!!!!!!!!
  HMC_type* dU = new HMC_type[NP]; 
  //std::vector<HMC_type> FDdU((int)q0.size()); 
  //std::cout << "q0 in HMC_base = " << q0[0] << std::endl;

  q = q0;
     for(int j=0;j<NP;j++){
       std::cout << q[j] << "\t";
      }
     std::cout << std::endl;
  //std::vector<HMC_type> p(q.size());
  //std::cout << "NP = " << NP << std::endl;
  p = new HMC_type[NP];
  //assert((int)p.size() == NP);
  
  for(int i=0;i<NP;i++) {
    p[i] = rand_p.Gaus();
    //p[i] = 0.5;
    //std::cout << i << "\t";
    //std:: cout << p[i] << "\t";
  }
  //std::cout << std::endl;

  // good to here for p and q and Uq0!

  HMC_type* p0 = new HMC_type[NP];
  p0 = p;
  std::cout << "here in HMC_base2" << std::endl;
  // 1/2 step in momentum
  dU = delU(q);
  std::cout << "in it() dU = ";
  for(int j=0;j<NP;j++){
    std::cout << dU[j] << "\t";
  }
  std::cout << std::endl;


  for(int i=0; i<NP;i++){
    p[i] = p[i] - 0.5*eps[i]*dU[i];
    if(p[i] != p[i]){
      std::cout << p[i] << std::endl;
      assert(0);
    }
    //std::cout << "dU[i] = " << dU[i] << std::endl;
  }
  
  for(int i=0;i<L;i++){
    //std::cout << "i = " << i << std::endl;
    // 1 step in position
    //std::cout << "p[0] = " << p[0] << std::endl; 
    for(int j=0;j<NP;j++) {
      q[j] = q[j] + eps[j]*p[j];
      // std::cout << "i = " << i << "  q[" << j << "] = " << q[j] << std::endl;
    }
    std::cout<< "here" << std::endl;
    dU = delU(q); 
    // std::cout << "dU[0] = " << dU[0] << std::endl;
    // 1 step in momentum, except at the end
    if(i != (L-1)){
      for(int j=0;j<NP;j++) {
	p[j] = p[j] - eps[j]*dU[j];
	if(dU[j] != dU[j]){
	   std::cout << "dU[" << j << "] = " << dU[j] << std::endl;
	  assert(0);
	}
      }
    }
  }
  // 1/2 step in momentum
  dU = delU(q);
  for(int i=0; i<NP;i++){
    p[i] = p[i] - 0.5*eps[i]*dU[i];
    if(p[i] != p[i]){
      assert(0);
    }
    //std::cout << "p[i] = " << p[i] << std::endl;
  }
 // to symmetrize momentum ?????
  for(int i=0; i<NP;i++){
    p[i] = -p[i];
    if(p[i] != p[i]){
      assert(0);
    }
  }


  //std::cout << "p[0] = " << p[0] << std::endl;
  //std::cout << "q[0] = " << q[0] << std::endl;
  //std::cout << std::endl;
  // Calculate original and new U & K
  HMC_type Uc = U(q0);
  //std::cout << "Uc = " << Uc << std::endl;
  HMC_type Un = U(q);
  //std::cout << "Un = " << Un << std::endl;


  HMC_type Kc = 0;
  for(int i=0;i<NP;i++){
    Kc += 0.5*p0[i]*p0[i];
  } 
  //std::cout << "Kc = " << Kc << std::endl;

  HMC_type Kn = 0;
  for(int i=0;i<NP;i++){
    Kn += 0.5*p[i]*p[i]; 
  } 
  //std::cout << "Kn = " << Kn << std::endl;
  // accept or reject?
  HMC_type f = exp(Uc-Un+Kc-Kn);
 
  //std::cout << "exp(Uc-Un+Kc-Kn) = " << f << std::endl;
  HMC_type rndm =  (HMC_type)rand()/(HMC_type)RAND_MAX;
  
   //std::cout << "rndm = " << rndm << std::endl;
   /*if(Uc + Kc > Un + Kn) {
    //std::cout << "exp(Uc-Un+Kc-Kn) = " << f << std::endl << "in it() q = ";
    //for(int j=0;j<(int)q0.size();j++){
    //std::cout << q[j] << "\t";
    //}
    //std::cout << std::endl;
    std::cout << "condition 1" << std::endl;
    return q; ///reject
    
  } else
   */ 
   if(rndm < f) {

    //char test;
    //std::cout << "no change" << std::endl;
    //std::cin >> test;
    //std::cout << "condition 2" << std::endl;
    return q;   //accept
  } else {
     // std::cout << "condition 3" << std::endl;
    return q0; //reject
  }
};
int HMC_base::getNP() {
  return NP;
};
void HMC_base::run(){
  std::cout << "nBurn = " << nBurn << " nRep = " << nRep << " nOut = " << nOut << std::endl;
  int nIter = nBurn + nRep*nOut;
  //vector<vector<float> > Q(nIter);
  
  //vector<float> q(nParams);
  //vector<float> q0(nParams);
  // cout << "before q define" << endl;
  q = new HMC_type[NP];
  for(int i=0;i<NP; i++){  
    // cout << "i = " << i << endl << endl;
    //cout << rand()/float(RAND_MAX) << endl;
    //q[i] = 2.0*((float)rand()/float(RAND_MAX))-1;
    q[i] = rand_p.Gaus();
    //q[i] = 0.5;
    //std::cout << "i = " << i << std::endl;
  }
  
  //std::ofstream of(s.c_str(),std::ofstream::out);
  //of.open();
  //int accept = 0;
  //of << I << "\t" << H << std::endl;
  for(int i=0; i<nIter; i++){
    q0 = q;

    q = it(q0);
     for(int j=0;j<NP;j++){
       std::cout << q0[j] << "\t";
      }
     std::cout << std::endl;
    //std::cout << "FINAL Q!" << "\t";
    //for(int j=0;j<(int)q.size();j++){
    //std::cout << q[j] << "\t";
    //}
    //std::cout << std::endl;
    //int dummy;
    //std::cin >> dummy;
    if(i%100==0){
      std::cout << "i = " << i << std::endl;
    }
    if(i>=nBurn && i%nRep==0){
      for(int j=0;j<NP;j++){
	of << q[j] << "\t";
      }
      of << std::endl;
    }
  }
};

