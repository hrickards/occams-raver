#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from sys import stdin
import time

NUM_TRACKS = 5
CURRENT_TRACK = 0
TRACK_FREQS = [0]*NUM_TRACKS

def main():
	# Estimate sampling frequency
	# estimate_fs()

	# Read in piped streamed input
	while 1:
		line = stdin.readline()
		if not line: break

		# Ignore blank lines
		line = line.replace("\r", "").replace("\n", "")
		if len(line) == 0: next

		check_track()
		process_line(line)

NUM_TIMING_MEASUREMENTS = 100
SAMPLING_FREQUENCY = 200
def estimate_fs():
	start = time.time()
	i = 0
	while i < NUM_TIMING_MEASUREMENTS:
		line = stdin.readline()
		line = line.replace("\r", "").replace("\n", "")
		if len(line) != 0: i += 1
	end = time.time()
	delta = (end-start)/(NUM_TIMING_MEASUREMENTS)
	SAMPLING_FREQUENCY = 1/delta
	print "Measured Fs: %.2f" % SAMPLING_FREQUENCY

accelerations = []
ACCELERATION_BIN_SIZE = 5*SAMPLING_FREQUENCY

def process_line(line):
	global accelerations

	acceleration = float(line)

	accelerations.append(acceleration)
	if len(accelerations) % ACCELERATION_BIN_SIZE == 0:
		print ACCELERATION_BIN_SIZE
		process_bin(accelerations)
		accelerations = []
		print_progress()

MIN_VAL = 0.01
def process_bin(data):
	f, Pwelch_spec = signal.welch(data, SAMPLING_FREQUENCY, scaling='spectrum', nperseg=512)
	max_i, max_v = max(enumerate(Pwelch_spec), key=lambda p: p[1])
	max_f = f[max_i]
	if max_v < MIN_VAL: max_f = 0
	print CURRENT_TRACK
	TRACK_FREQS[CURRENT_TRACK] = max_f / 2 # Up then down means we need to halve the frequency

def print_progress():
	print "%.2f %.2f %.2f %.2f %.2f" % (TRACK_FREQS[0], TRACK_FREQS[1], TRACK_FREQS[2], TRACK_FREQS[3], TRACK_FREQS[4])

def check_track():
	global CURRENT_TRACK
	CURRENT_TRACK = int(open('track_info', 'rb').read())

main()
