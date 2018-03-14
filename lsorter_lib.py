import pigpio, time, sys, os

pi = pigpio.pi()

class slideturner():
    def __init__(self, num_boxes, min_servo=675, max_servo=2350, pin=4):
        self.num_boxes = num_boxes
        self.min_servo, self.max_servo = min_servo, max_servo
        if num_boxes < 1:
            raise ValueError("You must init at least one box")
        pi.set_mode(pin, pigpio.OUTPUT)
    def calc_pulse(self, box, verbose=True):#box is from 0 to self.num_boxes-1
        angle = 180/self.num_boxes * (box+0.5)
        pulse = (angle/180*(self.max_servo - self.min_servo)) + self.min_servo
        if not verbose:
            print("Angle:", angle, "\nPulselength:", pulse)
        return pulse
    def goto_angle(self, box, verbose=True):
        self.box = box
        pulse = calc_pulse(box, verbose=verbose)
        pi.set_servo_pulsewidth(17, pulse)
        