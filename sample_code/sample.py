import os

def process_data(data):
    # bad practice: using eval
    result = eval(data)
    
    # security vulnerability: arbitrary command execution
    os.system(f"echo {data}")
    
    return result

if __name__ == "__main__":
    process_data("print('hello')")
