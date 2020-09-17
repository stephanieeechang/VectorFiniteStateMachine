import asyncio
import anki_vector
import time
import sys
from anki_vector.util import degrees, distance_mm, speed_mmps
import imgclassification
from transitions import Machine


class StateMachine(object):
    states = ['surveillance', 'defuse_bomb', 'in_the_heights', "burn_notice"]

    def __init__(self, robot):
        self.machine = Machine(model=self, states=self.states, initial='surveillance')
        self.robot = robot

        self.machine.add_transition(trigger='order', source='surveillance', dest='defuse_bomb')
        self.machine.add_transition(trigger='drone', source='surveillance', dest='in_the_heights')
        self.machine.add_transition(trigger='inspection', source='surveillance', dest='burn_notice')
        self.machine.add_transition(trigger='return_idle', source='defuse_bomb', dest='surveillance')
        self.machine.add_transition(trigger='return_idle', source='in_the_heights', dest='surveillance')
        self.machine.add_transition(trigger='return_idle', source='burn_notice', dest='surveillance')

    def run(self):
        while True:
            print("State: " + self.state)
            if self.state == 'surveillance':
                self.surveillance()
            if self.state == 'defuse_bomb':
                self.defuse_bomb()
            if self.state == 'in_the_heights':
                self.in_the_heights()
            if self.state == 'burn_notice':
                self.burn_notice()

    def surveillance(self):
        set_head_angle = self.robot.behavior.set_head_angle(degrees(0))
        set_head_angle.result()
        say_state = self.robot.behavior.say_text("Surveillance!")
        say_state.result()

        label = None
        # Place holder for transitions
        if label == 'order':
            self.order()
        if label == 'drone':
            self.drone()
        if label == 'order':
            self.inspection()

    def defuse_bomb(self):
        say_state = self.robot.behavior.say_text("Defuse the Bomb!")
        say_state.result()
        # Return to IDLE
        self.return_idle()

    def in_the_heights(self):
        say_state = self.robot.behavior.say_text("In the Heights")
        say_state.result()
        # Face Animation
        face_animation = self.robot.anim.play_animation('anim_eyepose_blink_bd_r')
        # Say SOS!
        say_sos = self.robot.behavior.say_text("S--O--S! Someone’s spying on us! Inform headquarters.")
        self.move_in_s_formation()
        # Make sure SOS is said
        say_sos.result()
        # Make sure animation is done
        face_animation.result()

        # Return to IDLE
        self.return_idle()

    def burn_notice(self):
        say_state = self.robot.behavior.say_text("Burn Notice")
        say_state.result()

        say_text = self.robot.behavior.say_text("I'm not a spy.")

        # Turn right to start walking in square
        turn_right = self.robot.behavior.turn_in_place(degrees(-90))
        say_text.result()
        turn_right.result()

        for i in range(4):
            degree = 90
            if i == 3:
                degree = 180
            self.burn_notice_routine(degree)

        # Make sure lift is lowered
        lower_lift_end = self.robot.behavior.set_lift_height(0.0)
        lower_lift_end.result()

        # Return to IDLE
        self.return_idle()

    def connect_robot(self):
        self.robot.connect()

    def disconnect_robot(self):
        self.robot.disconnect()

    def move_in_s_formation(self):
        # Turn right to start making an S formation
        turn_right = self.robot.behavior.turn_in_place(degrees(-90))
        # Wait until turn_right is completed
        turn_right.result()
        # Complete the first half of S
        first_half_s = self.robot.motors.set_wheel_motors(25, 50)
        time.sleep(10)
        # Wait until the first half is done
        first_half_s.result()
        # Complete the second half of S
        second_half_s = self.robot.motors.set_wheel_motors(50, 25)
        time.sleep(10)
        # Wait until the second half is done
        second_half_s.result()
        # Stop the motors
        stop_motion = self.robot.motors.stop_all_motors()
        stop_motion.result()

    def burn_notice_routine(self, degree=90):
        say_text_1 = self.robot.behavior.say_text("I am not a spy.")
        raise_lift = self.robot.behavior.set_lift_height(height=1.0, duration=2.0)
        drive_straight = self.robot.behavior.drive_straight(distance_mm(200), speed_mmps(50))
        raise_lift.result()
        say_text_1.result()
        say_text_2 = self.robot.behavior.say_text("I am not a spy.")
        lower_lift = self.robot.behavior.set_lift_height(height=0.0, duration=2.0)
        lower_lift.result()
        say_text_2.result()
        drive_straight.result()
        say_text_4 = self.robot.behavior.say_text("I am not a spy.")
        turn_left = self.robot.behavior.turn_in_place(degrees(degree))
        say_text_4.result()
        turn_left.result()


async def main():
    serial = sys.argv[1]
    print("Serial Number: " + serial)
    robot = anki_vector.AsyncRobot(serial=serial)
    state_machine = StateMachine(robot)
    state_machine.connect_robot()
    state_machine.run()
    state_machine.disconnect_robot()


if __name__ == '__main__':
    asyncio.run(main())
