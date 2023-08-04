import os
import shutil

import cantools
import math

# Generate CPP code from DBC file for a ODRIVE motor controller
# The main class will be ODriveCAN and it will have a method for each message in the DBC file that is sent to the ODRIVE
# It will also have a method for processing each can message that has the same ID as the instance of the class
main_header_template = """#ifndef {class_name}_H
#define {class_name}_H

#include <stdint.h>
#include <stdbool.h>
#include <FlexCAN_T4.h>

class {class_name} {{
public:
    {class_name}(uint8_t node_id, FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_64> *can_bus);
    
    void process_can_message(CAN_message_t &msg);
    
    {public_methods}
    
private:
    uint8_t node_id;
    FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_64> *can_bus;
    
    {variables}
    
    // CAN message processing
    {private_methods}
}};

"""

main_cpp_template = """#include "{class_name}.h"

{class_name}::{class_name}(uint8_t node_id, FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_64> *can_bus) {{
    this->node_id = node_id;
    this->can_bus = can_bus;
}}

{methods} 

// Because the ODrive ID is mixed with the message ID we need to bitwise it out
// Upper 6 bits - Node ID - max 0x3F
// Lower 5 bits - Command ID - max 0x1F

void {class_name}::process_can_message(CAN_message_t &msg) {{
    uint8_t node_id = (msg.id >> 5) & 0x3F;
    uint8_t command_id = msg.id & 0x1F;
    if (node_id != this->node_id) return;
    switch (command_id) {{
        {switch}
    }}
}}

"""


class CANMessage:

    def __init__(self, dbc_message):
        self.name = dbc_message.name
        self.id = dbc_message.frame_id
        self.signals = dbc_message.signals
        self.length = dbc_message.length
        self.is_extended_frame = dbc_message.is_extended_frame

    def generate_send_method(self):
        method = "void send_" + self.name + "("
        for signal in self.signals:
            method += CANMessage.signal_data_type(signal) + " " + CANMessage.signal_variable_name(signal.name) + ", "
        method = method[:-2] + ");"
        return method

    def generate_process_method(self):
        method = "void process_" + self.name + "(CAN_message_t &msg);"
        return method

    def generate_process_method_cpp(self):
        pass

    @staticmethod
    def build_name(name):
        nodes = name.split("_")
        nodes[0] = nodes[0].title()
        return "".join(nodes)

    @staticmethod
    def signal_variable_name(signal_name):
        return "m_" + CANMessage.build_name(signal_name)

    @staticmethod
    def isFloat(signal):
        return True if isinstance(signal.scale, float) else False

    @staticmethod
    def signal_data_type(signal):
        if not signal.choices:
            if CANMessage.isFloat(signal):
                return "float"
            else:
                return "int" if signal.is_signed else "uint" + str((math.floor((signal.length - 1) / 8) + 1) * 8) + "_t"
        else:
            return signal.name

    @staticmethod
    def process_float_cpp(signal):
        # Because floats might not be 32 bits we need to convert them to a 32 bit float and then use the scale value to
        # convert it back to the correct value
        msg = "float " + CANMessage.signal_variable_name(signal.name) + " = "
        msg += "((float)msg.buf[" + str(signal.start) + "] / 8) * " + str(signal.scale) + " + " + str(signal.offset)
        msg += ";"
        return msg

    @staticmethod
    def process_int_cpp(signal):
        msg = CANMessage.signal_data_type(signal) + " " + CANMessage.signal_variable_name(signal.name) + " = "
        msg += "msg.buf[" + str(signal.start)
        msg += ";"
        return msg


class ODriveCANGenerator:

    def __init__(self, dbc_file, output_dir):
        self.dbc_file = dbc_file
        self.output_dir = output_dir
        self.db = cantools.database.load_file(self.dbc_file)
        self.messages = self.db.messages
        self.message_holders = []

        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.mkdir(self.output_dir)

        self.class_name = "ODriveCAN"
        self.class_file = os.path.join(self.output_dir, self.class_name + ".h")
        self.class_file_cpp = os.path.join(self.output_dir, self.class_name + ".cpp")

        self.generate_message_holders()

    def generate_message_holders(self):
        for message in self.messages:
            self.message_holders.append(CANMessage(message))

if __name__ == '__main__':
    generator = ODriveCANGenerator("ODRIVECAN.dbc", "output")
