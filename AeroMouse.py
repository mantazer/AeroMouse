__author__ = 'muntaserahmed'

import sys
import Leap

from pymouse import PyMouse
from numpy import interp

# Initialize PyMouse object

FINGER_MOUSE = PyMouse()

# Grab screen size and x-axis, y-axis bounds

SCREEN_SIZE = FINGER_MOUSE.screen_size();
SCREEN_WIDTH_MIN = 0
SCREEN_WIDTH_MAX = SCREEN_SIZE[0]   #1280
SCREEN_HEIGHT_MIN = 0
SCREEN_HEIGHT_MAX = SCREEN_SIZE[1]  #800

# Predefined x-axis, y-axis bounds for Leap Motion Controller

LEAP_WIDTH_MIN = -40
LEAP_WIDTH_MAX = 40
LEAP_HEIGHT_MIN = 100
LEAP_HEIGHT_MAX = 180


# Custom LeapListener implementation

class LeapListener(Leap.Listener):
    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
            frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        if not frame.hands.is_empty:
            # Get the first hand
            hand = frame.hands[0]

            # Check if the hand has any fingers
            fingers = hand.fingers
            if not fingers.is_empty:
                # Calculate the hand's average finger tip position
                avg_pos = Leap.Vector()
                for finger in fingers:
                    avg_pos += finger.tip_position
                avg_pos /= len(fingers)

                # Grab average position on x, y, and z axes
                x_pos = avg_pos[0]
                y_pos = avg_pos[1]
                z_pos = avg_pos[2]

                # Call the move_cursor function to perform calculations and move the cursor
                move_cursor(x_pos, y_pos)

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""


def move_cursor(x_pos, y_pos):

    # If x-axis data from controller is outside the bounds, default them

    if x_pos < LEAP_WIDTH_MIN:
        scaled_x = SCREEN_WIDTH_MIN
    elif x_pos > LEAP_WIDTH_MAX:
        scaled_x = SCREEN_WIDTH_MAX
    else:
        # Linear interpolation from the controller's x-axis range to the screen width
        scaled_x = interp(x_pos, [LEAP_WIDTH_MIN, LEAP_WIDTH_MAX], [SCREEN_WIDTH_MIN, SCREEN_WIDTH_MAX])

    # If y-axis data from controller is outside bounds, default them

    if y_pos < LEAP_HEIGHT_MIN:
        scaled_y = SCREEN_HEIGHT_MIN
    elif y_pos > LEAP_HEIGHT_MAX:
        scaled_y = SCREEN_HEIGHT_MAX
    else:
        # Linear interpolation from the controller's y-axis range to the screen height
        scaled_y = interp(y_pos, [LEAP_HEIGHT_MIN, LEAP_HEIGHT_MAX], [SCREEN_HEIGHT_MAX, SCREEN_HEIGHT_MIN])

    print 'SCALED X: ' + str(scaled_x) + ',  SCALED Y: ' + str(scaled_y)

    # Move

    FINGER_MOUSE.move(scaled_x, scaled_y)


def main():
    # Create a sample listener and controller
    listener = LeapListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()
