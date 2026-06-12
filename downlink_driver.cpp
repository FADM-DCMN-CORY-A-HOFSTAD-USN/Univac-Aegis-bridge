// Append or include alongside your existing C++ network driver environment
#include "CommandDownlinkTypeSupportImpl.h"

// Listener class that fires a callback whenever Aegis issues a fire command
class WeaponDownlinkListener : public DDS::DataReaderListener {
public:
    int tx_socket_fd;
    struct sockaddr_in dtic_hardware_addr;

    void on_data_available(DDS::DataReader_ptr reader) override {
        AegisActuationCommandDataReader_var cmd_reader = AegisActuationCommandDataReader::_narrow(reader);
        AegisActuationCommand cmd;
        DDS::SampleInfo info;

        if (cmd_reader->take_next_sample(cmd, info) == DDS::RETCODE_OK) {
            if (info.valid_data) {
                uint32_t outbound_payload[4]; // Expanded to 4 words to include CRC-32 checksum

                // Convert Little-Endian Aegis math into Big-Endian layout for UNIVAC registers
                outbound_payload[0] = htonl(cmd.raw_launcher_azimuth);
                outbound_payload[1] = htonl(cmd.raw_launcher_elevation);
                outbound_payload[2] = htonl(cmd.fire_trigger_bitmask);

                // Calculate simple logical parity checksum (XOR) for the hardened ACTUATE.CMS fallback logic
                uint32_t crc_val = cmd.raw_launcher_azimuth ^ cmd.raw_launcher_elevation ^ cmd.fire_trigger_bitmask;
                outbound_payload[3] = htonl(crc_val);

                // Push raw 16-byte payload over Ethernet straight to the FPGA interface unit
                sendto(tx_socket_fd, outbound_payload, 16, 0, 
                       (struct sockaddr*)&dtic_hardware_addr, sizeof(dtic_hardware_addr));
            }
        }
    }
};
