# ------------------------------------------------------------------------------
# Updated: 06-Feb-2015 HBP - tweak
# ------------------------------------------------------------------------------
# Remove @ symbol to have a verbose printout
AT 	:= @

# define sub-directories
inc_dir	:= include
src_dir	:= src
app_dir	:= test
lib_dir	:= lib
bin_dir := bin
uname	:= $(shell uname)

slib_name := HMCMC
sharedlib := $(PWD)/$(lib_dir)/lib$(slib_name).so

# get architecture and word size
OS_ARCH    = $(shell uname -m)
OS_SIZE    = $(shell uname -m | sed -e "s/x86_64/64/")

# ------------------------------------------------------------------------------
# PTX is a low-level parallel-thread execution virtual machine and
# instruction set architecture (ISA). PTX exposes the GPU as a parallel
# computing device.

# SASS is the low-level assembly language that compiles to binary
# microcode, which executes natively on NVIDIA GPU hardware.
# ------------------------------------------------------------------------------
# set streaming multiprocessors (SMS) if not yet set
ifeq ($(OS_ARCH),armv7l)
SMS ?= 20 30 32 35 37 50
else
SMS ?= 11 20 30 35 37 50
endif

ifeq ($(GENCODE_FLAGS),)
# Generate SASS code for each SM architecture listed in $(SMS)
$(foreach sm,$(SMS),$(eval GENCODE_FLAGS += -gencode arch=compute_$(sm),code=sm_$(sm)))

# Generate PTX code from the highest SM architecture in $(SMS)
# to guarantee forward-compatibility
HIGHEST_SM := $(lastword $(sort $(SMS)))
ifneq ($(HIGHEST_SM),)
GENCODE_FLAGS += -gencode arch=compute_$(HIGHEST_SM),code=compute_$(HIGHEST_SM)
endif
endif

# compilers
CC	:= clang++ -stdlib=libstdc++
CU	:= nvcc -ccbin clang++ -Xcompiler

# flags
CPPFLAGS:= -Iinclude
CXXFLAGS:= -O2  $(DFLAG) -m$(OS_SIZE)
LDFLAGS	:= -m$(OS_SIZE)
LDSHARED:= nvcc -shared

# other libraries
LIBS	:= -lm

INC_LIB	:= $(wildcard $(inc_dir)/*.h)
HMC_SRC	:= $(wildcard $(src_dir)/*.cc)
APP_SRC	:= $(wildcard $(app_dir)/*.cc)
CUDA_SRC:= $(wildcard $(src_dir)/*.cu) 

lib_objs:= $(subst $(src_dir)/,$(lib_dir)/,$(HMC_SRC:.cc=.o))
app_objs:= $(subst $(app_dir)/,$(lib_dir)/,$(APP_SRC:.cc=.o))
cuda_objs	:= $(subst $(src_dir)/,$(lib_dir)/,$(CUDA_SRC:.cu=.o))

#say	:= $(shell echo "OS_ARCH:  $(OS_ARCH)"  >& 2)
#say	:= $(shell echo "LDFLAGS:  $(LDFLAGS)"  >& 2)
#say	:= $(shell echo "LDSHARED: $(LDSHARED)" >& 2)
#say	:= $(shell echo "CC:       $(CC)" >& 2)
#say	:= $(shell echo "CU:       $(CU)" >& 2)
#say	:= $(shell echo -e "INC_LIB: $(INC_LIB)" >& 2)
#say	:= $(shell echo -e "HMC_SRC: $(HMC_SRC)" >& 2)
#say	:= $(shell echo -e "APP_SRC: $(APP_SRC)" >& 2)
#say	:= $(shell echo "app_objs: $(app_objs)" >& 2)
#say	:= $(shell echo "lib_objs: $(lib_objs)" >& 2)
#say 	:= $(shell echo "cuda_objs: $(cuda_objs)" >& 2)

# Construct list of applications
applications	:= $(subst $(app_dir)/,$(bin_dir)/,$(APP_SRC:.cc=))
say	:= $(shell echo "")
say	:= $(shell echo "applications: $(applications)" >& 2)
say	:= $(shell echo "")
#$(error bye)

all:	lib bin

bin:	$(applications)

lib:	$(sharedlib)

$(applications)	: $(bin_dir)/%	:  $(lib_dir)/%.o $(sharedlib)
	@echo "----> Linking $@  and $<"
	$(AT)$(CC)  -L$(lib_dir) -l$(slib_name) $< -o $@

$(sharedlib) : $(lib_objs) $(cuda_objs) $(usr_objs)
	@echo "----> Linking $@"
	$(AT)$(LDSHARED) $(LDFLAGS) $(GENCODE_FLAGS) \
$(LIBS) $(cuda_objs) $(lib_objs) $(usr_objs) -o $@

$(app_objs)	: $(lib_dir)/%.o : $(app_dir)/%.cc $(INC_LIB) $(lib_objs)
	@echo "----> Compiling app_objs $@"
	$(AT)$(CU)  $(CPPFLAGS) -c -o $@ $<

$(cuda_objs)	: $(lib_dir)/%.o : $(src_dir)/%.cu $(INC_LIB)
	@echo "----> Compiling cuda_objs $@"
	$(AT)$(CU) $(CPPFLAGS) $(GENCODE_FLAGS) -c -o $@ $<

$(lib_objs)	: $(lib_dir)/%.o : $(src_dir)/%.cc $(INC_LIB)
	@echo "----> Compiling lib_objs $@"
	$(AT)$(CC) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

clean	:
	rm -rf $(lib_dir)/*.*o
	rm -rf $(bin_dir)/*

