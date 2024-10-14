from ConcreteMediator import ConcreteMediator
from MT_Cam import MT_Cam
from MT_Function import MT_Function

import time

class SmartLibrary:
    def __init__(self, name, mediator):
        self.name = name
        self.mediator = mediator


mediator = ConcreteMediator()

main_cam_thread = MT_Cam(mediator, "Cam_Thread")
main_function_thread = MT_Function(mediator, "Function_Thread")

mediator.add_user(main_cam_thread)
mediator.add_user(main_function_thread)

main_cam_thread.start()
main_function_thread.start()
