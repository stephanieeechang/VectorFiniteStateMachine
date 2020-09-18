import asyncio
import anki_vector
import time
import sys
from anki_vector.util import degrees, distance_mm, speed_mmps
from imgclassification import ImageClassifier
from transitions import Machine
import datetime
import numpy as np
from skimage import io


class StateMachine(object):
    states = ['surveillance', 'defuse_bomb', 'in_the_heights', "burn_notice"]

    def __init__(self, robot):
        self.machine = Machine(model=self, states=self.states, initial='surveillance')
        self.robot = robot
        self.img_clf = ImageClassifier()

        self.machine.add_transition(trigger='order', source='surveillance', dest='defuse_bomb')
        self.machine.add_transition(trigger='drone', source='surveillance', dest='in_the_heights')
        self.machine.add_transition(trigger='inspection', source='surveillance', dest='burn_notice')
        self.machine.add_transition(trigger='return_idle', source='defuse_bomb', dest='surveillance')
        self.machine.add_transition(trigger='return_idle', source='in_the_heights', dest='surveillance')
        self.machine.add_transition(trigger='return_idle', source='burn_notice', dest='surveillance')

    def run(self):
        # load training data
        (train_raw, train_labels) = self.img_clf.load_data_from_folder('./train/')
        # convert images into features
        train_data = self.img_clf.extract_image_features(train_raw)
        # train model
        self.img_clf.train_classifier(train_data, train_labels)

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

    def imread_convert(self, f):
        return io.imread(f).astype(np.uint8)

    def surveillance(self):
        set_head_angle = self.robot.behavior.set_head_angle(degrees(0))
        set_head_angle.result()
        say_state = self.robot.behavior.say_text("Surveillance!")
        say_state.result()

        label = None
        while label is None:
            say_state = self.robot.behavior.say_text("Taking a picture!")
            say_state.result()
            time.sleep(3)
            latest_image = self.robot.camera.latest_image
            scaled_image = latest_image.annotate_image(scale=0.7)
            # image = asarray(Image.open("./outputs/" + "img_" + timestamp + ".bmp"))
            say_state = self.robot.behavior.say_text("Picture taken")
            say_state.result()
            timestamp = datetime.datetime.now().strftime("%dT%H%M%S%f")
            # image_raw = latest_image.raw_image
            scaled_image.save("./outputs/" + "img_" + timestamp + ".bmp")
            ic = io.ImageCollection("./outputs/" + "img_" + timestamp + ".bmp", load_func=self.imread_convert)
            image = io.concatenate_images(ic)
            img_processed = self.img_clf.extract_image_features(image)
            label = self.img_clf.predict_labels(img_processed)
            print(label)

        # Place holder for transitions
        if label == 'order':
            say_state = self.robot.behavior.say_text("Order")
            say_state.result()
            self.defuse_bomb()
        if label == 'drone':
            say_state = self.robot.behavior.say_text("Drone")
            say_state.result()
            self.in_the_heights()
        if label == 'inspection':
            say_state = self.robot.behavior.say_text("Inspection")
            say_state.result()
            self.burn_notice()

    def defuse_bomb(self):
        say_state = self.robot.behavior.say_text("Defuse the Bomb!")
        say_state.result()
        # self.robot.world.connect_cube()
        cube = self.robot.world.light_cube
        # get_cube = self.robot.behavior.dock_with_cube(cube)
        # get_cube.result()
        pickup_cube = self.robot.behavior.pickup_object(target_object=cube)
        pickup_cube.result()
        drive_forward = self.robot.behavior.drive_straight(distance_mm(330), speed_mmps(50))
        drive_forward.result()
        place_cube = self.robot.behavior.place_object_on_ground_here(num_retries=5)
        place_cube.result()
        drive_back = self.robot.behavior.drive_straight(distance_mm(-380), speed_mmps(50))
        drive_back.result()
        # Return to IDLE
        self.surveillance()

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
        self.surveillance()

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
        self.surveillance()

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
        first_half_s = self.robot.motors.set_wheel_motors(25, 75)
        time.sleep(7)
        # Wait until the first half is done
        first_half_s.result()
        # Complete the second half of S
        second_half_s = self.robot.motors.set_wheel_motors(75, 25)
        time.sleep(7)
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
    robot = anki_vector.AsyncRobot(serial=serial, show_viewer=True)
    state_machine = StateMachine(robot)
    state_machine.connect_robot()
    state_machine.run()
    state_machine.disconnect_robot()


if __name__ == '__main__':
    asyncio.run(main())
