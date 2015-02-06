/*!*****************************************
  \class HMC_dist 
  \brief probability distribution class
  \author Michelle E. Perry
  \date created 21/2/13 updated
 
*******************************************/
#ifndef _HMC_DIST_H
#define _HMC_DIST_H
#include "define_type.h"
#include "HMC_base.h"
#include <iostream>


class HMC_dist : public HMC_base {
 public:
 HMC_dist(int l, int nParams, int nOut_, int nRep_, int nBurn_) : HMC_base(l,nParams,nOut_,nRep_,nBurn_){
    std::cout << "This is HMC with a user-defined probability distribution." << std::endl << "Make sure your U is defined in src/HMC_dist.cc" << std::endl;
    //HMC_type rand;
    //std::cin >> rand;
  };

  virtual HMC_type U(std::vector<HMC_type>&);
  virtual std::vector<HMC_type> delU(std::vector<HMC_type> &);
  std::vector<HMC_type> FD(std::vector<HMC_type> &q){  
    HMC_type h = 0.001;
    std::vector<HMC_type> dU((int)q.size());
  
    for(int i=0; i<getNP();i++){
      // std::cout << "q[" << i << "] = " <<  q[i] << "\t"; 
      std::vector<HMC_type> qm = q;
      std::vector<HMC_type> qp = q;
      qm[i] = qm[i] - h;
      qp[i] = qp[i] + h;
      dU[i] =  (U(qp) - U(qm))/(2*h);
      //  std::cout << "numerator: " <<   (U(qp) - U(qm)) << "\t";
      //std::cout << "U(qp) = " << U(qp) << "\t" << "U(qm) = " << U(qm) << " ";
    }
    //std::cout << std::endl;

    return dU;
  };
};
#endif
