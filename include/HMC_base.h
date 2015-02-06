/*!****************************************
  \class HMC_base 
  \brief Base Hybrid Monte Carlo class

   \author Michelle E. Perry
   \date created 6/6/2013 updated 9/9/2013
 
*******************************************/
#ifndef _HMC_BASE_H
#define _HMC_BASE_H
#include <vector>
#include <string>
#include <fstream>
#include "define_type.h"
//#include "TRandom3.h"

class HMC_base {
  int L; //!< number of steps in one HMC iteration 
  int NP; //!< number of parameters 
  HMC_type Uq0; //!< potential at current point
  int nOut, nRep, nBurn;
  //TRandom3 rand_p;
  std::vector<HMC_type> calc_step(std::vector<HMC_type> &q); //!< calculates step size each HMC iteration 
  std::vector<HMC_type> q; //!< class parameters definition to avoid many re-allocations in loops
  std::vector<HMC_type> q0;
  std::vector<HMC_type> p; //!< class momentum definition to avoid many re-allocations in loops
 public:
 HMC_base(int l, int nParams, int nOut_, int nRep_, int nBurn_) 
   : L(l), 
    NP(nParams), 
    nOut(nOut_),
    nRep(nRep_),
    nBurn(nBurn_),
    q(std::vector<HMC_type>(NP)),
    q0(std::vector<HMC_type>(NP)),
    p(std::vector<HMC_type>(NP)) 
      {}
  virtual ~HMC_base(){};
  std::ofstream of; //!< output file
  int getNP(); //!< getter for NP variable in derived classes
  inline std::vector<HMC_type> it(std::vector<HMC_type> &); //!< one HMC iteration 
  void run();
  virtual HMC_type U(std::vector<HMC_type>&) = 0; //!< calculate U 
  virtual std::vector<HMC_type> delU(std::vector<HMC_type>&) = 0; //!< calculate dU */
};
#endif
