#include "HMC_dist.h"
#include <math.h>
/// U = -ln(P(q))

HMC_type HMC_dist::U(std::vector<HMC_type > &q) {
  
  /// 1D case of HMC_old working example


  if((int)q.size() != 2){
    std::cout << "WARNING: this is a 2D probability distribution and you have more or less than two variables" << std::endl;
  }
  //float u = 0;
  //u = -log(exp(-q[0]*q[0]) + exp(-(q[0]-1)*(q[0]-1)/(0.5*0.5))) ;
  //  u = -log(exp(-0.5*(q[0]*q[0])) + exp(-((q[0]-4)*(q[0]-4)+(q[1]-2)*(q[1]-2)))); 
   // u = -log(exp(-0.5*(q[0]*q[0] + q[1]*q[1])) + exp(-((q[0]-4)*(q[0]-4)+(q[1]-2)*(q[1]-2)))); 
  //std::cout << "u = " << u << std::endl; 
  //return u;
  //for(int i=0; i<1;i++){
  //u = -log(exp(-0.5*q[i]*q[i])+exp(-(q[i]-a)*(q[i]-a)));
  //}
  //return u;
  HMC_type  a = 4.0;
  HMC_type  b = 8.0;
  HMC_type  c = 0;
  HMC_type  siga = 1.0;
  HMC_type  sigb = 1.0;
  HMC_type  sigc = 1.0;
  HMC_type  ta = 0.0;
  HMC_type  tb = 0.0; 
  HMC_type  tc = 0.0;  

  HMC_type u = 0.0;

   for(int i=0;i<getNP();i++){
     // u += -log(exp(-0.5*q[i]*q[i]) + exp(-(q[i]-a)*(q[i]-a)/(2*siga*siga)) + exp(-(q[i]-b)*(q[i]-b)/(2*sigb*sigb)));
     ta += (q[i]-a)*(q[i]-a)/(siga*siga);   
     tb += (q[i]-b)*(q[i]-b)/(sigb*sigb);
     tc += (q[i]-c)*(q[i]-c)/(sigc*sigc);
  //   //std::cout << "U terms: " << ta << "\t" << t2 << "\t" << t3 << std::endl;     
   }
   u = exp(-ta)+exp(-tb)+exp(-tc);
   return -log(u);
  // HMC_type  ya = exp(-0.5*ta);
  // HMC_type  yb = exp(-0.5*tb);
  // HMC_type  yc = exp(-0.5*tc);
  // HMC_type  sum = ya+yb+yc;
  // //std::cout << "sum = " << sum << std::endl; 
  // if(sum == 0) {
  //   return(1e30);
  // }else {
  //   return -log(sum);
  // }




};

std::vector<HMC_type> HMC_dist::delU(std::vector<HMC_type > &q) {
  std::vector<HMC_type > FDdU((int)q.size());
  FDdU = FD(q);


  //  std::vector<float> du((int)q.size());
  //cout << "q in prob delU = " << q[0] << endl;

  //du[0] = (q[0]*exp(-0.5*(q[0]*q[0] + q[1]*q[1]))+2*(q[0]-4)*exp(-((q[0]-4)*(q[0]-4)+(q[1]-2)*(q[1]-2))))/(exp(-0.5*(q[0]*q[0] + q[1]*q[1])) + exp(-((q[0]-4)*(q[0]-4)+(q[1]-2)*(q[1]-2))));
  //du[1] = (q[1]*exp(-0.5*(q[0]*q[0] + q[1]*q[1]))+2*(q[1]-2)*exp(-((q[0]-4)*(q[0]-4)+(q[1]-2)*(q[1]-2))))/(exp(-0.5*(q[0]*q[0] + q[1]*q[1])) + exp(-((q[0]-4)*(q[0]-4)+(q[1]-2)*(q[1]-2))));
  return FDdU;







  // std::cout << "FDdU = ";
  // for(int i=0;i<(int)q.size();i++){  
  //   std::cout << FDdU[i] << "\t";
  // }
  // std::cout << std::endl;

  // HMC_type  a = 4.0;
  // HMC_type  b = 8.0;
  // HMC_type  siga = 2.0;
  // HMC_type  sigb = 0.5;
  // std::vector<HMC_type     > du((int)q.size());
  // //std::cout << "probdU = ";
  // for(int i=0;i<(int)q.size();i++){
  //   du[i] = (q[i]*exp(-0.5*q[i]*q[i]) +(q[i]-a)*exp(-(q[i]-a)*(q[i]-a)/(2*siga*siga))/pow(siga,2) +(q[i]-b)*exp(-(q[i]-b)*(q[i]-b)/(2*sigb*sigb))/pow(siga,2))/(exp(-0.5*q[i]*q[i]) + exp(-(q[i]-a)*(q[i]-a)/(2*siga*siga)) + exp(-(q[i]-b)*(q[i]-b)/(2*sigb*sigb))) ;
  //   //std::cout << du[i] << "\t";
  // }
  // std::cout << std::endl;
  //return du;
  //return FDdU;
}

