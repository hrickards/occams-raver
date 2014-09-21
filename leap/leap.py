# Setup import path so we can import leap
import os, sys, inspect, thread, time
from os import system
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = './lib'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

class LeapListener(Leap.Listener):
		def on_connect(self, controller):
			print "Connected"

		def on_frame(self, controller):
			frame = controller.frame()

			if len(frame.hands) > 1:
				print len(frame.hands)
				system("afplay /Users/rickards/src/unhackathon/myo/sounds/du_hast2.wav")

			print "%d hands, %d fingers" % (len(frame.hands), len(frame.fingers))

def main():
	# Listen to events from the LeapMotion
	listener = LeapListener()
	controller = Leap.Controller()
	controller.add_listener(listener)

	# Keep this process running until Enter is pressed
	print "Press Enter to quit..."
	try:
		sys.stdin.readline()
	except KeyboardInterrupt:
		pass
	finally:
		controller.remove_listener(listener)

if __name__ == "__main__":
    main()
