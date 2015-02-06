#-----------------------------------------------------------------------------
# Some ROOT histogram utilities
# Created: sometime in the early 21st century, HBP
#-----------------------------------------------------------------------------
import os, sys, re
from glob import glob
from array import array
from ROOT import *
from string import *
from math import *
#-----------------------------------------------------------------------------
RED    ="\x1b[0;31;48m"
GREEN  ="\x1b[0;32;48m"
YELLOW ="\x1b[0;33;48m"
BLUE   ="\x1b[0;34;48m"
MAGENTA="\x1b[0;35;48m"
CYAN   ="\x1b[0;36;48m"

BOLDRED    ="\x1b[1;31;48m"
BOLDGREEN  ="\x1b[1;32;48m"
BOLDYELLOW ="\x1b[1;33;48m"
BOLDBLUE   ="\x1b[1;34;48m"
BOLDMAGENTA="\x1b[1;35;48m"
BOLDCYAN   ="\x1b[1;36;48m"

RESETCOLOR ="\x1b[0m"    # reset to default foreground color             
#------------------------------------------------------------------------------
WIDTH  = 500    # Default canvas width
HEIGHT = 500    # Default canvas height
NDIVX  = 510

TEXTFONT = 42
# Font code = 10 * fontnumber + precision with fontnumber 1..14
# fontnumber= 1..14
# precision = 0 fast hardware fonts
# precision = 1 scalable and rotatable hardware fonts

# precision = 2 scalable and rotatable hardware fonts
# precision = 3 scalable and rotatable hardware fonts. Text size in pixels. 

Arial             = 43
FONTSIZE          = 18 # font size in pixels

TimesNewRomanBold = 33
LABEL_FONTSIZE    = 18
FONTSCALE         = 0.0027

TimesNewRoman2    = 12
TITLE_FONTSIZE    = 0.04

# Text alignment = 10 * horizontal + vertical
# For horizontal alignment:
#   1=left adjusted, 2=centered, 3=right adjusted
# For vertical alignment:
#   1=bottom adjusted, 2=centered, 3=top adjusted
ALIGN_LEFT_BOTTOM = 11
#------------------------------------------------------------------------------
CMSstyle = TStyle("CMSstyle","CMS Style")
def setStyle():
	CMSstyle.SetPalette(1)
	# For the canvas:
	CMSstyle.SetCanvasBorderMode(0)
	CMSstyle.SetCanvasColor(kWhite)
	CMSstyle.SetCanvasDefH(500) #Height of canvas
	CMSstyle.SetCanvasDefW(500) #Width of canvas
	CMSstyle.SetCanvasDefX(0)   #Position on screen
	CMSstyle.SetCanvasDefY(0)

	# For the Pad:
	CMSstyle.SetPadBorderMode(0)
	CMSstyle.SetPadColor(kWhite)
	CMSstyle.SetPadGridX(kFALSE)
	CMSstyle.SetPadGridY(kFALSE)
	CMSstyle.SetGridColor(kGreen)
	CMSstyle.SetGridStyle(3)
	CMSstyle.SetGridWidth(1)
	
	# For the frame:
	CMSstyle.SetFrameBorderMode(0)
	CMSstyle.SetFrameBorderSize(1)
	CMSstyle.SetFrameFillColor(0)
	CMSstyle.SetFrameFillStyle(0)
	CMSstyle.SetFrameLineColor(1)
	CMSstyle.SetFrameLineStyle(1)
	CMSstyle.SetFrameLineWidth(1)
	
	# For the histo:
	CMSstyle.SetHistLineColor(1)
	CMSstyle.SetHistLineStyle(0)
	CMSstyle.SetHistLineWidth(2)
	
	CMSstyle.SetEndErrorSize(2)
	CMSstyle.SetErrorX(0.)
	
	CMSstyle.SetMarkerSize(0.5)
	CMSstyle.SetMarkerStyle(20)

	# For the fit/function:
	CMSstyle.SetOptFit(1)
	CMSstyle.SetFitFormat("5.4g")
	CMSstyle.SetFuncColor(2)
	CMSstyle.SetFuncStyle(1)
	CMSstyle.SetFuncWidth(1)
	
	# For the date:
	CMSstyle.SetOptDate(0)

	# For the statistics box:
	CMSstyle.SetOptFile(0)
	CMSstyle.SetOptStat("")
	# To display the mean and RMS:
	# CMSstyle.SetOptStat("mr") 
	CMSstyle.SetStatColor(kWhite)
	CMSstyle.SetStatFont(TEXTFONT)
	CMSstyle.SetStatFontSize(0.03)
	CMSstyle.SetStatTextColor(1)
	CMSstyle.SetStatFormat("6.4g")
	CMSstyle.SetStatBorderSize(1)
	CMSstyle.SetStatH(0.2)
	CMSstyle.SetStatW(0.3)
    
	# Margins:
	CMSstyle.SetPadTopMargin(0.05)
	CMSstyle.SetPadBottomMargin(0.16)
	CMSstyle.SetPadLeftMargin(0.20)
	CMSstyle.SetPadRightMargin(0.10)
	
	# For the Global title:
	CMSstyle.SetOptTitle(0) 
	CMSstyle.SetTitleFont(TEXTFONT)
	CMSstyle.SetTitleColor(1)
	CMSstyle.SetTitleTextColor(1)
	CMSstyle.SetTitleFillColor(10)
	CMSstyle.SetTitleFontSize(0.05)

	# For the axis titles:
	CMSstyle.SetTitleColor(1, "XYZ")
	CMSstyle.SetTitleFont(TEXTFONT, "XYZ")
	CMSstyle.SetTitleSize(0.05, "XYZ")
	CMSstyle.SetTitleXOffset(1.20)    #(1.25)
	CMSstyle.SetTitleYOffset(1.37)    #(1.60)
					
	# For the axis labels:
	CMSstyle.SetLabelColor(1, "XYZ")
	CMSstyle.SetLabelFont(TEXTFONT, "XYZ")
	CMSstyle.SetLabelOffset(0.007, "XYZ")
	CMSstyle.SetLabelSize(0.05, "XYZ")
  
	# For the axis:
	CMSstyle.SetAxisColor(1, "XYZ")
	CMSstyle.SetStripDecimals(kTRUE)
	CMSstyle.SetTickLength(0.03, "XYZ")
	CMSstyle.SetNdivisions(NDIVX, "XYZ")
	# To get tick marks on the opposite side of the frame
	CMSstyle.SetPadTickX(1)  
	CMSstyle.SetPadTickY(1)

	# Change for log plots:
	CMSstyle.SetOptLogx(0)
	CMSstyle.SetOptLogy(0)
	CMSstyle.SetOptLogz(0)

	# Postscript options:
	CMSstyle.SetPaperSize(20.,20.)
	CMSstyle.cd()
#------------------------------------------------------------------------------
class Scribe:
	def __init__(self, xxpos, yypos, size=TITLE_FONTSIZE, font=TEXTFONT):
		self.xpos = xxpos
		self.ypos = yypos
		self.linewidth = 1.5*size
		self.t = TLatex()
		self.t.SetNDC()
		self.t.SetTextSize(size)
		self.t.SetTextFont(font)
		self.t.SetTextAlign(12)

	def __del__(self):
		if self.t != 0: del self.t

	def write(self, text, xoffset=0):
		y = self.ypos
		if y < 0: return
		self.t.DrawLatex(self.xpos+xoffset, y, text)
		self.ypos -= self.linewidth

	def vspace(self, f=0.5):
		y = self.ypos
		if y < 0: return
		self.t.DrawLatex(self.xpos, y, " ")
		self.ypos -= self.linewidth * f;
#------------------------------------------------------------------------------
def addTitle(title="CMS       L = 5 fb^{-1}    #sqrt{s} = 7 TeV"):
	xtext = 0.200
	ytext = 0.975
	s = Scribe(xtext, ytext)
	s.write(title)
	return s
#------------------------------------------------------------------------------
PERCENT = [0.0230,
	   0.1579,
	   0.5000,
	   0.8415,
	   0.9770]

def percentiles(points, percent):
	pts = map(lambda x: x, points)
	pts.sort()
	np = len(pts)
	ps = []
	for p in percent:
		x = p * np
		k = int(x)
		f = x - k
		c1= pts[k]
		if k < np-1:
			c2 = pts[k+1]
			c  = c1*(1-f) + c2*f
		else:
			c = c1
		ps.append(c)
	return ps

class PercentileCurve:

	def __init__(self, size):
		self.size = size
		self.points = map(lambda x: [], size*[0])

	def __del__(self):
		pass

	def add(self, curve):
		# check if this is a histogram
		try:
			nbins = curve.GetNbinsX()
			if nbins != self.size:
				print "*** PercentileCurve - ERROR*** wrong number of bins (points on curve)"
				print "nbins: %d, size: %d" % (nbins, self.size)
				return False
			
			for ii in xrange(nbins):
				c = curve.GetBinContent(ii+1)
				self.points[ii].append(c)
		except:
			if len(curve) != self.size:
				print "*** PercentileCurve - ERROR*** wrong number of points on curve"
				print "len(curve): %d, size: %d" % (len(curve), self.size)
				return False
		
			for ii, y in enumerate(curve):
				self.points[ii].append(y)
		return True
	
	def __call__(self, percentile):
		z = []
		for ii in xrange(self.size):
			points = self.points[ii]
			points.sort()
			np = len(points)
			
			x = percentile * np
			k = int(x)
			f = x - k
			c1= points[k]
			if k < np-1:
				c2 = points[k+1]
				c  = c1*(1-f) + c2*f
			else:
				c = c1				
			z.append(c)
		return z

class StandardCurve:

	def __init__(self, size):
		self.size = size
		self.points = map(lambda x: [], size*[0])

	def __del__(self):
		pass

	def add(self, curve):
		if len(curve) != self.size:
			print "*** StandardCurve - ERROR** wrong number of points on curve"
			print "len(curve): %d, size: %d" % (len(curve), self.size)
			return False
		
		for ii, y in enumerate(curve):
			self.points[ii].append(y)
		return True
	
	def __call__(self, nsigma):
		z = []
		for ii in xrange(self.size):
			points = self.points[ii]
			c = sum(points)/len(points)
			ec= sqrt(sum(map(lambda x: (x-c)**2, points))/len(points))
			if nsigma != 0: c = c + nsigma * ec
			z.append(c)
		return z
#------------------------------------------------------------------------------
def getarg(args, key, d):
	if args.has_key(key):
		return args[key]
	else:
		return d
#------------------------------------------------------------------------------
def mkpline(xx, y1, y2, boundary, **args):
	
	color  = getarg(args, 'color',   kYellow)
	fstyle = getarg(args, 'fstyle',  3001)
	lwidth = getarg(args, 'lwidth',  2)
	
	nbins = len(xx)

	# lower curve
	x = array('d')
	if type(xx) == type([]):		
		x.fromlist(xx)
	else:
		for z in xx: x.append(z)

	y = array('d')
	if type(y1) == type([]):
		y.fromlist(y1)
	else:
		for z in y1: y.append(z)

	# upper curve
	
	for i in xrange(nbins):
		j = nbins - i - 1
		x.append(xx[j])
		y.append(y2[j])

	x.append(xx[0])
	y.append(y1[0])

	# clip polygon
	np = 2*nbins
	npp = 2*np
	xc = array('d')
	xc.fromlist(npp*[0])
	yc = array('d')
	yc.fromlist(npp*[0])

	xmin, xmax, ymin, ymax = boundary
	np = gPad.ClipPolygon(np, x, y, npp, xc, yc, xmin, ymin, xmax, ymax)
	
	pl = TPolyLine(np, xc, yc)
	pl.SetLineColor(color)
	pl.SetLineWidth(lwidth)
	pl.SetFillColor(color)
	pl.SetFillStyle(fstyle)

	return pl
#------------------------------------------------------------------------------
def mkhist1(hname, xtitle, ytitle, nbins, xmin, xmax, **args):
	ymin   = getarg(args, 'ymin', None)
	ymax   = getarg(args, 'ymax', None)
	color  = getarg(args, 'color',   kBlack)
	lstyle = getarg(args, 'lstyle',  1)
	lwidth = getarg(args, 'lwidth',  1)
	ndivx  = getarg(args, 'ndivx',   505)
	ndivy  = getarg(args, 'ndivy',   510)

	h = TH1F(hname, "", nbins, xmin, xmax)		
	h.SetLineColor(color)
	h.SetLineStyle(lstyle)
	h.SetLineWidth(lwidth)
	
	h.SetMarkerSize(0.8)
	h.SetMarkerColor(color)
	h.SetMarkerStyle(20)
	
	h.GetXaxis().SetTitle(xtitle)
	h.GetXaxis().SetTitleOffset(1.2);
	h.GetXaxis().SetLimits(xmin, xmax)
	h.SetNdivisions(ndivx, "X")
	
	h.GetYaxis().SetTitle(ytitle)
	h.GetYaxis().SetTitleOffset(1.6)
	if ymin != None: h.SetMinimum(ymin)
	if ymax != None: h.SetMaximum(ymax)
	h.SetNdivisions(ndivy, "Y")
	return h
#------------------------------------------------------------------------------
def mkhist2(hname, xtitle, ytitle,
	    nbinx, xmin, xmax,	
	    nbiny, ymin, ymax, **args):
	color  = getarg(args, 'color',   kBlack)
	mstyle = getarg(args, 'mstyle',  20)
	msize  = getarg(args, 'msize',   0.5)
	ndivx  = getarg(args, 'ndivx',   505)
	ndivy  = getarg(args, 'ndivy',   505)
	
	h = TH2F(hname, "", nbinx, xmin, xmax, nbiny, ymin, ymax)
	h.SetLineColor(color)
	h.SetMarkerColor(color)
	h.SetMarkerSize(msize)
	h.SetMarkerStyle(mstyle)
	
        #h.GetXaxis().CenterTitle()
	h.GetXaxis().SetTitle(xtitle)
	h.GetXaxis().SetTitleOffset(1.3)
	h.SetNdivisions(ndivx, "X")
	
        #h.GetYaxis().CenterTitle()
	h.GetYaxis().SetTitle(ytitle)
	h.GetYaxis().SetTitleOffset(0.9)
	h.SetNdivisions(ndivy, "Y")
	return h
def fixhist2(h, xtitle, ytitle, **args):
	color  = getarg(args, 'color',   kBlack)
	mstyle = getarg(args, 'mstyle',  20)
	msize  = getarg(args, 'msize',   0.5)
	ndivx  = getarg(args, 'ndivx',   505)
	ndivy  = getarg(args, 'ndivy',   505)

	h.SetLineColor(color)
	h.SetMarkerColor(color)
	h.SetMarkerSize(msize)
	h.SetMarkerStyle(mstyle)

	h.GetXaxis().SetTitle(xtitle)
	h.GetXaxis().SetTitleOffset(1.3)
	h.SetNdivisions(ndivx, "X")

	h.GetYaxis().SetTitle(ytitle)
	h.GetYaxis().SetTitleOffset(0.9)
	h.SetNdivisions(ndivy, "Y")
#------------------------------------------------------------------------------
def mkgraph(x, y, xtitle, ytitle, xmin, xmax, **args):
	ymin   = getarg(args, 'ymin', None)
	ymax   = getarg(args, 'ymax', None)
	color  = getarg(args, 'color',   kBlack)
	lstyle = getarg(args, 'lstyle',  1)
	lwidth = getarg(args, 'lwidth',  1)
	ndivx  = getarg(args, 'ndivx',   505)
	ndivy  = getarg(args, 'ndivy',   510)

	n = len(y)

	xx = x
	yy = y
	if type(y) == type([]): yy = array('d')

	for i in range(n): yy.append(y[i])
		
	g = TGraph(n, xx, yy)
		
	g.SetLineColor(color)
	g.SetLineStyle(lstyle)
	g.SetLineWidth(lwidth)
	
	g.SetMarkerSize(0.8)
	g.SetMarkerColor(color)
	g.SetMarkerStyle(20);
	
	g.GetXaxis().SetTitle(xtitle)
	g.GetXaxis().SetTitleOffset(1.2);
	g.GetXaxis().SetLimits(xmin, xmax)
	g.GetHistogram().SetNdivisions(ndivx, "X")
	
	g.GetYaxis().SetTitle(ytitle)
	g.GetYaxis().SetTitleOffset(1.6)
	if ymin != None and ymax != None:
		g.GetHistogram().SetAxisRange(ymin, ymax, "Y")
	g.GetHistogram().SetNdivisions(ndivy, "Y")
	return g
#------------------------------------------------------------------------------
def mklegend(xx, yy, xw, yw):
	lg = TLegend(xx, yy, xx+xw, yy+yw)
	lg.SetFillColor(kWhite)
	lg.SetTextFont(TEXTFONT)
	lg.SetBorderSize(0)
	lg.SetShadowColor(kWhite)
	return lg
#------------------------------------------------------------------------------
class Row:
	def __init__(self, rownumber, varmap, data):
		self.row = rownumber
		self.varmap = varmap
		self.data = data
		self.items = map(lambda x: (x[1],x[0]), self.varmap.items())
		self.items.sort()
		
		# Initialize row counter
		self.col = 0
		self.maxcol = len(self.items)-1
		
	def __del__(self):
		pass

	def __call__(self, variable):
		if not self.varmap.has_key(variable): return None
		index = self.varmap[variable]
		return self.data[index]

	def __str__(self):
		strrep = "Row: %d\n" % self.row
		for index, name in self.items:
			value = self.data[index]
			if type(value) != type(""):
				strvalue = "%12.3f" % value
			else:
				strvalue = "%12s" % value
			strrep += "%4d\t%-32s\t%s\n" % (index, name, strvalue)
		return strip(strrep)

	# Implement Python iterator protocol
	
	def __iter__(self):
		return self

	def next(self):
		if self.col > self.maxcol:
			self.col = 0
			raise StopIteration
		else:
			index, name = self.items[self.col]
			value = self.data[index]
			self.col += 1
			return (name, value)
#------------------------------------------------------------------------------
def tonumber(x):
	try:
		y = atof(x)
	except:
		y = x
	return y

class Table:
	
	def __init__(self, filename, nrows=-1):
		try:
			file = open(filename, 'r')
		except:
			print "*** can't read file %s" % filename
			sys.exit(0)

		# Read header
		header = split(file.readline())
		#print header
		
		row = 0
		self.data = []
		while 1:
			try:
				record = file.readline()
			except:
				break

			# Convert to numbers
			record = map(tonumber, split(record))
			
			#print record
			self.data.append(record)
			row += 1
			if nrows > 0:
				if row >= nrows:
					break
		file.close()

		# Initialize row counter
		self.row = 0
		self.maxrow = len(self.data)-1
		
		# Create a name to index map
		self.varmap = {} # empty map
		for index, name in enumerate(header):
			self.varmap[name] = index

	def __del__(self):
		pass

	def __call__(self, row, variable=None):
		if row < 0: return None
		if row > self.maxrow: return None
		if variable == None:
			return Row(row, self.varmap, self.data[row])
		else:
			if not self.varmap.has_key(variable): return None
			index = self.varmap[variable]
			return self.data[row][index]

	# Implement Python iterator protocol
	
	def __iter__(self):
		return self

	def next(self):
		if self.row > self.maxrow:
			self.row = 0
			raise StopIteration
		else:
			data = Row(self.row, self.varmap, self.data[self.row])
			self.row += 1
			return data
#------------------------------------------------------------------------------
class Buffer:

	def __init__(self, buffer, buffermap, variable):
		self.buffer = buffer
		self.buffermap = buffermap
		self.variable = variable

	def __getattr__(self, variable):
		if self.buffermap.has_key(variable):
			jj = self.buffermap[variable]
			return self.buffer[jj].__getattribute__(variable)
		else:
			raise AttributeError(variable)
		
	def __str__(self):
		s = 'Event variables:\n'
		for tname, name, maxcount in self.variable:
			s += "  %-12s %-24s:\t" % (tname, name)
			s += "%s\n" % self.__getattr__(name)
		return s
	
class Ntuple:
	# "self" is Python's equivalent of the "this" pointer in C++
	# self points to the memory allocated for the object
	
	def __init__(self, filename, treename, nrows=None):

		# cache inputs
		
		self.filename = filename # Root file name
		self.treename = treename
		self.nrows = nrows
		
		# check that root file exists
		if not os.path.exists(filename):
			print "** Ntuple *** "\
			      "root file %s not found" % filename
			sys.exit(0)

		# ------------------------------------
		# open root file
		# ------------------------------------
		print "reading root file\t--> %s" % filename
		
		self.file = TFile(self.filename)
		self.tree = self.file.Get(self.treename)
		tree = self.tree
		
		if tree == None:
			print "** Tree is non-cooperative - perhaps the name is wrong?"
			sys.exit(0)

		# get names of variables from root file
		branches  = tree.GetListOfBranches()
		# get number of variables 
		nbranches = branches.GetEntries()

		# print variables
		self.vars = []
		#print "variables:"
		for i in xrange(nbranches):
			# get the ith branch (aka variable)
			bname = branches[i].GetName()			
			
			# assume that the leaf attached to this branch
			# has the same name as the branch
			leafname = bname
			leaf  = branches[i].GetLeaf(leafname)
			if leaf == None:
				# Get all leaves associated with this branch
				leaves = branches[i].GetListOfLeaves()
				if leaves == None:
					print "No leaves found!"
					sys.exit(0)

				# Assume one leaf/branch
				leaf = leaves[0]
				if leaf == None:
					print "No leaf found"
					sys.exit(0)
					
				leafname = leaf.GetName()
				
			# get leaf type (int, float, double, etc.)
			tname = leaf.GetTypeName()

			#check for leaf counter
			flag = Long(0)
			leafcounter = leaf.GetLeafCounter(flag)
			if leafcounter:
				maxcount = leafcounter.GetMaximum()
			else:
				maxcount = leaf.GetLen()
				
			# store type and variable name
			self.vars.append( (tname, bname, maxcount) )
			#print "\t%4d\t%-12s\t%-32s\t%d" % (i, tname, bname, maxcount)
		nlen = len(self.vars)

		# create a map of variable name to column number
		self.varmap = {}
		for ind, var in enumerate(self.vars):
			self.varmap[var] = ind

		# initialize row number
		self.row = 0
		nentries = self.tree.GetEntries()
		if self.nrows != None:
			self.entries = min(self.nrows, nentries) 
		else:			
			self.entries = nentries
		# ------------------------------------
		# set up branches as a struct
		# Root has a limit on how long a
		# string it can cope with, so split
		# into multiple strings
		# ------------------------------------

		bufferCount = 0
		newBuffer = True
		rec = ""
		bufferName = ""
		maxlength  = 2000
		self.buffermap  = {}
		self.buffer = []
		
		for count, (tname, name, maxcount) in enumerate(self.vars):

			# keep track of map from variable name to buffer count
			self.buffermap[name] = bufferCount
			
			if newBuffer:
				newBuffer = False
				bufferName = "Buffer%d" % bufferCount
				rec = "struct %s {" % bufferName

			if maxcount == 1:
				rec += "%s %s;" % (tname, name)
			else:				
				rec += "%s %s[%d];" % (tname, name, maxcount)

			if (len(rec) > maxlength) or \
				   (count >= len(self.vars)-1):
				rec += "};"
				newBuffer = True
				
				# evaluate it
				gROOT.ProcessLine(rec)

				# now import struct
				exec("from ROOT import %s" % bufferName)

				# add to list of buffers
				self.buffer.append(eval("%s()" % bufferName))

				# remember of update buffer count
				bufferCount += 1

		# create a generic event object
		self.event = Buffer(self.buffer, self.buffermap, self.vars)
		
		# Now that addresses are stable, give address of each variable
		for tname, name, maxcount in self.vars:
			jj = self.buffermap[name]
			tree.SetBranchAddress(name, AddressOf(self.buffer[jj], name))

	# destructor
	def __del__(self):
		pass

	def entries(self):
		return self.entries

	def read(self, row):
		self.tree.GetEntry(row)

	def get(self, variable):
		if buffermap.has_key(variable):
			jj = buffermap[variable]
			return self.buffer[jj].__getattribute__(variable)
		else:
			return None
		
	# Implement Python iterator protocol
	
	def __iter__(self):
		return self

	def next(self):
		if self.row > self.entries-1:
			self.row = 0
			raise StopIteration
		else:
			self.read(self.row)
			
## 			if len(self.buffer) == 1:
## 				data = self.buffer[0]
## 			else:
## 				# map to a single large Python class
## 				data = self.event
			self.row += 1
			return self.event
