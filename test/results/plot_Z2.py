#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: plot.py
# Description: plot results of training
# Created: 25-Feb-2014 HBP
#------------------------------------------------------------------------------
import os, sys, re
from time import sleep
from ROOT import *
from histutil import *
from math import *
#------------------------------------------------------------------------------
def main():
    gROOT.ProcessLine('.L Z2mass_2_26_14.cpp+')
    
    ntuple = Ntuple('../data/ppZZ.root', 'Events')
  #  if not ntuple.good():
   #     print "can't open file"

    setStyle()
    
    canvas = TCanvas('fig_Z2mass', 'Z2mass', 10, 10, 500, 500)
    h2 = mkhist2('hZ2mass', 'Z2mass (GeV)', 'Z2mass(BNN) (GeV)',
                 100, 0, 100, 100, 0, 100,
                 color=kBlue, msize=0.5)
    h2.Draw()

    for row, event in enumerate(ntuple):
        if row < 2000: continue
        
        mass = Z2mass_2_26_14(event.lept3_pt, event.lept3_eta, event.lept3_phi,
                      event.lept4_pt, event.lept4_eta, event.lept4_phi)
        h2.Fill(event.Z2mass, 100 * mass)
        if row % 100 == 0:
            canvas.cd()
            h2.Draw('p same')
            canvas.Update()
        if row > 5000: break
    canvas.SaveAs('.pdf')
    sleep(5)
#-----------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print
    print 'ciao!'
    print
    
