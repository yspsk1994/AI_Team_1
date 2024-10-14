import time

def exec_db():
    print("Database Thread started")
    for i in range(6):
        time.sleep(10)  # Simulate database operation
        print(f"Database Component running cnt: {10*(i+1)}")
    print("Database Thread finished")