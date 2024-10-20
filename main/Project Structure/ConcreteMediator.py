import queue

class ConcreteMediator:
    def __init__(self, cam1_queue,cam2_queue, widget_cam_1_queue,widget_cam_2_queue, function_1_queue,function_2_queue):
        self.cam1_queue = cam1_queue
        self.cam2_queue = cam2_queue
        self.widget_cam_1_queue = widget_cam_1_queue
        self.widget_cam_2_queue = widget_cam_2_queue
        self.function_1_queue = function_1_queue
        self.function_2_queue = function_2_queue
        
        self.message_queue = queue.Queue()
        self.ui = None
        self.mt_function = None
        self.mt_db = None

    def add_user(self, user):
        user.set_mediator(self)
        user_name = user.__class__.__name__
        if user_name == "MT_UI":
            self.ui = user
        elif user_name == "MT_Function":
            self.mt_function = user

    def send_message(self, target, message_type, data):
        if target == "UI" and self.ui:
            self.ui.update_data(message_type, data)
        elif target == "FUNCTION" and self.mt_function:
            self.mt_function.handle_message(message_type, data)
