#!/usr/bin/python
# -*- coding: utf-8 -*-

import scribus
import getopt, sys


def usage():
    print """-o, --output=\toutput file
-t, --template=\ttemplate file
"""
try:
    opts, args = getopt.getopt(sys.argv[1:], "o:t:pa", ["output=", "template=",])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
    
for opt, arg in opts:
  if opt in ("-t", "--template"):
     template = arg
  elif opt in ("-o", "--output"):
     pdf_file = arg

scribus.openDoc(template)
pdf = scribus.PDFfile()
pdf.file = pdf_file
pdf.save()
