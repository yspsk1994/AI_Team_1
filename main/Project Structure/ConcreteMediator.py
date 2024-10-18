from Mediator import Mediator

class  ConcreteMediator (Mediator): 
    def  __init__ ( self ): 
        self.users = [] 
        
    def  add_user ( self, user ): 
         self.users.append(user) 

    def send_message(self, target, final_target, message, sender, data=None): 
        print(f"Sending message to {final_target} via Mediator")  # 로그 추가
        for user in self.users: 
            if user.name == target:
                user.receive_message(target, final_target,message, sender, data)