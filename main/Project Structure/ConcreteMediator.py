from Mediator import Mediator

class  ConcreteMediator (Mediator): 
    def  __init__ ( self ): 
        self.users = [] 
        
    def  add_user ( self, user ): 
         self.users.append(user) 

    def send_message(self, target, message, sender, data=None): 
        for user in self.users: 
            if user == target:
                user.receive_message(message, sender, data)