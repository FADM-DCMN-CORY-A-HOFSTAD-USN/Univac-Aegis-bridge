#include <iostream>
#include <cstring>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <thread>
#include <vector>
#include <sched.h>     
#include <pthread.h>   
#include "TacticalTrackTypeSupportImpl.h" 

#define PORT 5005
#define BUFFER_SIZE 16  

uint32_t convert_big_endian_to_native(uint32_t value) {
    return ntohl(value);
}

void uplink_worker(int core_id, LegacyTrackDataWriter_var track_writer) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    int server_fd;
    struct sockaddr_in address;
    uint32_t network_buffer[4];
    
    if ((server_fd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) return;

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt))) return;
    
    std::memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; 
    address.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        close(server_fd);
        return;
    }

    std::cout << "[INFO] Core " << core_id << " pinned and listening." << std::endl;

    while (true) {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        
        ssize_t bytes_received = recvfrom(server_fd, network_buffer, BUFFER_SIZE, 0,
                                          (struct sockaddr*)&client_addr, &addr_len);
                                          
        if (bytes_received == BUFFER_SIZE) {
            LegacyTrack track_msg;
            track_msg.track_id           = convert_big_endian_to_native(network_buffer[0]) & 0x3FFFFFFF;
            track_msg.target_range_yds   = convert_big_endian_to_native(network_buffer[1]);
            track_msg.target_bearing_min = convert_big_endian_to_native(network_buffer[2]);
            track_msg.target_altitude_ft = convert_big_endian_to_native(network_buffer[3]);
            
            track_writer->write(track_msg, DDS::HANDLE_NIL);
        }
    }
    close(server_fd);
}

int main() {
    auto participant = DDS::DomainParticipantFactory::get_instance()->create_participant(
        0, PARTICIPANT_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
        
    LegacyTrackTypeSupport_var ts = new LegacyTrackTypeSupportImpl();
    ts->register_type(participant.in(), "");
    
    auto topic = participant->create_topic(
        "Aegis_Legacy_Tracks", ts->get_type_name(), TOPIC_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
        
    auto publisher = participant->create_publisher(PUBLISHER_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
    auto writer = publisher->create_datawriter_with_profile(
        topic.in(), "TacticalCombatLibrary", "HighPriorityTargetProfile", nullptr, STATUS_MASK_NONE);
        
    LegacyTrackDataWriter_var track_writer = LegacyTrackDataWriter::_narrow(writer.in());

    unsigned int num_cores = std::thread::hardware_concurrency();
    std::cout << "[INFO] Detected " << num_cores << " CPU cores. Spawning UDP worker array..." << std::endl;

    std::vector<std::thread> worker_threads;
    for (unsigned int i = 0; i < num_cores; ++i) {
        worker_threads.emplace_back(uplink_worker, i, track_writer);
    }

    for (auto& t : worker_threads) {
        if (t.joinable()) t.join();
    }
    return 0;
}
