#include "CommandDownlinkTypeSupportImpl.h"
#include <mutex> // Required for Thread Synchronization

// Global Mutex to prevent data collision when multiple DDS threads fire at once
std::mutex udp_tx_mutex;

class WeaponDownlinkListener : public DDS::DataReaderListener {
public:
    int tx_socket_fd;
    struct sockaddr_in dtic_hardware_addr;

    void on_data_available(DDS::DataReader_ptr reader) override {
        AegisActuationCommandDataReader_var cmd_reader = AegisActuationCommandDataReader::_narrow(reader);
        AegisActuationCommand cmd;
        DDS::SampleInfo info;

        // DDS may call this function simultaneously across multiple cores
        if (cmd_reader->take_next_sample(cmd, info) == DDS::RETCODE_OK) {
            if (info.valid_data) {
                uint32_t outbound_payload[4]; 

                outbound_payload[0] = htonl(cmd.raw_launcher_azimuth);
                outbound_payload[1] = htonl(cmd.raw_launcher_elevation);
                outbound_payload[2] = htonl(cmd.fire_trigger_bitmask);

                uint32_t crc_val = cmd.raw_launcher_azimuth ^ cmd.raw_launcher_elevation ^ cmd.fire_trigger_bitmask;
                outbound_payload[3] = htonl(crc_val);

                // CRITICAL: Lock the UDP socket so parallel cores don't interleave bytes on the wire
                std::lock_guard<std::mutex> lock(udp_tx_mutex);
                
                sendto(tx_socket_fd, outbound_payload, 16, 0, 
                       (struct sockaddr*)&dtic_hardware_addr, sizeof(dtic_hardware_addr));
            }
        }
    }
};
