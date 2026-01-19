#!python
#

# [20260116] (air) parse a videi filename to get a usal title
#

import sys, os

import time
from datetime import datetime,timedelta
import isodate
import random
import json
import argparse
import csv
from io import StringIO
import re
from pprint import pprint

tests = [
    "CCC_8-5-6thRoutines10-06-87_atPatsStudio-00.07.09.742-00.12.42.239-seg3.mp4",
    "CCC_OldManAtTheMill_WilkinsSchool_09-07-94-00.00.17.361-00.06.04.842.mp4",
    "CCC_8-5-6thRoutines10-06-87_atPatsStudio-00.00.00.000-00.03.18.667-seg1.mp4",
    "CoalCountryCloggersAtMtAloysiusCollege03-14-1997__02____00.11.07.600-00.15.03.633-seg02.mp4",
    "'CoalCountryCloggers_George English Files-1991-00.00.08.467-00.57.18.867-seg02__02____00.00.00.167-00.03.29.487-seg02.mp4'",
    "CoalCountryConvention1989-00.00.00.000-00.55.31.807__01____00.00.00.000-00.08.50.796-seg01.mp4",
    "2596100-10-005__02____00.00.25.025-00.03.36.884-seg02__05____00.00.50.353-00.03.07.123.mp4",
    "2596100-04-008 FINAL-00.10.58.467-00.13.22.901-seg2.mp4",
    "CoalCountryCloggersRoaringSpringAltoona07-30-89_AAPL_MediaProductions-00.00.00.000-00.58.05.032.mp4",
    "",
    ]
    
pat = []
timept = '"\\d{2}.\\d{2}.\\d{2}.\\d{3}"'   #"'\d{2}.\d{2}.\d{2}.\d{3}'"
pat.extend([
    re.compile( r"(.+)(\d{2}.\d\d.\d\d.\d\d\d-\d\d.\d\d.\d\d.\d\d\d)(.+).mp4$" ),
    re.compile( r"(.+)(__\d{2}____)(.+).mp4" ),
#    re.compile( r"(.+)(-00)(.+).mp4" ),
],
           
           )

for p in pat :
    for t in tests :
        print("\t",end="")
        m = None
        m = re.search(p,t)
        if  m :
            print( '  ',t,'\n\t','-', m.group(1)," | ",  m.group(2), '\n' )
#            print( '  ',t,'\n\t','-', m.group(1)," | ",  m.group(2), " | ",m.group(3), '\n' )
            continue
        else :
            print("-")


#
