// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#define _USE_MATH_DEFINES
#include <cmath>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <string>

// The only file that needs to be included to use the Myo C++ SDK is myo.hpp.
#include <myo/myo.hpp>

// Classes that inherit from myo::DeviceListener can be used to receive events from Myo devices. DeviceListener
// provides several virtual functions for handling different kinds of events. If you do not override an event, the
// default behavior is to do nothing.

class DataCollector : public myo::DeviceListener {
public:
    DataCollector()
    : onArm(false), fist(false), roll(0), pitch(0), yaw(0)
    {
    }

    // onUnpair() is called whenever the Myo is disconnected from Myo Connect by the user.
    void onUnpair(myo::Myo* myo, uint64_t timestamp)
    {
        // We've lost a Myo.
        // Let's clean up some leftover state.
				onArm = false;
				fist = false;
				roll = 0;
				pitch = 0;
				yaw = 0;
    }

		void onPose(myo::Myo* myo, uint64_t timestamp, myo::Pose pose)
    {
        if (pose == myo::Pose::fist) {
						fist = true;
            myo->vibrate(myo::Myo::vibrationMedium);
        } else {
						fist = false;
				}
    }

    void onOrientationData(myo::Myo* myo, uint64_t timestamp, const myo::Quaternion<float>& quat)
    {
        using std::atan2;
        using std::asin;
        using std::sqrt;
        // Calculate Euler angles (roll, pitch, and yaw) from the unit quaternion.
        roll = atan2(2.0f * (quat.w() * quat.x() + quat.y() * quat.z()),
                           1.0f - 2.0f * (quat.x() * quat.x() + quat.y() * quat.y()));
        pitch = asin(2.0f * (quat.w() * quat.y() - quat.z() * quat.x()));
        yaw = atan2(2.0f * (quat.w() * quat.z() + quat.x() * quat.y()),
                        1.0f - 2.0f * (quat.y() * quat.y() + quat.z() * quat.z()));
    }
		

		void onArmRecognized(myo::Myo* myo, uint64_t timestamp, myo::Arm arm, myo::XDirection xDirection)
    {
        onArm = true;
    }

		void onArmLost(myo::Myo* myo, uint64_t timestamp)
		{
				onArm = false;
		}

    void print()
    {
				std::cout << '\r';
				if (onArm && fist)
				{
					std::cout << std::to_string(roll);
					std::cout << ",";
					std::cout << std::to_string(pitch);
					std::cout << ",";
					std::cout << std::to_string(yaw);
				} else {
					std::cout << "neutral,";
					std::cout << std::to_string(roll);
					std::cout << ",";
					std::cout << std::to_string(pitch);
					std::cout << ",";
					std::cout << std::to_string(yaw);
				}
				std::cout << std::endl;
				std::cout << std::flush;
    }

		bool onArm;
		bool fist;
		float roll, pitch, yaw;
};


int main(int argc, char** argv)
{
    // We catch any exceptions that might occur below -- see the catch statement for more details.
    try {
    // First, we create a Hub with our application identifier. Be sure not to use the com.example namespace when
    // publishing your application. The Hub provides access to one or more Myos.
    myo::Hub hub("com.example.hello-myo");

    // Next, we attempt to find a Myo to use. If a Myo is already paired in Myo Connect, this will return that Myo
    // immediately.
    // waitForAnyMyo() takes a timeout value in milliseconds. In this case we will try to find a Myo for 10 seconds, and
    // if that fails, the function will return a null pointer.
    myo::Myo* myo = hub.waitForMyo(10000);

    // If waitForAnyMyo() returned a null pointer, we failed to find a Myo, so exit with an error message.
    if (!myo) {
        throw std::runtime_error("Unable to find a Myo!");
    }

    // Next we construct an instance of our DeviceListener, so that we can register it with the Hub.
    DataCollector collector;
    // Hub::addListener() takes the address of any object whose class inherits from DeviceListener, and will cause
    // Hub::run() to send events to all registered device listeners.
    hub.addListener(&collector);

    // Finally we enter our main loop.
    while (1) {
        // In each iteration of our main loop, we run the Myo event loop for a set number of milliseconds.
        // In this case, we wish to update our display 20 times a second, so we run for 1000/20 milliseconds.
        hub.run(1000/20);

        // After processing events, we call the print() member function we defined above to print out the values we've
        // obtained from any events that have occurred.
        collector.print();
    }

    // If a standard exception occurred, we print out its message and exit.
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cerr << "Press enter to continue.";
        std::cin.ignore();
        return 1;
    }
}
