#Imports - General

import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser
from FaradayIO import cc430radioconfig


#Variables
local_device_callsign = 'KB1LQD' # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = 1 # Should match the connected Faraday unit as assigned in Proxy configuration

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()


# Verify UART communications
# Reset Device Debug Configuration Flash
# Verify SPI SRAM operation
# Verify FLASH updating
# Test GPIO
# Verify ADC's
# Verify GPS
# Verify Radio


############
## Verify UART Communcations
############

## ECHO MESSAGE

print "/n** Beginning ECHO command test** /n"



def TestEchoUart():
    #Display information
    for i in range(0,1):
        originalmsg = os.urandom(40)  # Cannot be longer than max UART payload size!
        # Use the general command library to send a text message to the Faraday UART "ECHO" command. Will only ECHO a SINGLE packet. This will send the payload of the message back (up to 62 bytes, this can be updated in firmware to 124!)
        faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT)
        command = faradaycommands.commandmodule.create_command_datagram(faraday_cmd.CMD_ECHO, originalmsg)
        faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
        # Retrive waiting data packet in UART Transport service number for the COMMAND application (Use GETWait() to block until ready or return False).
        rx_echo_raw = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT,
                                        sec_timeout=3)  # Wait for up to 3 seconds for data to arrive
        # Now parse data again
        b64_data = rx_echo_raw[0]['data']
        echo_decoded = faraday_1.DecodeRawPacket(b64_data)
        print repr(originalmsg)
        print repr(echo_decoded[0:len(originalmsg)]) #Note that ECHO sends back a fixed packed regardless. Should update to send back exact length.
        echo_len = len(originalmsg)
        if(originalmsg == echo_decoded[0:echo_len]):
            print "TEST: ECHO - Success"
        else:
            print "TEST: ECHO - Fail"


def GetDebugFlash():
    # Flush old data from UART service port
    faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT)

    # Command UART Telemetry Update NOW
    faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT,
                   faraday_cmd.CommandLocalSendTelemDeviceDebugFlash())

    # Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
    rx_debug_data = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT, 2,
                                      False)  # Will block and wait for given time until a packet is recevied

    # Decode the first packet in list from BASE 64 to a RAW bytesting
    rx_debug_data_pkt_decoded = faraday_1.DecodeRawPacket(rx_debug_data[0]['data'])

    # Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
    rx_debug_data_datagram = faraday_parser.UnpackDatagram(rx_debug_data_pkt_decoded, False)  # Debug is ON
    rx_debug_data_packet = rx_debug_data_datagram['PayloadData']

    # Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
    rx_debug_data_pkt_extracted = faraday_parser.ExtractPaddedPacket(rx_debug_data_packet, faraday_parser.packet_2_len)
    #
    # Parse the Telemetry #3 packet
    rx_debug_data_parsed = faraday_parser.UnpackPacket_2(rx_debug_data_pkt_extracted, debug=True)  # Debug ON

#
#
# ############
# ## Reset Device Debug Flash
# ############

rx_debug_data_parsed = GetDebugFlash()

print repr(rx_debug_data_parsed)

# Reset the device debug flash counters and data
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalResetDeviceDebugFlash())

# Sleep to allow unit to perform reset and be ready for next command
time.sleep(3)

rx_debug_data_parsed = GetDebugFlash()

print repr(rx_debug_data_parsed)
#
# ############
# ## Read System Settings
# ############
#
# #Flush old data from UART service port
# faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT)
#
# #Command UART Telemetry Update NOW
# faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalSendTelemDeviceSystemSettings())
#
# #Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
# rx_settings_data = faraday_1.GETWait(local_device_callsign, local_device_node_id,faraday_1.TELEMETRY_PORT, 1, False) #Will block and wait for given time until a packet is recevied
#
# #Decode the first packet in list from BASE 64 to a RAW bytesting
# rx_settings_pkt_decoded = faraday_1.DecodeRawPacket(rx_settings_data[0]['data'])
#
# #Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
# rx_settings_datagram = faraday_parser.UnpackDatagram(rx_settings_pkt_decoded, debug = False) #Debug is ON
# rx_settings_packet = rx_settings_datagram['PayloadData']
#
# #Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
# rx_settings_pkt_extracted = faraday_parser.ExtractPaddedPacket(rx_settings_packet, faraday_parser.packet_1_len)
#
# #Parse the Telemetry #3 packet
# rx_settings_parsed = faraday_parser.UnpackPacket_1(rx_settings_pkt_extracted, debug = False) #Debug ON
#
# # Print current Faraday radio frequency
# faraday_freq_mhz = cc430radioconfig.freq0_reverse_carrier_calculation(rx_settings_parsed['RF_Freq_2'], rx_settings_parsed['RF_Freq_1'], rx_settings_parsed['RF_Freq_0'])
# #print "Faraday's Current Frequency:", str(faraday_freq_mhz)[0:7], "MHz"
#
#
#
# ############
# ## Read Telemetry
# ############
#
# #Flush old data from UART service port
# faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT)
#
# #Command UART Telemetry Update NOW
# faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalUARTFaradayTelemetry())
#
# #Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
# rx_telem_data = faraday_1.GETWait(local_device_callsign, local_device_node_id,faraday_1.TELEMETRY_PORT, 1) #Will block and wait for given time until a packet is recevied
#
# #Decode the first packet in list from BASE 64 to a RAW bytesting
# rx_telem_pkt_decoded = faraday_1.DecodeRawPacket(rx_telem_data[0]['data'])
#
# #Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
# rx_telemetry_datagram = faraday_parser.UnpackDatagram(rx_telem_pkt_decoded) #Debug is OFF
# rx_telemetry_packet = rx_telemetry_datagram['PayloadData']
#
# #Extract the exact debug packet from longer datagram payload (Telemetry Packet #3)
# rx_telemetry_datagram_extracted = faraday_parser.ExtractPaddedPacket(rx_telemetry_packet, faraday_parser.packet_3_len)
#
# #Parse the Telemetry #3 packet
# rx_telemetry_packet_parsed = faraday_parser.UnpackPacket_3(rx_telemetry_datagram_extracted, debug = False) #Debug ON
#
# #print "Parsed packet dictionary:", rx_telemetry_packet_parsed


#TestEchoUart()