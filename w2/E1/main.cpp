#include <iostream>
#include <thread>
#include <random>
#include <chrono>

uint64_t messages[2];

void f1() {

    uint64_t local_time = 0;
    while(1) {

        std::this_thread::sleep_for(std::chrono::milliseconds(900));
        // Sending message
        std::cout << "T1: Sending time: " << local_time << "\n";
        messages[1] = local_time;
        local_time++;

        // Receiving message (if any pending)
        if (messages[0]) {
            std::cout << "T1: Rcv message: " << messages[0] << "\tCurrent local time " << local_time << "\n";
            if (messages[0] > local_time) {
                local_time = messages[0];
            }
            local_time++;
            messages[0] = 0;
        }
        std::cout << "T1: (New) Local time " << local_time << "\n";

    }
}


void f2() {

    uint64_t local_time = 0;
    while(1) {

        std::this_thread::sleep_for(std::chrono::milliseconds(3000));
        // Sending message
        std::cout << "T2: Sending time: " << local_time << "\n";
        messages[0] = local_time;
        local_time++;

        // Receiving message (if any pending)
        if (messages[1]) {
            std::cout << "T2: Rcv message: " << messages[1] << "\tCurrent local time " << local_time << "\n";
            if (messages[1] > local_time) {
                local_time = messages[1];
            }
            local_time++;
            messages[1] = 0;
        }
        std::cout << "T2: (New) Local time " << local_time << "\n";

    }
}



int main() 
{
    auto tmp = std::thread(f1);
    auto tmp2 = std::thread(f2);

    while(1);
}