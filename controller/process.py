#!/usr/bin/python
import numpy as np
import threading
import matplotlib.pyplot as plt
import scipy.signal as signal
from sys import stdin
import time
from subprocess import Popen
from time import sleep
import random
import math

NUM_TRACKS = 25
RECORD_MODE = 0
LISTEN_MODE = 1

def main():
	current_track = 0
	tracks = [Track(i) for i in range(NUM_TRACKS)]

	while 1:
		# Read stdin
		line = stdin.readline()
		if not line: break
		line = line.replace("\r", "").replace("\n", "")
		if len(line) == 0: next

		# Switch tracks
		new_track_str = open("track_info", "rb").read()
		if new_track_str == "": continue
		new_track = int(new_track_str)
		if new_track != current_track: tracks[current_track].force_finished()
		current_track = new_track

		# Switch modes
		mode = open("mode_info", "rb").read().rstrip()
		if mode == "record":
			mode = RECORD_MODE
		else:
			mode = LISTEN_MODE

		# Harmonise frequencies of all non-current tracks
		time_periods = [tracks[i].time_period for i in range(NUM_TRACKS) if i != current_track]
		time_periods = [period for period in time_periods if period > 0]
		if len(time_periods) > 0:
			base_period = max(time_periods)
			for i in range(NUM_TRACKS):
				if i != current_track or (i == current_track and tracks[i].current_state == FINISHED_STATE and tracks[i].time_period < base_period):
					tp = tracks[i].time_period
					if tp == 0: continue
					current_multiplier = base_period / tp
					new_multiplier = int(math.ceil(current_multiplier))
					if current_multiplier != new_multiplier:
						tracks[i].time_period = base_period / new_multiplier
						print ""
						print "timeperiods" + str(time_periods)
						print "baseperiod    : %.2f" % base_period
						print "timeperiod old: %.2f" % tp
						print "multiplier old: %.2f" % current_multiplier
						print "multiplier new: %.2f" % new_multiplier
						print "timeperiod new: %.2f" % tracks[i].time_period

		# Play all tracks
		tracks[current_track].next_measurement(float(line), mode)
		for i in range(NUM_TRACKS):
			if i != current_track: 
				tracks[i].play_auto()

WAIT_STATE = 0
BEATS_STATE = 1
FINISHED_STATE = 2
UPPER_THRESHOLD = 1.3
LOWER_THRESHOLD = 1.3
FINISHED_MULTIPLIER = 40
FINISHED_RATE = 0.01 * 0.1
N = 50
SAMPLING_FREQUENCY = 1000
MIN_SPECTRUM_AMPLITUDE = 0.01
FIRST_SOUND = 0
SECOND_SOUND = 1
HIGH_FREQUENCY_THRESHOLD = 1.0

class Track:
	def __init__(self, track):
		self.data = []
		self.current_state = WAIT_STATE
		self.time_period = 0
		self.last_played_autobeat = time.time()
		self.last_played_manualbeat = 0
		self.previous_last_played_manualbeat = 0
		self.track = track
		self.last_sound = FIRST_SOUND
		self.high_frequency = False

	def should_move_to_beats_state(self):
		if len(self.data) < 5: return False
		last_n = self.data[-N-1:-1]
		over_threshold = map(lambda x: x < UPPER_THRESHOLD, last_n)
		return sum(over_threshold) == 0

	def should_finish_beats_state(self):
		last_n = self.data[-N-1:-1]
		under_threshold = map(lambda x: x > LOWER_THRESHOLD, last_n)
		return sum(under_threshold) == 0

	def should_move_to_finished_state(self):
		offset = FINISHED_MULTIPLIER*N
		if len(self.data) < offset: return False
		else: return sum(map(lambda x: x > LOWER_THRESHOLD, self.data[-(offset+1):-1])) < offset*FINISHED_RATE

	def sound_needed(self):
		time_delta = time.time() - self.last_played_autobeat
		return (self.time_period <= 0) or (time_delta >= self.time_period)

	# Tiny state machine
	def next_measurement(self, datum, mode):
		self.data.append(datum)

		if self.current_state == WAIT_STATE:
			if self.should_move_to_beats_state():
				self.puts("Beat")
				self.current_state = BEATS_STATE
				self.play_manual(mode)

			elif self.should_move_to_finished_state() and self.sound_needed():
				self.puts("Finished")
				self.current_state = FINISHED_STATE
				self.puts(self.time_period)

		elif self.current_state == FINISHED_STATE:
			if self.should_move_to_beats_state():
				self.puts("Beat")
				self.current_state = BEATS_STATE
				self.play_manual(mode)

			else:
				# We're staying in FINISHED_STATE, so we should carry on playing a beat at the speed last recorded
				self.play_auto()

		elif self.current_state == BEATS_STATE:
			if self.should_finish_beats_state():
				self.puts("Wait")
				self.current_state = WAIT_STATE

	def puts(self, msg):
		return True
		# print "%d: %s" % (self.track, msg)

	def play_manual(self, mode):
		if mode == RECORD_MODE:
			self.previous_last_played_manualbeat = self.last_played_manualbeat
			self.last_played_manualbeat = time.time()
			self.time_period = self.last_played_manualbeat - self.previous_last_played_manualbeat
			print "UPDATING TIME PERIOD %d" % self.track
			self.update_high_frequency()
		self.play()

	def play_auto(self):
		time_delta = time.time() - self.last_played_autobeat
		if self.time_period > 0 and time_delta > self.time_period:
			self.puts("play_auto")
			self.play()
			self.last_played_autobeat = time.time()

	def force_finished(self):
		self.current_state = FINISHED_STATE
		self.puts(self.time_period)

	def play(self):
		if self.last_sound == FIRST_SOUND and self.high_frequency:
			play_sound("track%db" % self.track)
			self.last_sound = SECOND_SOUND
		else:
			play_sound("track%da" % self.track)
			self.last_sound = FIRST_SOUND

	def update_high_frequency(self):
		frequency = 1.0/self.time_period
		self.high_frequency = (frequency > HIGH_FREQUENCY_THRESHOLD)


def play_sound(fname):
	print "Playing %s" % fname
	Popen(["afplay", "../sounds/%s.wav" % fname])

main()

