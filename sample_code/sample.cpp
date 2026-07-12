#include <iostream>
#include <cstring>

void processInput(const char* input) {
    char buffer[10];
    
    // security vulnerability: buffer overflow
    strcpy(buffer, input); 
    
    std::cout << "Buffer contains: " << buffer << std::endl;
}

int main() {
    processInput("This string is way too long for the buffer");
    return 0;
}
