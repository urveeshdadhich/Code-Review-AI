def divide_numbers(a, b):
    # Missing division by zero check
    return a / b

def get_element(my_list, index):
    # Missing bounds checking
    return my_list[index]

def read_file(filename):
    # Resource leak: file is not closed
    f = open(filename, 'r')
    return f.read()

if __name__ == "__main__":
    print("Result: " + divide_numbers(10, 0)) # Type mismatch bug
