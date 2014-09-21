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

NUM_TRACKS = 5

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
		new_track = int(open("track_info", "rb").read())
		if new_track != current_track: tracks[current_track].force_finished()
		current_track = new_track

		# Play all tracks
		tracks[current_track].next_measurement(float(line))
		for i in range(NUM_TRACKS):
			if i != current_track: 
				tracks[i].play_auto()

WAIT_STATE = 0
BEATS_STATE = 1
FINISHED_STATE = 2
UPPER_THRESHOLD = 1.1
LOWER_THRESHOLD = 1.1
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

	def should_move_to_beats_state(self):
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

	# Tiny state machine
	def next_measurement(self, datum):
		self.data.append(datum)

		if self.current_state == WAIT_STATE:
			if self.should_move_to_beats_state():
				self.puts("Beat")
				self.current_state = BEATS_STATE
				self.previous_last_played_manualbeat = self.last_played_manualbeat
				self.last_played_manualbeat = time.time()
				self.play()

			elif self.should_move_to_finished_state():
				self.puts("Finished")
				self.current_state = FINISHED_STATE
				self.time_period = self.last_played_manualbeat - self.previous_last_played_manualbeat
				self.puts(self.time_period)

		elif self.current_state == FINISHED_STATE:
			if self.should_move_to_beats_state():
				self.puts("Beat")
				self.current_state = BEATS_STATE
				self.play()

			else:
				# We're staying in FINISHED_STATE, so we should carry on playing a beat at the speed last recorded
				self.play_auto()

		elif self.current_state == BEATS_STATE:
			if self.should_finish_beats_state():
				self.puts("Wait")
				self.current_state = WAIT_STATE

	def puts(self, msg):
		print "%d: %s" % (self.track, msg)

	def play_auto(self):
		time_delta = time.time() - self.last_played_autobeat
		if self.time_period > 0 and time_delta > self.time_period:
			print "%d play_auto" % self.track
			self.play()
			self.last_played_autobeat = time.time()

	def force_finished(self):
		self.current_state = FINISHED_STATE
		self.time_period = self.last_played_manualbeat - self.previous_last_played_manualbeat
		self.puts(self.time_period)

	def play(self):
		print "Play"
		if self.last_sound == FIRST_SOUND and self.high_frequency():
			play_sound("track%db" % self.track)
			self.last_sound = SECOND_SOUND
		else:
			play_sound("track%da" % self.track)
			self.last_sound = FIRST_SOUND

	def high_frequency(self):
		self.time_period = self.last_played_manualbeat - self.previous_last_played_manualbeat
		frequency = 1.0/self.time_period
		return (frequency > HIGH_FREQUENCY_THRESHOLD)


def play_sound(fname):
	print "Playing %s" % fname
	Popen(["afplay", "../sounds/%s.wav" % fname])

main()

