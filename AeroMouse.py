__author__ = 'muntaserahmed'

import sys
import Leap

from Leap import ScreenTapGesture, SwipeGesture
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from numpy import interp

import threading
from threading import Thread

# Initialize PyMouse object

AERO_MOUSE = PyMouse()
AERO_GESTURES = PyKeyboard()


# Grab screen size and x-axis, y-axis bounds

SCREEN_SIZE = AERO_MOUSE.screen_size()
SCREEN_WIDTH_MIN = 0
SCREEN_WIDTH_MAX = SCREEN_SIZE[0]
SCREEN_HEIGHT_MIN = 0
SCREEN_HEIGHT_MAX = SCREEN_SIZE[1]

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

                # Call the calc_position function to get scaled coordinates,
                scaled_x, scaled_y = calc_position(x_pos, y_pos)

                # Move the cursor
                AERO_MOUSE.move(scaled_x, scaled_y)

            #Gestures
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                    screen_tap = ScreenTapGesture(gesture)

                    print "Screen Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_string(gesture.state),
                        screen_tap.position, screen_tap.direction)

                    x_pos = screen_tap.position[0]
                    y_pos = screen_tap.position[1]
                    z_pos = screen_tap.position[2]

                    scaled_x, scaled_y = calc_position(x_pos, y_pos)

                    AERO_MOUSE.click(scaled_x, scaled_y)

                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    print "Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                        gesture.id, self.state_string(gesture.state),
                        swipe.position, swipe.direction, swipe.speed)

                    # Swipe Left -> Right
                    if swipe.position[0] > 0 and swipe.state == gesture.STATE_START:     # Swipe Left to Right (->)
                        print "Swiped Right"

                    elif swipe.position[0] < 0 and swipe.state == gesture.STATE_START:   # Swipe Right to Left (<-)
                        print "Swiped Left"

                    else:
                        pass    # do nothing

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"


def calc_position(x_pos, y_pos):

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
    return scaled_x, scaled_y


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
