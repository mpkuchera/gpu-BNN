runHMCex : HMCex.o HMC.o
	g++ -o $@ $^
HMC.o : HMC.cc

HMCex.o : HMCex.cc

#---------------------

run: runHMCex
	./runHMC

clean:
	rm -f *.o
	rm -f runHMCex

build: clean runHMCex

%.o: %.cc
	g++ -c $<

#-----------------------
