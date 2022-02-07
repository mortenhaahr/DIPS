#include <iostream>
#include <random>
#include <thread>
#include <chrono>

typedef struct {
    uint64_t t[3] = {0, 0, 0};
    uint8_t new_message = 0;

} time_vector_t;

std::ostream& operator<<(std::ostream& os, const time_vector_t& vec) {
    os << "[" << vec.t[0] << ", " << vec.t[1] << ", " << vec.t[2] << "]";
    return os;
}

time_vector_t message[3];

void do_internal(time_vector_t &local_time, int index, const std::string& thread) {
    if ((std::rand() % 3) == 0) {
        local_time.t[index]++;
        std::cout << thread << " Internal event. New time: " << local_time << "\n";
    }
}

void send_message(time_vector_t &local_time, int index, int to_thread_index, const std::string& thread) {
    if ((std::rand() % 3) == 0) {
        local_time.t[index]++;
        message[to_thread_index] = local_time;
        message[to_thread_index].new_message = index + 1;
        std::cout << thread << " Sent message to T"<< to_thread_index << ". New time: " << local_time << "\n";
    }
}

void recv_message(time_vector_t &local_time, int index, const std::string& thread) {
    if (message[index].new_message) {

        for (auto i = 0; i < 3; i++) {
            local_time.t[i] = std::max(message[index].t[i], local_time.t[i]);
        }

        local_time.t[index]++;

        std::cout << thread << " Received message from T" << message[index].new_message - 1 << ". New time: " << local_time << "\n";
        message[index].new_message = 0;
    }
}

void f0() {
    time_vector_t local_time;
    while(1) {
        do_internal(local_time, 0, "T0:");
        recv_message(local_time, 0, "T0:");
        send_message(local_time, 0, 1, "T0:");
        send_message(local_time, 0, 2, "T0:");
        std::this_thread::sleep_for(std::chrono::milliseconds(900));
    }
}

void f1() {
    time_vector_t local_time;
    while(1) {
        do_internal(local_time, 1, "T1:");
        recv_message(local_time, 1, "T1:");
        send_message(local_time, 1, 0, "T1:");
        send_message(local_time, 1, 2, "T1:");
        std::this_thread::sleep_for(std::chrono::milliseconds(1400));
    }
}

void f2() {
    time_vector_t local_time;
    while(1) {
        do_internal(local_time, 2, "T2:");
        recv_message(local_time, 2, "T2:");
        send_message(local_time, 2, 0, "T2:");
        send_message(local_time, 2, 1, "T2:");
        std::this_thread::sleep_for(std::chrono::milliseconds(2000));
    }
}

int main() {
    std::cout << "Hello, World!" << std::endl;

    std::srand(std::time(0));

    auto tmp = std::thread(f0);
    auto tmp1 = std::thread(f1);
    auto tmp2 = std::thread(f2);

    while(1);
    return 0;
}
