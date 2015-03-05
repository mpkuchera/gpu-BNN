/*!****************************************
  \file BNN_regression.cc
 
  \author Michelle E. Perry
  \date created 25/2/2013 updated 9/9/2013
*******************************************/

#include "BNN_regression.cuh"
#include <math.h>
#include <iostream>
#include <iomanip>
#include <cassert>
//#include <thrust/host_vector.h>
//#include <thrust/device_vector.h>
#include <thrust/device_ptr.h>
#include <thrust/reduce.h> /// thrust parallel reduce
#include <thrust/device_free.h>

/*!**
NN PARAMETERS
q[0] = b;
q[j+1] = v_j;
q[H+j+1] = a_j
q[2H+1+i+j*I] = u_ji
 ****/


__global__ void diff(HMC_type* q, HMC_type* x, HMC_type* w, HMC_type* t, HMC_type* d, int H, int I, int N) {

  int th = threadIdx.x + blockIdx.x*blockDim.x;  
  if(th < N){
  HMC_type f = q[0];
  for(int j=0;j<H;j++){
    HMC_type inSum = 0.0;
    for(int i=0;i<I;i++){
      inSum += q[2*H+1+I*j+i]*x[th*I+i];
    }
    f+=q[j+1]*tanh(q[H+1+j]+inSum);
  }
  d[th] = w[th]*(t[th]-f)*(t[th]-f);
  }
};
__global__ void diff2(HMC_type* q, HMC_type* x, HMC_type* w, HMC_type* t, HMC_type* d, int H, int I, HMC_type* block_sum, int N) {


  int tid = threadIdx.x;
  int th = threadIdx.x + blockIdx.x*blockDim.x;  
  if(th < N ){
  extern __shared__ HMC_type sdata[];
  HMC_type f = q[0];
  for(int j=0;j<H;j++){
    HMC_type inSum = 0.0;
    for(int i=0;i<I;i++){
      inSum += q[2*H+1+I*j+i]*x[th*I+i];
    }
    f+=q[j+1]*tanh(q[H+1+j]+inSum);
  }
  d[th] = w[th]*(t[th]-f)*(t[th]-f);
  /* parallel reduction */
  sdata[tid] = d[th];
  __syncthreads();

  //do reduction in shared memory.
  for(unsigned int s=1;s<blockDim.x;s*=2){
    //if(tid < s){
    //sdata[tid] += sdata[tid+s];
    //}
    int index = 2*s*tid;
    if(index < blockDim.x){
      sdata[index] += sdata[index+s];
    }
    //if(tid % (2*s) == 0){
    //sdata[tid] += sdata[tid+s];
    //}
    __syncthreads();
  }
  if(tid ==0) block_sum[blockIdx.x]=sdata[0];
  }
};
 HMC_type diff3(std::vector<HMC_type> &q, std::vector<HMC_type> &x, std::vector<HMC_type> &w, std::vector<HMC_type> &t, int H, int I, int N) {

  HMC_type d = 0.0;
  for(int th=0;th<N;th++){
    HMC_type f = q[0];
    //  std::cout << "here" << std::endl;
    for(int j=0;j<H;j++){
      HMC_type inSum = 0.0;
      for(int i=0;i<I;i++){
	inSum += q[2*H+1+I*j+i]*x[th*I+i];//****CHANGED****//
      }
      f+=q[j+1]*tanh(q[H+1+j]+inSum);//********//
    }
    d += w[th]*(t[th]-f)*(t[th]-f);
    if(th%256 == 0){
      std::cout << "!!!!!!!!" << std::endl;
      std::cout << d << std::endl;
    }
  }
  return d;
}

inline void cudaCheckError(const char * fn) 
{
    const cudaError_t err = cudaGetLastError();

    if (err != cudaSuccess)
    {
        std::cerr << fn << ": " << cudaGetErrorString(err) << "!\n";
        std::exit(EXIT_FAILURE);
    }
}


BNN_regression::BNN_regression(int l, int nOut_, int nRep_, int nBurn_, int h, int inp, std::vector<HMC_type> &data, std::vector<HMC_type> &weights, std::vector<HMC_type> &targets, std::string s) 
  : HMC_base(l, 1+h*(2+inp), nOut_, nRep_, nBurn_),
    v_x(data),
    H(h),
    I(inp),
    N(targets.size()),
    sig(1),
    v_w(weights),
    v_t(targets),
    oFile(s),
    sigb(100),
    sigv(1.65),
    siga(0.86),
    sigu(0.54)
{
  std::cout << "N = " << N << std::endl;
  np = getNP();
  std::cout << "BNN_regression(L,nOut,nRep,nBurn,H,I,x,w,t,s)" << std::endl;
  std::cout << "v_x[0] = " << v_x[0] << "\t v_x[1] = " << v_x[1] << std::endl;
  std::cout << "v_t[0] = " << v_t[0] << std::endl;
  of.open(oFile.c_str(),std::ofstream::out);
  of << I << "\t" << H << std::endl;

  /** memory allocation on GPU **/
  /* need to allocate d,t,x,w,q  */
  size_np = np*sizeof(HMC_type);
  size_n = N*sizeof(HMC_type);  

  //cudaSetDevice(0);
  //cudaDeviceSynchronize();
  //cudaThreadSynchronize();
  size_t freeMem, totalMem;

  cudaMemGetInfo(&freeMem, &totalMem);

  fprintf(stderr, "Free = %ld, Total = %ld\n", freeMem, totalMem); 

  x = &v_x[0];
  t = &v_t[0];
  w = &v_w[0];
  //q = &v_q[0];
  //d = &v_d[0];
  
  /** allocate data x **/
  dev_x = new HMC_type[N*I];
  cudaMalloc(&dev_x,size_n*I);
  cudaCheckError("cudaMalloc dev_x");
  /** allocate dev targets t **/
  dev_t = new HMC_type[N];
  cudaMalloc(&dev_t,size_n);
  cudaCheckError("cudaMalloc dev_t");
  /** allocate dev weights w **/  
  dev_w = new HMC_type[N];
  cudaMalloc(&dev_w,size_n);
  cudaCheckError("cudaMalloc dev_w");
  /** allocate NN parameters q **/
  dev_q = new HMC_type[np];  
  cudaMalloc(&dev_q,size_np);
  cudaCheckError("cudaMalloc dev_q");
  /** allocate diff array **/  
  dev_d = new HMC_type[N];
  cudaMalloc(&dev_d,size_n);
  cudaCheckError("cudaMalloc dev_t");
  //  thrust::device_ptr<HMC_type> d_dev_ptr(dev_d);

  std::cout << "GPU memory allocated\n";

  d_dev_ptr = thrust::device_ptr<HMC_type>(dev_d);
  /** copying memory from CPU to GPU **/
  cudaMemcpy(dev_x, x, size_n*I, cudaMemcpyHostToDevice);
  cudaCheckError("cudaMemcpy dev_x");
  cudaMemcpy(dev_t, t, size_n, cudaMemcpyHostToDevice);
  cudaCheckError("cudaMemcpy dev_t");
  cudaMemcpy(dev_w, w, size_n, cudaMemcpyHostToDevice);
  cudaCheckError("cudaMemcpy dev_w");
  std::cout << "GPU memory filled\n";
  
};

BNN_regression::BNN_regression(int l, int nOut_, int nRep_, int nBurn_, int h, int i, std::string s) 
  : HMC_base(l, 1+h*(2+i), nOut_, nRep_, nBurn_),
    v_x(std::vector<HMC_type>()),
    H(h),
    I(i),
    N(0),
    sig(1),
    v_w(std::vector<HMC_type>()),
    v_t(std::vector<HMC_type>()),
    oFile(s),
    sigb(100),
    sigv(1.65),
    siga(0.86),
    sigu(0.54)
{
  np = getNP();
  std::cout << "BNN_regression(l,h,i,s)" << std::endl;
  std::cout << "x[0] = " << x[0] << "\t x[1] = " << x[1] << std::endl;
  std::cout << "t[0] = " << t[0] << std::endl;
  of.open(oFile.c_str(),std::ofstream::out);

  of << I << "\t" << H << std::endl;

 /** memory allocation on GPU **/
  /* need to allocate d,t,x,w,q  */
  size_t size_np = np*sizeof(HMC_type);
  size_t size_n = N*sizeof(HMC_type);  

  /** allocate data x **/
  dev_x = new HMC_type[N*I];
  cudaMalloc(&dev_x,size_n*I);
  /** allocate dev targets t **/
  dev_t = new HMC_type[N];
  cudaMalloc(&dev_t,size_n);
  /** allocate dev weights w **/  
  dev_w = new HMC_type[N];
  cudaMalloc(&dev_w,size_n);
  /** allocate NN parameters q **/
  dev_q = new HMC_type[np];  
  cudaMalloc(&dev_q,size_np);
  /** allocate diff array **/  
  dev_d = new HMC_type[N];
  cudaMalloc(&dev_d,size_n);

  /** copying memory from CPU to GPU **/
  cudaMemcpy(dev_x, x, size_n*I, cudaMemcpyHostToDevice);
  cudaCheckError("cudaMemcpy dev_x");
  cudaMemcpy(dev_t, t, size_n, cudaMemcpyHostToDevice);
  cudaCheckError("cudaMemcpy dev_t");
  cudaMemcpy(dev_w, w, size_n, cudaMemcpyHostToDevice);
  cudaCheckError("cudaMemcpy dev_w");
};
void BNN_regression::add(std::vector<HMC_type> &inputs, HMC_type target, HMC_type weight){
  std::cout << "TO BE IMPLEMENTED" << std::endl;
};

BNN_regression::~BNN_regression() {
  std::cout << "destructor of BNN_regression()" << std::endl;
  cudaFree(dev_x);
  cudaFree(dev_t);
  cudaFree(dev_w);
  cudaFree(dev_q);
  cudaFree(dev_d);

  thrust::device_free(d_dev_ptr);
};

inline HMC_type BNN_regression::U(std::vector<HMC_type> &in_q) {
  // if((int)q.size() != np){
  //std::cout << "ERROR: incorrect parameter numbers" << std::endl;
  //assert(0);
  // }
  /*! probability density for BNN regression is -logP */
  // HMC_type sum = 0;
  // for(int j=0;j<np;j++){
  //std::cout << q[j] << "\t";
  //}
  //std::cout << std::endl;
  //std::vector<HMC_type> diff(N);
  //thrust::host_vector<HMC_type> diff(N);
  HMC_type* qq = &in_q[0];
  int threadsPerBlock = 256;
  int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;
  
  cudaMemcpy(dev_q, qq, size_np, cudaMemcpyHostToDevice);
  cudaCheckError("cudaMemcpy dev_q");
  //std::cout << "IN BNNREG" << std::endl;
  //thrust::device_ptr<HMC_type> d_dev_ptr(dev_d);
 
  diff<<<blocksPerGrid,threadsPerBlock>>>(dev_q, dev_x, dev_w, dev_t, dev_d, H, I, N); 
  //diff<<<threadsPerBlock,blocksPerGrid>>>(dev_q, dev_x, dev_w, dev_t, dev_d, H, I, N); 
  //HMC_type sum3 = diff3(in_q, v_x, v_w, v_t, H, I, N); 
  //diff[i] = w[i]*(t[i]-fq)*(t[i]-fq);
  //}
  HMC_type sum = thrust::reduce(d_dev_ptr,d_dev_ptr+N);
  //cudaDeviceSynchronize();
  //HMC_type* dev_sum;// = new HMC_type[blocksPerGrid];
  //cudaMalloc(&dev_sum,blocksPerGrid*sizeof(HMC_type));
  //cudaCheckError("cudaMalloc dev_sum");
  //HMC_type* par_sum = new HMC_type[blocksPerGrid];
  //diff2<<<blocksPerGrid,threadsPerBlock>>>(dev_q, dev_x, dev_w, dev_t, dev_d, H, I, dev_sum, N); 
  //diff2<<<threadsPerBlock,blocksPerGrid>>>(dev_q, dev_x, dev_w, dev_t, dev_d, H, I, dev_sum, N); 
  //cudaDeviceSynchronize();
  //cudaMemcpy(par_sum, dev_sum, sizeof(HMC_type)*blocksPerGrid, cudaMemcpyDeviceToHost);
  //cudaCheckError("cudaMemcpy sum");
  
  //std::cout << blocksPerGrid << std::endl;
  //HMC_type sum2 = 0.0;
  //for(int i=0;i<blocksPerGrid;i++){
  //std::cout << par_sum[i] << "\t";
  //sum2 += par_sum[i];
  //}
  //std::cout << "IN BNNREG" << std::endl;
  // thrust::device_vector<HMC_type> diff_d = diff;
  //HMC_type sum = thrust::reduce(diff_d.begin(), diff_d.end());
  //std::cout << "GPU thrust sum = " << sum << "\t" << "GPU sum = " << sum2 << std::endl;//"\tCPU sum = " << sum3 << std::endl;
  //char test;
  //std::cin >> test; 

  return sum/(2*sig*sig) + LnPrior(in_q);

};
/*! OPTIMIZE! CACHE!!!!! */
inline std::vector<HMC_type> BNN_regression::delU(std::vector<HMC_type> &q) {
  std::vector<HMC_type> FDdU(np);// = new HMC_type[np];
  std::vector<HMC_type> qm(np);
  std::vector<HMC_type> qp(np);
  
  
  //std::cout<< "in BNN_regression::delU" << std::endl;
   HMC_type h = 0.001;
   //std::vector<HMC_type> dU(np);
   for(int i=0; i<np;i++){
     qm = q;
     qp = q;
     qm[i] = qm[i] - 0.5*h;
     qp[i] = qp[i] + 0.5*h;
     //std::cout<< qm[i] << "\t";
     //std::cout<< qp[i] << "\t";
     FDdU[i] =  (U(qp) - U(qm))/h;
   }
   //std::cout<<std::endl;
  
   // FDdU = FDdelU(q);
  return FDdU;  //int np = getNP();

};



inline HMC_type BNN_regression::LnPrior(std::vector<HMC_type> &q) {


  HMC_type prior = 0.0;
  prior += 0.5*q[0]*q[0]/(sigb*sigb);
  for (int v=1; v<H+1;v++){
    // std::cout << "v = " << v << std::endl;
    prior +=  0.5*q[v]*q[v]/(sigv*sigv);
  }
  for(int a=H+1;a<2*H+1;a++){
    prior +=  0.5*q[a]*q[a]/(siga*siga);
    //std::cout << "a = " << a << std::endl;
  }
  for(int u=2*H+1; u<H*(2+I)+1; u++){
    prior +=  0.5*q[u]*q[u]/(sigu*sigu);
    //std::cout << "u = " << u << std::endl;
  }
  return prior;
};

