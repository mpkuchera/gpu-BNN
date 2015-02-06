#!/usr/bin/env python
#------------------------------------------------------------------------------
#- File: plot.py
#- Description: Make plots
#- Created:     28-Apr-2009 Harrison B. Prosper
#------------------------------------------------------------------------------
import os, sys
from ROOT import *
from histutil import *
from time import sleep
#------------------------------------------------------------------------------
XNBINS= 40
XMIN  = -2.0
XMAX  =  2.0

YNBINS= 40
YMIN  = -2.0
YMAX  = 2.0
#------------------------------------------------------------------------------
def main():
	gROOT.ProcessLine(".L reg_12_9_13.cpp+")
	setStyle()

	c  = TCanvas("fig_sinxcosy_3_24", "", 0, 0, 800, 400)
	c.Divide(2,1)

	h1 = mkhist2("h1", "x", "y", XNBINS, XMIN, XMAX, YNBINS, YMIN, YMAX)
	h2 = mkhist2("h2", "x", "y", XNBINS, XMIN, XMAX, YNBINS, YMIN, YMAX)

	h1.GetYaxis().SetTitleOffset(1.4);
	h2.GetYaxis().SetTitleOffset(1.4);
	xstep = (XMAX-XMIN)/XNBINS
	ystep = (YMAX-YMIN)/YNBINS
	for i in xrange(XNBINS):
		x = XMIN + (i+0.5)*xstep
		for j in xrange(YNBINS):
			y = YMIN + (j+0.5)*ystep
			z = reg_12_9_13(x, y)
			z1= sin(x)*cos(y)
			h1.Fill(x, y, z)
			h2.Fill(x, y, z1)

	c.cd(1)
	h1.Draw("SURF1")
	c.cd(2)
	h2.Draw("SURF1")
	c.Update()
	c.SaveAs(".gif")
	c.SaveAs(".pdf")
	sleep(5)
#------------------------------------------------------------------------------
main()
