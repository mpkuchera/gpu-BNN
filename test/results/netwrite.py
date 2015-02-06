#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: netwrite.py
# Purpose: Write nn-function by reading output of net-display. net-display
#          is from Radford Neal's Bayesian Neural Network package.
# Created: 12-Feb-2005 Harrison B. Prosper, Daekwang Kau
# Updated: 14-Feb-2005 HBP Add averaging function
#          22-Feb-2005 HBP Add auto-scaling
#          22-Aug-2005 HBP Add function take vector of floats/doubles
#          03-Oct-2005 HBP Change handling of defaults to be compatible with
#                          loadfcn
#          10-Dec-2005 HBP Fix for CMS/Physics TDR work
#          01-Feb-2006 HBP Allow simplified var file
#          21-Dec-2007 HBP Add -H to write header file if desired
#          15-May-2010 HBP Change format of floats - use more precision
#          17-Sep-2010 HBP handle abs(..) variables
#          18-Oct-2010 HBP remove ";" from end of namespace
#$Id: netwrite.py,v 1.16 2011/05/07 18:39:15 prosper Exp $
#------------------------------------------------------------------------------
import os, sys
from getopt import getopt, GetoptError
from string import *
from time   import *
#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------
USAGE = '''
Usage:
  netwrite <options> <bnn-log-file-name>.txt

  options:
	   -h   print this
	   -r   <first:last>           Use networks first to last
	   -n   <n>                    Use last n networks
	   -H                          Write header file as well as C++ file

  Needs:
	   <bnn-log-file-name>.txt

	   and

	  // <bnn-log-file-name>.var with format

	   \tvariable-name\t[offset\tscale]
	   \t::\t::

  This will write the C++ function <bnn-log-file-name>.cpp

  NB: The first network in <nn-log-file-name>.bin has index 1. However,
  netwrite creates a C++ function that adopts the C++ convention of
  counting from 0.
'''
shortOptions = 'Hhr:n:'
#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def usage():
	print USAGE
	sys.exit(0)

def quit(s):
	print "\n**error** %s" % s
	sys.exit(1)

def printParameters(u,a,v,b):
	print "Output Bias"
	print "%11.4e" % b

	print "Hidden to Output Weights"
	c = 0
	for j in xrange(len(v)):
		c = c + 1
		if c < 5:
			print "%11.4e" % v[j],
		else:
			c = 0
			print "%11.4e" % v[j]
	print

	print "Hidden Biases"
	c = 0
	for j in xrange(len(a)):
		c = c + 1
		if c < 5:
			print "%11.4e" % a[j],
		else:
			c = 0
			print "%11.4e" % a[j]
	print

	print "Input to Hidden Weights"
	for i in xrange(len(u)):
		c = 0
		for j in xrange(len(u[0])):
			c = c + 1
			if c < 5:
				print "%11.4e" % u[i][j],
			else:
				c = 0
				print "%11.4e" % u[i][j]
		print


def funname(name, index):
	return '%s%3.3d' % (name, index)
#------------------------------------------------------------------------------
# Class to write network function recursively
#------------------------------------------------------------------------------
class NetWriter:

	def __init__(self, name, numnet, ninputs, nhidden, model, writeHeader):
		self.name = name
		self.nnet = numnet
		self.ninputs = ninputs
		self.nhidden = nhidden
		self.model = model
		self.writeHeader = writeHeader

		# Read data from var file, if it exists

		varfile = name + ".var"
		if os.path.exists(varfile):
			self.var = map(lambda x: split(x), open(varfile).readlines())
			self.var = filter(lambda x: len(x) > 0, self.var)

			if len(self.var[0]) != 3:
				self.var = map(lambda x: [x[0],0.0,1.0], self.var)
		else:
			print "\n**File %s not found..will create default names" % varfile
			self.var = []
			for i in xrange(ninputs):
				nm = "X%d" % i
				self.var.append([nm, 0.0, 1.0])

		nparams = nhidden * ( ninputs + 2 ) + 1

		self.filename = name + ".cpp"
		self.out = open(self.filename,'w')
		out = self.out

		out.write('//' + 77*'-' + '\n')
		out.write('// Network: ' + name + '\n')
		out.write('// Inputs:\n')
		out.write('//    %-40s%12s%12s\n' % ("","Offset", "Scale"))
		for namen, mean, sigma in self.var:
			out.write('//    %-40s%12.3e%12.3e\n' % (namen,
			atof(mean), atof(sigma)))
		out.write('//\n')
		out.write('// Created: ' + ctime(time()) + ' by netwrite.py\n')
		out.write('//' + 77*'-' + '\n')
		out.write('#include <cmath>\n')
		out.write('#include <vector>\n')
		out.write('#include <iostream>\n')
		out.write('#include <stdlib.h>\n')
		out.write('//' + 77*'-' + '\n')
		out.write('// Make following visible only to this programming unit\n')
		out.write('namespace {\n')
		out.write('  // NOTE: Network indices start at 0\n')
		out.write('  static const int nnetworks=%d;\n' % numnet)
		out.write('  static const int ninputs  =%d;\n' % ninputs)
		out.write('  static const int nhidden  =%d;\n' % nhidden)
		out.write('  static const int nparams  =%d;\n\n' % nparams)

		out.write('  static const double mean[ninputs]={\n')
		delim = ' '
		for namen, mean, sigma in self.var:
			out.write('%s%11.4e' % (delim,atof(mean)))
			delim = ',\n '
		out.write('\n  };\n\n')

		out.write('  static const double sigma[ninputs]={\n')
		delim = ' '
		for namen, mean, sigma in self.var:
			out.write('%s%11.4e' % (delim,atof(sigma)))
			delim = ',\n '
		out.write('\n  };\n\n')

		out.write('  static const double weight[nnetworks][nparams]={\n')

	def __del__(self):
		pass

	def write(self, u, a, v, b, lastnet):

		name = self.name
		out  = self.out

		# Get network structure

		ninputs = len(u)
		nhidden = len(u[0])
		nodes   = [ninputs,nhidden,1]

		# Put weights into a single list

		weight = []

		# Loop over hidden biases

		for j in xrange(len(a)):
			weight.append(a[j])

			# For current bias, loop over input weights

			for i in xrange(len(u)):
				weight.append(u[i][j])

		# Next add output bias

		weight.append(b)

		# Add output weights

		for j in xrange(len(v)):
			weight.append(v[j])

		# write out weights
		index = 0
		count = 0
		out.write('    {')
		for w in weight:
			index = index + 1
			count = count + 1
			if index == len(weight):
				delim = '\n'
			elif count > 5: 
				count = 0
				delim = ',\n     '
			else:
				delim = ','
			out.write('%11.4e%s' % (atof(w),delim))
		out.write('    }')
		if lastnet:
			out.write('\n  };\n\n')
		else:
			out.write(',\n')

	def close(self):
		name  = self.name
		nnet  = self.nnet
		ninputs=self.ninputs
		nhidden=self.nhidden
		npar  = nhidden * ( ninputs + 2 ) + 1
		out   = self.out
		nodes = [ninputs,nhidden,1]
		var   = self.var

		# Write network function

		out.write('\n')
		out.write('  double netfun(std::vector<double>& in, '\
				  'const double* w)\n')
		out.write('  {\n')
		inp = ninputs*[0]
		for i in xrange(ninputs):
			inp[i] = 'x0%d' % i
			out.write("    double " + inp[i] + " = in[%d];\n" % i)

		out.write('    double x;\n')

		print "model type: ", self.model
		if self.model == "real":
			outfunc = "x"
		else:
			outfunc = "1.0/(1.0+exp(-x))"

		nnwrite(1,0,nodes,inp,"",out, outfunc)

		out.write('    return x20;\n')
		out.write('  }\n} // End anonymous namespace\n\n')

		out.write('//' + 77*'-' + '\n')
		out.write('// Compute average over networks. '\
				  'Default is to use all networks\n')
		out.write('//' + 77*'-' + '\n')

		# Write out function with vector argument

		out.write('\n')
		str = 'double %s(std::vector<double>& inputs,\n' % name
		tab = (find(str, "(") + 1)*" "
		out.write(str)
		out.write('%sint first=0,\n' % tab)
		out.write('%sint last=nnetworks-1)\n' % tab)

		# Write body

		out.write('{\n')
		out.write('  if ( first < 0 ) first = 0;\n')
		out.write('  if ( last  < 0 ) last  = nnetworks-1;\n')
		out.write('  if ( last  > nnetworks-1 ) last = nnetworks-1;\n')
		out.write('  if ( first > last )\n')
		out.write('    {\n')
		out.write('      std::cerr << "** %s ** first-index > '\
				  'last-index"\n' % name)
		out.write('                << std::endl; exit(3);\n')
		out.write('    }\n')
		out.write('\n')
		out.write('  // Compute average over networks\n')
		out.write('  std::vector<double> in(ninputs);\n')
		for index, (namen, mean, sigma) in enumerate(var):
			out.write('  in[%d] = (inputs[%d] - mean[%d]) / sigma[%d];\n' % \
					  (index, index, index, index))
		out.write('\n')
		out.write('  int   n = last - first + 1;\n')
		out.write('  double x = 0.0;\n')
		out.write('  for(int i=first; i <= last; i++) '\
				  'x += netfun(in, weight[i]);\n')
		out.write('  return x / n;\n')
		out.write('}\n')

		if len(var) < 31:

			# Write calling sequence

			out.write('\n')		
			str = 'double %s(' % name
			space = (find(str,'(')+1)*' '
			tab = ''
			out.write(str)
			for namen, mean, sigma in var:
				if namen[0]=="|": namen = namen[1:-1]
				out.write('%sdouble %s,\n' % (tab, namen))
				tab = space 
			out.write('%sint first=0, int last=nnetworks-1)\n' % tab)
			out.write('{\n')
			out.write('  std::vector<double> in(ninputs);\n')
			for index, (namen, mean, sigma) in enumerate(var):
				if namen[0]=="|": namen = "abs(%s)" % namen[1:-1]
				out.write('  in[%d] = %s;\n' % \
						  (index, namen))
			out.write('  return %s(in, first, last);\n}\n' % name)
		else:
			print "\t** Warning: since the number of input variables > 30"\
				  "\n\t** you must use y = %s(inp), where inp is of type "\
				  "vector<double>" % name

##         # Write out function that can be loaded with dlopen

##         out.write('\n')
##         str = 'extern "C" double %s_dl(std::vector<double>& in,\n' % name
##         tab = (find(str, "(") + 1)*" "
##         out.write(str)
##         out.write('%sint first=0,\n' % tab)
##         out.write('%sint last=nnetworks-1)\n' % tab)
##         out.write('{\n')
##         str = '  return %s(' % name
##         tab = (find(str,'(')+1) * ' '
##         out.write(str)
##         delim = ''
##         for i in xrange(ninputs):
##             out.write(delim + 'in[%d]' % i)
##             delim = ',\n%s' % tab
##         out.write(', first, last);\n}\n')

##         out.write('\n')
##         str = 'extern "C" double %s_dl2(double* in,\n' % name
##         tab = (find(str, "(") + 1)*" "
##         out.write(str)
##         out.write('%sint first=0,\n' % tab)
##         out.write('%sint last=nnetworks-1)\n' % tab)
##         out.write('{\n')
##         str = '  return %s(' % name
##         tab = (find(str,'(')+1) * ' '
##         out.write(str)
##         delim = ''
##         for i in xrange(ninputs):
##             out.write(delim + 'in[%d]' % i)
##             delim = ',\n%s' % tab
##         out.write(', first, last);\n}\n')        

		out.close()

		# Write out header, if requested

		if not self.writeHeader: return

		self.filename = name + ".hpp"
		out = open(self.filename,'w')

		out.write('#ifndef %s_HPP\n' % upper(name))
		out.write('#define %s_HPP\n' % upper(name))
		out.write('//' + 77*'-' + '\n')
		out.write('// Network: ' + name + '\n')
		out.write('// Inputs:\n')
		out.write('//    %-40s%12s%12s\n' % ("","Offset", "Scale"))
		for namen, mean, sigma in self.var:
			out.write('//    %-40s%12.3e%12.3e\n' % (namen,
			atof(mean), atof(sigma)))
		out.write('//\n')
		out.write('// Created: ' + ctime(time()) + '\n')
		out.write('//' + 77*'-' + '\n')
		out.write('#include <vector>\n')
		out.write('\n')
		str = 'double %s(std::vector<double>& input,\n' % name
		tab = (find(str, "(") + 1)*" "
		out.write(str)
		out.write('%sint first=0,\n' % tab)
		out.write('%sint last=%d);\n\n' % (tab, nnet-1))
		out.write('#endif\n')
		out.close()
#-----------------------------------------------------------------------------
def nnwrite(layer,k,nodes,inp,s,out,outfunc):

	# Check if we are at the last layer
	last = layer >= len(nodes)-1

	prefix = "    "
	delim  = ";"
	vtype  = prefix + "double "
	endl   = "\n"

	inn = nodes[layer]*[0]
	for i in xrange(nodes[layer]):
		s = s + endl + prefix + "//Layer %d" % layer + ", Node %d" % i + endl
		s = s + prefix + "x = w[%d]" % k + delim + endl
		k = k + 1
		for j in xrange(len(inp)):
			s = s + prefix + "x = x + w[%d]" % k
			s = s + " * %s" % inp[j] + delim + endl
			k = k + 1
		xs = "x%d%d" % (layer,i)

		if not last:
			s = s + vtype + xs + " = tanh(x)" + delim + endl
		else:
			s = s + vtype + xs + " = %s" % outfunc + delim + endl
		inn[i] = xs
	if last:
		out.write(s)
		return
	else:
		nnwrite(layer+1,k,nodes,inn,s,out, outfunc)
#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
def main():

	#---------------------------------------------------
	# Decode command line using getopt module
	#---------------------------------------------------
	try:
		options, inputs = getopt(sys.argv[1:], shortOptions)
	except GetoptError, m:
		print
		print m
		usage()

	# Make sure we have a network log-file

	if len(inputs) == 0: usage()

	# Strip away extension

	netname  = os.path.splitext(inputs[0])[0] # Name of network
	nnlogfile= netname + ".txt"               # Name of (ASCII) log file
	#nnvarfile= netname + ".var"               # Name of variables file

	names = {'file':'', 'index':0}
	names['file'] = nnlogfile

	# Make sure bnn-logfile and bnn-varfile exist

	if not os.path.exists(nnlogfile): quit("File %s not found" % nnlogfile)
	#if not os.path.exists(nnlogfile): quit("File %s not found" % nnvarfile)

	# Get maximum network index 

	#input = os.popen("net-display -h %(file)s" % names)
	#record  = input.readline() # Skip blank line
	#record  = input.readline()
	#t = split(record)
	#maximumIndex = 0
	#try:
	#
	#	MAXIMUMINDEX = atoi(t[6])
	#except:
	#	quit("Unable to decode:\n%s" % record)

	try:
		with open( nnlogfile, 'r') as input:
			lines = input.readlines()
			maximumIndex = len(lines)-1
			print "maximumIndex = ", maximumIndex
		#maximumIndex = 
#		quit("maximumIndex = " % maximumIndex)
	except:
		quit("Unable to open:\n%s" % nnlogfile)

	# Decode options


	writeHeader = False

	firstIndex = 1
	lastIndex = maximumIndex

	for option, value in options:
		if option == "-h":
			quit(" if option == -h")
			usage()

		elif option == "-H":
			writeHeader = True

		elif option == "-r":
			t = split(value,':')

			if len(t) == 0:
				quit("You must specify a range as first:last")

			elif len(t) == 1:
				try:
					firstIndex = atoi(t[0])
				except:
					quit("You must specify range using integers!")
				lastIndex = maximumIndex

			elif len(t) == 2:
				try:
					firstIndex, lastIndex = map(lambda x: atoi(x), t)
				except:
					quit("You must specify range using integers!")

		elif option == '-n':
			n = 0
			try:
				n = atoi(value)
			except:
				quit("Specify an integer with option -n")

			lastIndex  = maximumIndex
			firstIndex = lastIndex - n + 1
			if firstIndex < 1: firstIndex = 1

	# Check indices

	if firstIndex <= 0:
		print " if firstIndex <=0"
		usage() 
	if firstIndex > maximumIndex: quit("first index must be <= %d" % \
									   maximumIndex)

	if lastIndex <= 0: 
		usage()
		quit(" if lastIndex <=0")
	if lastIndex > maximumIndex: quit("last index must be <= %d" % \
									   maximumIndex)

	if lastIndex < firstIndex:
		quit("first index <= last index")

	print "Made it through!"
	# Ok, let's get down to work!

	#---------------------------------------------------
	# Get network structure. Assume a single output only
	#---------------------------------------------------        
#	net = os.popen("net-spec %s" % nnlogfile).readlines()
#	for record in net:
#		t = split(record)
#		if len(t) == 0: continue
#
#		keyword = t[0]
#		if keyword == "Input":
#			ninputs = atoi(t[3])
#		elif keyword == "Hidden":
#			nhidden = atoi(t[4])
#			break

	t = split(lines[0])
	ninputs = atoi(t[0])
	nhidden = atoi(t[1])
	lines = lines[1:]

	numberNetworks = lastIndex - firstIndex + 1

	#---------------------------------------------------
	# Get network type (real or binary)
	#---------------------------------------------------        
	#net = os.popen("model-spec %s" % nnlogfile).read()
	#if find(net, "real") > -1:
	#	model = "real"
	#else:
	#	model = "binary"

	model = "real"
	netwriter = NetWriter(netname, numberNetworks, ninputs, nhidden,
						  model, writeHeader)

	numberParams   = nhidden * (ninputs + 2) + 1
	print 
	print "Use networks:           %d to %d" % (firstIndex, lastIndex)
	print "Number of inputs:       %d" % ninputs
	print "Number of hidden nodes: %d" % nhidden
	print "Number of parameters:   %d" % numberParams

	#---------------------------------------------------
	# Call net-display for each index
	#---------------------------------------------------

	netnumber = 0
	for index in xrange(firstIndex-1,lastIndex):
		#print index
		#names['index'] = index
	
		#---------------------------------------------------
		# Read as one long record
		#---------------------------------------------------
		#record = os.popen("net-display -p %(file)s %(index)d" % \
		#				   names).read()



		# Extract weights from records

		u = ninputs*[0] # input-hidden weights u[i][j],
		# j = 1, nhidden, i=1,ninputs

		a = nhidden*[0] # hidden biases
		v = nhidden*[0] # hidden-output weights

		#---------------------------------------------------
		# Split into tokens and fill various parameter lists
		#---------------------------------------------------
		tokens = split(lines[index])
		b = atof(tokens[0])
                # Fill hidden to output weights

		for j in xrange(nhidden):
			v[j] = atof(tokens[j+1])

		for j in xrange(nhidden):
			a[j] = atof(tokens[j+1+nhidden])

		for i in xrange(ninputs):
			u[i] = nhidden*[0]
			for j in xrange(nhidden):
				u[i][j] = atof(tokens[2*nhidden+1+ninputs*j+i])


		if index < 2: 
			printParameters(u,a,v,b)
			print "="*40
		#---------------------------------------------------
		# Build function
		#---------------------------------------------------        
		netnumber += 1

		netwriter.write(u,a,v,b, netnumber==numberNetworks)

	netwriter.close()
#------------------------------------------------------------------------------
main()


















