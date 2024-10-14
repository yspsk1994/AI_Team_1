import time

def exec_cam():
    print("Cam Thread started")
    for i in range(60):
        time.sleep(1)  # Simulate camera operation
        print(f"Cam Component running cnt: {i+1}") 
    print("Cam Thread finished")