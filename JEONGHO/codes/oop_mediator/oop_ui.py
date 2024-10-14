import time

def exec_ui():
    print("UI Thread started")
    for i in range(12):
        time.sleep(5)  # Simulate UI operation
        print(f"UI Component running cnt: {5*(i+1)}")
    print("UI Thread finished")