#
# Raspberry PI implementation of the eZ80 Zilog Debug Interface
#
# The Zilog Debug Interface (ZDI) provides a built-in debugging interface
# to the eZ80 # CPU. ZDI provides basic in-circuit emulation features including:
#     * Examining and modifying internal registers
#     * Examining and modifying memory
#     * Starting and stopping the user program
#     * Setting program and data BREAK points
#     * Single-stepping the user program
#     * Executing user-supplied instructions
#     * Debugging the final product with the inclusion of one small connector
#     * Downloading code into SRAM
#
# see: page 165 in the datasheet
#      https://www.zilog.com/docs/ez80acclaim/ps0153.pdf
#

from gpiozero import InputDevice, OutputDevice
import time

class EZ80Status:
    def __init__(self, status_byte):
        self


class ZdiHighLevel:
    def __init__(self, pin_clk="GPIO17", pin_data="GPIO27", ez80_clk_freq_hz=20000):
        self.zdi = ZdiLowLevel(pin_clk, pin_data, ez80_clk_freq_hz)

    def reset_ez80(self):
        self.zdi.write_bytes_to_registers(ZdiLowLevel.WRITE_REGISTER_MASTER_CONTROL, [0xf0])

    def read_product_id(self):
        """
        returns the 2 byte product id. for eZ80F92 it should be [0x00, 0x07]
        """
        return self.zdi.read_bytes_from_registers(ZdiLowLevel.READ_REGISTER_ID_L, 2)

    def read_product_revision(self):
        """
        returns the one byte revision
        """
        return self.zdi.read_bytes_from_registers(ZdiLowLevel.READ_REGISTER_ID_U, 1)[0]

    def read_registers_mbase_f_a(self):

    def read_registers_bcu_b_c(self):

    def read_registers_deu_d_e(self):

    def read_registers_ix(self):

    def read_registers_iy(self):

    def read_stack_pointer(self):
        # first get acl mode to see how much bytes we need to read?

    def read_memory_from_current_pc(self):

    def set_adl(self):

    def reset_adl(self):

    def write_registers_mbase_f_a(self, mbase, f, a):

    def write_registers_bcu_b_c(self, bcu, b, c):

    def write_registers_deu_d_e(self, deu, d, e):

    def write_registers_ix(self, ixu, ixh, ixl):

    def write_registers_iy(self, iyu, iyh, iyl):

    def write_stack_pointer_short(self, sph, spl):

    def write_stack_pointer_long(self, spu, sph, spl):

    def write_memory_from_current_pc(self, bytes_to_write):
        self.zdi.write_bytes_to_registers(ZdiLowLevel.WRITE_REGISTER_MEMORY, bytes_to_write)

    def execute_instructions(self, opcodes):
        """up to 5 opcodes, executed by the eZ80 immediately"""
        reversed_opcodes=opcodes[::-1]
        start_address = ZdiLowLevel.WRITE_REGISTER_INSTRUCTION_STORE_0 + len(opcodes) + 1
        self.zdi.write_bytes_to_registers(start_address, reversed_opcodes)



class ZdiLowLevel:
    def __init__(self, pin_clk="GPIO17", pin_data="GPIO27", ez80_clk_freq_hz=20000):
        self.pin_clk = pin_clk
        self.pin_data = pin_data

        # the ZDI clock speed must be slower than the eZ80 clock speed and of course way
        # slower than the raspberry pi speed. So we will sleep at least 3 eZ80 CPU cycles
        # between each transition in the ZDI (so the zdi clock speed will be at least 6
        # times slower than eZ80 clock speed)
        self.sleep_time = 3 / ez80_clk_freq_hz

        # we initialize bot the zdi clock and the data pins to be high and output
        self.data = OutputDevice(pin=pin_data,  active_high=True, initial_value=True)
        self.clk = OutputDevice(pin=pin_clk,  active_high=True, initial_value=True)

    def write_bytes_to_registers(self, start_register, bytes_to_write):
        self.start()
        # writing 7 bit register address
        self.write_bits_to_bus(ZDI.number_to_bin_array(start_register, 7))
        # writing the '0' write indicator bit
        self.write_bits_to_bus([0])

        for value in bytes_to_write:
            # writing a single bit byte separator (value '1')
            self.write_bits_to_bus([1])
            # writing 8 bit data
            self.write_bits_to_bus(ZDI.number_to_bin_array(value, 8))

        # writing a last bit (value '1'), but keeping the clock high,
        # indicating the end of the operation (a new start can begin)
        self.write_bits_to_bus([1], last_bit=True)

    def read_bytes_from_registers(self, start_register, number_of_bytes):
        self.start()
        # writing 7 bit register address
        self.write_bits_to_bus(ZDI.number_to_bin_array(start_register, 7))
        # writing the '1' write indicator bit
        self.write_bits_to_bus([1])

        # changing to read mode
        self.data.close()
        self.data = InputDevice(pin=self.pin_data, active_state=True)

        bytes_read = []
        for byte_idx in range(number_of_bytes):
            byte = 0
            for y in range(8):
                time.sleep(self.sleep_time)
                self.clk.on()
                time.sleep(self.sleep_time)

                # we can read the data on the High-To-Low clock transition
                self.clk.off()
                time.sleep(self.sleep_time)
                byte = (byte << 1) | self.data.is_active()

            bytes_read.append(byte)

            # advancing the clock once for the byte separator, if there will be more bytes
            # (we don't care about the value of the byte separator)
            if byte_idx < number_of_bytes - 1:
                time.sleep(self.sleep_time)
                self.clk.on()
                time.sleep(self.sleep_time)

        # changing back to write mode on the data pin (we will need that for the next start)
        self.data.close()
        self.data = OutputDevice(pin=pin_data,  active_high=True, initial_value=None)

        # setting a last bit (value '1'), but keeping the clock high,
        # indicating the end of the operation (a new start can begin)
        self.write_bits_to_bus([1], last_bit=True)

        return bytes_read

    def write_bits_to_bus(self, bits, last_bit=False):
        """
        Writing bits to the bus. Expecting to be called during low clock state.
        When returns, leaves the clock in low state normally, unless this is the
        last bit of the operation, in which case it keeps the clock in a high state,
        st that a new start can be called.
        """
        for data_bit in bits:
            # setting the data pin
            time.sleep(self.sleep_time)
            if data_bit == 1:
                self.data.on()
            else:
                self.data.off()
            time.sleep(self.sleep_time)

            # eZ80 will read the data on the Low-To-High clock transition
            self.clk.on()
            time.sleep(self.sleep_time)
            self.clk.off()

    def close(self):
        # setting everything to High (as this is the default)
        self.clk.on()
        self.data.on()
        time.sleep(self.sleep_time)

        self.clk.close()
        self.data.close()

    def start(self):
        """
        All ZDI commands are preceded by the ZDI START signal, which is a High-to-Low
        transition of the data pin when the clock is High.
        """
        time.sleep(self.sleep_time)
        self.data.off()
        time.sleep(self.sleep_time)
        self.clk.off()

    @staticmethod
    def number_to_bin_array(num, array_length=8):
        # we only need the last 'array_length' bit
        num = num % (2 ** array_length)
        length_format = "0"+array_length+"b"
        return [int(x) for x in format(num, length_format)]

    WRITE_REGISTER_ADDRESS_0_L = 0x00
    WRITE_REGISTER_ADDRESS_0_H = 0x01
    WRITE_REGISTER_ADDRESS_0_U = 0x02
    WRITE_REGISTER_ADDRESS_1_L = 0x04
    WRITE_REGISTER_ADDRESS_1_H = 0x05
    WRITE_REGISTER_ADDRESS_1_U = 0x06
    WRITE_REGISTER_ADDRESS_2_L = 0x08
    WRITE_REGISTER_ADDRESS_2_H = 0x09
    WRITE_REGISTER_ADDRESS_2_U = 0x0A
    WRITE_REGISTER_ADDRESS_3_L = 0x0C
    WRITE_REGISTER_ADDRESS_3_H = 0x0D
    WRITE_REGISTER_ADDRESS_3_U = 0x0E
    WRITE_REGISTER_BREAK_CONTROL = 0x10
    WRITE_REGISTER_MASTER_CONTROL = 0x11
    WRITE_REGISTER_DATA_L = 0x13
    WRITE_REGISTER_DATA_H = 0x14
    WRITE_REGISTER_DATA_U = 0x15
    WRITE_REGISTER_READ_WRITE_CONTROL = 0x16
    WRITE_REGISTER_BUS_CONTROL = 0x17
    WRITE_REGISTER_INSTRUCTION_STORE_4 = 0x21
    WRITE_REGISTER_INSTRUCTION_STORE_3 = 0x22
    WRITE_REGISTER_INSTRUCTION_STORE_2 = 0x23
    WRITE_REGISTER_INSTRUCTION_STORE_1 = 0x24
    WRITE_REGISTER_INSTRUCTION_STORE_0 = 0x25
    WRITE_REGISTER_MEMORY = 0x30

    READ_REGISTER_ID_L = 0x00
    READ_REGISTER_ID_H = 0x01
    READ_REGISTER_ID_U = 0x02
    READ_REGISTER_STATUS = 0x03
    READ_REGISTER_MEMORY_ADDRESS_L = 0x10
    READ_REGISTER_MEMORY_ADDRESS_H = 0x11
    READ_REGISTER_MEMORY_ADDRESS_U = 0x12
    READ_REGISTER_BUS_STATUS = 0x17
    READ_REGISTER_MEMORY_DATA = 0x20


