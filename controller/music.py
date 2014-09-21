#!/usr/bin/python
from subprocess import Popen
from time import sleep
import random

sounds = ["track0", "track1", "track2", "track3", "track4"]

def play_beats(beats):
	beats = map(int, beats)
	timestamp_tracks = calculate_timestamps(beats)
	timestamps = sorted(timestamp_tracks.keys())
	for i in range(len(timestamps)):
		if i == 0:
			delta = 0
		else:
			delta = timestamps[i] - timestamps[i-1]
		sleep(delta)
		play_sound(timestamp_tracks[timestamps[i]])

def calculate_timestamps(beats):
	timestamps = {}	
	for i, frequency in enumerate(beats):
		period = 1.0/frequency
		offset = random.randrange(100)*1.0/100
		track_timestamps = [round(j*period + offset, 2) for j in range(frequency)]
		for timestamp in track_timestamps:
			timestamps[timestamp] = i
	return timestamps

def play_sound(track):
	Popen(["afplay", "../sounds/%s.wav" % sounds[track]])
