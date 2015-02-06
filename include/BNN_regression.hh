/*!****************************************
   \class BNN_regression
   \brief BNN functional approximation class
   \author Michelle E. Perry
   \date created 25/2/13 updated 9/9/2013
 
*******************************************/

#ifndef _BNN_REGRESSION_H
#define _BNN_REGRESSION_H

#include "HMC_base.h"
#include <iostream>

class BNN_regression : public HMC_base {
 private:
  std::vector<HMC_type> x; //!< training data 
  int H; //!< number of hidden nodes
  int I; //!< number of data inputs 
  int N; //!< number of training events 
  HMC_type sig; //!< standard deviation for priors 
  std::vector<HMC_type> w; //!< training event weights 
  std::vector<HMC_type> t; //!< targets for training data
  std::string oFile; //!< output file name 
  HMC_type diff(std::vector<HMC_type>&, int); //!< neural network function 
  HMC_type LnPrior(std::vector<HMC_type>&); //!< LogPrior function 
  // numbers from Radford Neal code test run sinxcosy
  HMC_type sigb; //!< standard deviation for b parameters
  HMC_type sigv; //!< standard deviation for v parameters
  HMC_type siga; //!< standard deviation for a parameters
  HMC_type sigu; //!< standard deviation for u parameters
 
 public:
  /*! constructor for storing data, targets, and (optional) weights using add() */
  BNN_regression(int l, int nOut_, int nRep_, int nBurn_, int h, int i, std::string s);
  /*! constructor where data, targets, weights are fully stored by user prior to calling contructor*/
  BNN_regression(int l, int nOut_, int nRep_, int nBurn_, int h, int i, std::vector<HMC_type> &data, std::vector<HMC_type>& weights, std::vector<HMC_type> &targets, std::string s); 
  virtual ~BNN_regression();
  /*! probability distribution for a regression neural network */
  virtual HMC_type U(std::vector<HMC_type>&);
  /*! analytical derivative of the probability distribution for a regression neural network */
  virtual std::vector<HMC_type> delU(std::vector<HMC_type>&);

  std::vector<HMC_type> FDdelU(std::vector<HMC_type>&);
  /*! adds to the input, target, and weight array while iterating over each training event  */
  void add(std::vector<HMC_type>& input,HMC_type target, HMC_type weight=1);
};
#endif
