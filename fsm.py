import anki_vector
import imgclassification
from transition import machine

class StateMachine(object):
    states = ['surveillance','defuse_bomb','in_the_heights', "burn_notice"]

    def __init__(self, robot):
        self.machine = Machine(model=self, states=self.states, initial='surveillance')
        self.robot = robot

        self.machine.add_transition(trigger='order', source='surveillance', dest='defuse_bomb')
        self.machine.add_transition(trigger='drone', source='surveillance', dest='in_the_heights')
        self.machine.add_transition(trigger='inspection', source='surveillance', dest='burn_notice')
        self.machine.add_transition(trigger='return_idle', source='defuse_bomb', dest='surveillance')
        self.machine.add_transition(trigger='return_idle', source='in_the_heights', dest='surveillance')
        self.machine.add_transition(trigger='return_idle', source='burn_notice', dest='surveillance')

    def run():
        while True:
            if self.machine.state == 'surveillance':
                surveillance()
            if self.machine.state == 'defuse_bomb':
                defuse_bomb()
            if self.machine.state == 'in_the_heights':
                in_the_heights()
            if self.machine.state == 'burn_notice':
                burn_notice()

    def surveillance():

        # Place holder for transitions
        if label == 'order':
            state.order()
        if label == 'drone':
            state.drone()
        if label == 'order':
            state.inspection()

    def defuse_bomb():
        state.return_idle()


    def in_the_heights():
        state.return_idle()


    def burn_notice():
        state.return_idle()

    def connect_robot():
        self.robot.connect()

    def disconnect_robot():
        self.robot.disconnect()


if __name__ == '__main__':

    # Create a Robot object
    robot = anki_vector.Robot()
    state_machine = StateMachine(robot)
    state_machine.connect_robot()
    state_machine.run()
    state_machine.disconnect_robot()
