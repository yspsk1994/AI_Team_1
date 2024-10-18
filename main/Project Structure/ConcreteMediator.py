class ConcreteMediator:
    def __init__(self, cam1_queue, cam2_queue, ui_queue, function_queue):
        self.users = {}
        self.cam1_queue = cam1_queue
        self.cam2_queue = cam2_queue
        self.ui_queue = ui_queue
        self.function_queue = function_queue

    def add_user(self, user):
        self.users[user.name] = user
        user.set_mediator(self)

    def send_message(self, target, message_type, data=None):
        if target == "UI":
            if message_type == "UPDATE_BOOK_LIST_1":
                self.ui_queue.put(("UPDATE_BOOK_LIST_1", data))
            elif message_type == "UPDATE_BOOK_LIST_2":
                self.ui_queue.put(("UPDATE_BOOK_LIST_2", data))
