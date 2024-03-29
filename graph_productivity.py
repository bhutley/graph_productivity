#!/usr/bin/python
#
# graph_productivity.py
# 
# Author: Brett Hutley <brett@hutley.net>
#
# This code is to extract the list of Pomodoros from my Mac OS/X calendar
# using the program 'callistevents' https://github.com/bhutley/callistevents
# and then create a bar-chart aggregating the work done each hour, in order
# to show how my productivity looks during the day.
# 
# By default it will create a chart called graph_productivity.png in
# the current directory. You can specify a different output file using
# the '-o' command-line option.
#
import os, sys
import subprocess
import datetime
import argparse


parser = argparse.ArgumentParser(description="Generate a bar-chart of your hourly productivity by processing all the Pomodoro entries in your Pomodoro calendar for the current day")

parser.add_argument('-o', nargs='?',
                    dest='outfile',
                    default='productivity.png',
                    help='The PNG file containing the chart')

parser.add_argument('-i', nargs='?',
                    dest='infile',
                    default='productivity_data.txt',
                    help='The text file containing productivity data')

parser.add_argument('-W', nargs='?',
                    dest='width',
                    type=int,
                    default=600,
                    help='The width in pixels of the PNG file')
parser.add_argument('-H', nargs='?',
                    dest='height',
                    type=int,
                    default=400,
                    help='The height in pixels of the PNG file')

args = parser.parse_args()

if not args.infile:
    print("Error: An input file must be specified")
    exit(0)

filename = args.infile

time_buckets = [0.0 for i in xrange(0, 24)]


ttl_mins_worked = 0

start_date = datetime.date.today()
start_date_str = ("%d-%02d-%02d" % (start_date.year, start_date.month, start_date.day, ))

file = open(filename, 'r')
for line in file:
    fields = line.split("\t")
    if len(fields) >= 3:
        sta = fields[0]
        end = fields[1]

        if len(sta) == 19 and len(end) == 19:
            sta_hr = int(sta[11:13])
            sta_mn = int(sta[14:16])

            end_hr = int(end[11:13])
            end_mn = int(end[14:16])

            if sta_hr == end_hr:
                mins = end_mn - sta_mn
                ttl_mins_worked += mins
                time_buckets[sta_hr] += float(mins) / 60.0
            else:
                for h in xrange(sta_hr, end_hr+1):
                    if h == sta_hr:
                        mins = 60.0 - sta_mn
                        ttl_mins_worked += mins
                        time_buckets[sta_hr] += float(mins) / 60.0
                    elif h == end_hr:
                        mins = end_mn
                        ttl_mins_worked += mins
                        time_buckets[end_hr] += float(mins) / 60.0
                    else:
                        ttl_mins_worked += 60
                        time_buckets[h] += 1.0

## OK, the code following is for generating the plot.
# The code above has no dependencies on matplotlib

import numpy as n
from pylab import figure, show
import matplotlib.cm as cm
import matplotlib.colors as colors

colours_to_use = [
    '#000000',
    '#990000',
    '#CC0000',
    '#994C00',
    '#CC6600',
    '#999900',
    '#FFFF00',
    '#009900',
    '#00CC00',
    '#00FF00',
    '#33FF33',
]

width = 1.0
fig = figure(1, figsize=(float(args.width) / 100.0, float(args.height) / 100.0))
ax = fig.add_subplot(111)
rects1 = ax.bar(xrange(0, 24), time_buckets, width,
                    color='r')

cc = colors.ColorConverter()
for i in xrange(0, len(time_buckets)):
    offset = int(round(time_buckets[i] * 10.0))
    if offset >= len(colours_to_use):
        offset = len(colours_to_use)-1
    r = rects1[i]
    r.set_color( cc.to_rgb(colours_to_use[offset]) )


ax.set_ylabel('Productivity')
ax.set_xlabel('Hour')
ax.set_title('Productivity for %s' % (start_date_str, ))
ax.set_axis_bgcolor('#EEE9E9')
ax.set_ylim(0, 1.0)
ax.set_xticks(xrange(0, 24))

hours_worked = int(float(ttl_mins_worked) / 60.0)
minutes_worked = (ttl_mins_worked % 60)
ax.text(0.5, 0.9, "Time worked: %d:%02d" % (hours_worked, minutes_worked ), color='#2f4f4f' )

for tick in ax.xaxis.get_major_ticks():
    #tick.label.set_fontsize(14) 
    # specify integer or one of preset strings, e.g.
    tick.label.set_fontsize('x-small') 
    tick.label.set_rotation('vertical')

for tick in ax.yaxis.get_major_ticks():
    #tick.label.set_fontsize(14) 
    # specify integer or one of preset strings, e.g.
    tick.label.set_fontsize('x-small') 


fig.savefig(args.outfile, format="png", dpi=100)
