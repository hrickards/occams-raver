#!/usr/bin/python
from sys import stdin
from os import system
import time
TRACK = 3
NUM_TRACKS = 5

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

		direction = process_line(line)
		change_track(direction)

PITCH_THRESHOLD = 0.5
YAW_THRESHOLD = 1.2
# Returns 0 for nothing, 1 for track up and 0 for track down
def process_line(line):
	if line[0:7] == "neutral":
		neutral, roll, pitch, yaw = line.split(",")
		yaw = float(yaw)
		if yaw > YAW_THRESHOLD:
			print "RECORD"
			f = open('mode_info', 'wb')
			f.write("record")
			f.close()
		else:
			f = open('mode_info', 'wb')
			f.write("listen")
			f.close()
			print "LISTEN"

	else:
		roll, pitch, yaw = map(float, line.split(","))

		if abs(pitch) < PITCH_THRESHOLD: return 0

		if pitch > 0: return -1
		else: return 1

PREVIOUS_TIMESTAMP = 0
MIN_TIME_DELTA = 1
def change_track(direction):
	global PREVIOUS_TIMESTAMP, TRACK

	if direction != 1 and direction != -1: return None

	current_timestamp = time.time()
	if (current_timestamp - PREVIOUS_TIMESTAMP) > MIN_TIME_DELTA:
		PREVIOUS_TIMESTAMP = current_timestamp
		
		TRACK = (TRACK + direction) % NUM_TRACKS
		system("terminal-notifier -message \"Switching to Track %d\"" % TRACK)
		f = open('track_info', 'wb')
		f.write(str(TRACK))
		f.close()

		if direction == 1: print "UP"
		else: print "DOWN"

main()
