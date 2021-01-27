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
        self.current_breakpoints = [ [0x00, 0x00, 0x00],  # breakpoint 0: addr_u, addr_h, addr_l
                                     [0x00, 0x00, 0x00],  # breakpoint 1: addr_u, addr_h, addr_l
                                     [0x00, 0x00, 0x00],  # breakpoint 2: addr_u, addr_h, addr_l
                                     [0x00, 0x00, 0x00] ] # breakpoint 3: addr_u, addr_h, addr_l
        self.breakpoints_enabled = [False, False, False, False]
        self.break_now_enabled = False
        self.break_ignore_low_0_enabled = False
        self.break_ignore_low_1_enabled = False
        self.single_step_break_enabled = False

    def reset_ez80(self):
        # issue the reset command
        self.zdi.write_bytes_to_registers(ZdiLowLevel.WRITE_REGISTER_MASTER_CONTROL, [0xf0])

        # keep the eZ80 to remember the breakpoint settings we have stored, even if the reset would clean them
        b = [self.current_breakpoints[0][3], self.current_breakpoints[0][2], self.current_breakpoints[0][1],
             self.current_breakpoints[1][3], self.current_breakpoints[1][2], self.current_breakpoints[1][1],
             self.current_breakpoints[2][3], self.current_breakpoints[2][2], self.current_breakpoints[2][1],
             self.current_breakpoints[3][3], self.current_breakpoints[3][2], self.current_breakpoints[3][1]]
        self.zdi.write_bytes_to_registers(ZdiLowLevel.WRITE_REGISTER_BREAK_ADDRESS_0_L, b)
        self.zdi.update_break_control_register(self.breakpoints_enabled, self.is_cpu_in_break(),
                                               self.break_ignore_low_0_enabled, self.break_ignore_low_1_enabled,
                                               self.single_step_break_enabled)


    def read_product_id(self):
        """
        returns the 2 bytes long product id number (for eZ80F92 it should be 0x0007)
        """
        bytes = self.zdi.read_bytes_from_registers(ZdiLowLevel.READ_REGISTER_ID_L, 2)
        return bytes[0]*256 + bytes[1]

    def read_product_revision(self):
        """
        returns the product revision number (one byte)
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


    # ----------------------------------------------------------------------------------------
    # --                        breakpoint related debug operations                         --
    # ----------------------------------------------------------------------------------------

    def break_now(self):
        """
        Causing the CPU to halt on the next operation. After this you can use
        continue_after_break() to continue the execution or to step one operation.
        """
        self.break_now_enabled = True
        self.zdi.update_break_control_register(self.breakpoints_enabled, self.break_now_enabled,
                                               self.break_ignore_low_0_enabled, self.break_ignore_low_1_enabled,
                                               self.single_step_break_enabled)

    def continue_after_break(self, break_after_a_single_step=False):
        """
        Finishing the breaks and continue operations. By default the CPU will break again only
        if an enabled breakpoint triggers a halt. If break_after_a_single_step is set to True,
        the CPU will break in the next operation.
        """
        self.single_step_break_enabled = break_after_a_single_step
        self.break_now_enabled = False
        self.zdi.update_break_control_register(self.breakpoints_enabled, self.break_now_enabled,
                                               self.break_ignore_low_0_enabled, self.break_ignore_low_1_enabled,
                                               self.single_step_break_enabled)

    def set_breakpoint(self, breakpoint_id, addr_u, addr_h, addr_l, break_now=False):
        """
        ZDI supports to set 4 independent breakpoints, halting the CPU after the current
        operation, if the given address is accessed by the CPU. This function will set a
        breakpoint address and enable the given breakpoint.

        :param breakpoint_id: 0..3
        :param addru: most significant byte of the 24 bit address (when the CPU is in Z80 mode,
                      then the MBASE register will be used for the breakpoint instead of this
                      byte, so in this case anything can be set here)
        :param addrh: middle byte of the 24 bit address
        :param addrl: least significant byte of the 24 bit address (when it is set to None, then
                      the breakpoint will match on any address hitting this 256 byte long page.
                      This feature is enabled only for breakpoint 0 and 1)
        :param break_now: break the execution right now. Set this parameter to true, e.g if you
                          have the CPU in a break state and you want to set a new breakpoint
        """
        if breakpoint_id < 0 or breakpoint_id > 3:
            raise ValueError("breakpoint_id must be between 0..3")
        if addr_l is not None and (breakpoint_id != 0 and breakpoint_id != 1):
            raise ValueError("addr_l can not be None (only for breakpoint id 0 and 1)")
        if addr_l is not None and (addr_l < 0 or addr_l > 255):
            raise ValueError("addr_l must be between 0..255 (or None, for breakpoint id 0 and 1)")
        if addr_h is None or addr_h < 0 or addr_h > 255:
            raise ValueError("addr_h must be between 0..255 (and can not be None)")
        if addr_u is not None and (addr_h < 0 or addr_h > 255):
            raise ValueError("addr_u must be between 0..255 (and also can be None, but in this case make sure the CPU is in Z80 mode)")

        delta = breakpoint_id * 4
        if addr_u is not None and self.current_breakpoints[breakpoint_id][0] != addr_u:
            self.current_breakpoints[breakpoint_id][0] = addr_u
            self.zdi.write_bytes_to_registers(ZdiLowLevel.WRITE_REGISTER_BREAK_ADDRESS_0_U + delta, [addr_u])
        if addr_h is not None and self.current_breakpoints[breakpoint_id][1] != addr_h:
            self.current_breakpoints[breakpoint_id][1] = addr_h
            self.zdi.write_bytes_to_registers(ZdiLowLevel.WRITE_REGISTER_BREAK_ADDRESS_0_H + delta, [addr_h])
        if addr_l is not None and self.current_breakpoints[breakpoint_id][2] != addr_l:
            self.current_breakpoints[breakpoint_id][2] = addr_l
            self.zdi.write_bytes_to_registers(ZdiLowLevel.WRITE_REGISTER_BREAK_ADDRESS_0_L + delta, [addr_l])

        if breakpoint_id == 0:
            self.break_ignore_low_0_enabled = addr_l is None
        if breakpoint_id == 1:
            self.break_ignore_low_1_enabled = addr_l is None
        self.breakpoints_enabled[breakpoint_id] = True
        self.zdi.update_break_control_register(self.breakpoints_enabled, self.is_cpu_in_break(),
                                               self.break_ignore_low_0_enabled, self.break_ignore_low_1_enabled,
                                               self.single_step_break_enabled)

    def disable_breakpoint(self, breakpoint_id):
        if breakpoint_id < 0 or breakpoint_id > 3:
            raise ValueError("breakpoint_id must be between 0..3")
        self.breakpoints_enabled[breakpoint_id] = False
        self.zdi.update_break_control_register(self.breakpoints_enabled, self.is_cpu_in_break(),
                                               self.break_ignore_low_0_enabled, self.break_ignore_low_1_enabled,
                                               self.single_step_break_enabled)

    def is_cpu_in_break(self):
        return self.break_now_enabled or self.single_step_break_enabled

    def get_current_breakpoint_state(self):
        return {
            "is_cpu_in_break": self.is_cpu_in_break(),
            "current_breakpoints": self.current_breakpoints,
            "breakpoints_enabled": self.breakpoints_enabled,
            "break_ignore_low_0_enabled": self.break_ignore_low_0_enabled,
            "break_ignore_low_1_enabled": self.break_ignore_low_1_enabled
        }


class ZdiLowLevel:
    def __init__(self, pin_clk="GPIO17", pin_data="GPIO27", ez80_clk_freq_hz=20000):
        self.pin_clk = pin_clk
        self.pin_data = pin_data

        # the ZDI clock speed must be slower than the eZ80 clock speed and of course way
        # slower than the raspberry pi speed. So we will sleep at least 3 eZ80 CPU cycles
        # between each change in the ZDI pins. As we have at least 2 changes (usually more)
        # during each ZDI clock cycles, we expect the ZDI clock speed to be at least 6
        # times slower than eZ80 clock speed)
        self.sleep_time = 3 / ez80_clk_freq_hz

        # we initialize bot the zdi clock and the data pins to be high and output
        self.data = OutputDevice(pin=pin_data,  active_high=True, initial_value=True)
        self.clk = OutputDevice(pin=pin_clk,  active_high=True, initial_value=True)

    def write_bytes_to_registers(self, start_register, bytes_to_write):
        self.start()
        # writing 7 bit register address
        self.write_bits_to_bus(ZdiLowLevel.number_to_bin_array(start_register, 7))
        # writing the '0' write indicator bit
        self.write_bits_to_bus([0])

        for value in bytes_to_write:
            # writing a single bit byte separator (value '0') - making sure the CPU doesn't accept
            # bus request while the ZDI operation is ongoing.
            self.write_bits_to_bus([1])
            # writing 8 bit data
            self.write_bits_to_bus(ZdiLowLevel.number_to_bin_array(value, 8))

        # writing a last bit (value '1'), but keeping the clock high,
        # indicating the end of the operation (a new start can begin)
        self.write_single_bit_keeping_the_clock_high(1)

    def read_bytes_from_registers(self, start_register, number_of_bytes):
        self.start()
        # writing 7 bit register address
        self.write_bits_to_bus(ZdiLowLevel.number_to_bin_array(start_register, 7))
        # writing the '1' write indicator bit
        self.write_bits_to_bus([1])


        bytes_read = []
        for byte_idx in range(number_of_bytes):
            # changing to read mode
            self.data.close()
            self.data = InputDevice(pin=self.pin_data, active_state=True)

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

            # changing back to write mode on the data pin (we will either write a byte separator
            # now or finishing the operation)
            self.data.close()
            self.data = OutputDevice(pin=self.pin_data, active_high=True, initial_value=None)

            # advancing the clock once and write the byte separator, if there will be more bytes
            # we are writing a single bit byte separator (value '0') - making sure the CPU doesn't
            # accept bus request while the ZDI operation is ongoing.
            if byte_idx < number_of_bytes - 1:
                self.write_bits_to_bus([0])

        # setting a last bit (value '1'), but keeping the clock high,
        # indicating the end of the operation (a new start can begin)
        self.write_single_bit_keeping_the_clock_high(1)

        return bytes_read

    def write_single_bit_keeping_the_clock_high(self, data_bit):
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

    def write_bits_to_bus(self, bits):
        """
        Writing bits to the bus. Expecting to be called during low clock state.
        Before returning returns, brings back the clock in low state normally, unless this is the
        last bit of the operation, in which case it keeps the clock in a high state,
        st that a new start can be called.
        """
        for data_bit in bits:
            self.write_single_bit_keeping_the_clock_high(data_bit)
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

    def update_break_control_register(self, breakpoints_enabled, break_now_enabled, break_ignore_low_0_enabled,
                                      break_ignore_low_1_enabled, single_step_break_enabled):
        """
        updating the break control register on eZ80
        """
        byte = 0
        byte = (byte << 1) | break_now_enabled
        byte = (byte << 1) | breakpoints_enabled[3]
        byte = (byte << 1) | breakpoints_enabled[2]
        byte = (byte << 1) | breakpoints_enabled[1]
        byte = (byte << 1) | breakpoints_enabled[0]
        byte = (byte << 1) | break_ignore_low_1_enabled
        byte = (byte << 1) | break_ignore_low_0_enabled
        byte = (byte << 1) | single_step_break_enabled
        self.write_bytes_to_registers(self.WRITE_REGISTER_BREAK_CONTROL, [byte])

    @staticmethod
    def number_to_bin_array(num, array_length=8):
        # we only need the last 'array_length' bit
        num = num % (2 ** array_length)
        length_format = "0"+str(array_length)+"b"
        return [int(x) for x in format(num, length_format)]

    WRITE_REGISTER_BREAK_ADDRESS_0_L = 0x00
    WRITE_REGISTER_BREAK_ADDRESS_0_H = 0x01
    WRITE_REGISTER_BREAK_ADDRESS_0_U = 0x02
    WRITE_REGISTER_BREAK_ADDRESS_1_L = 0x04
    WRITE_REGISTER_BREAK_ADDRESS_1_H = 0x05
    WRITE_REGISTER_BREAK_ADDRESS_1_U = 0x06
    WRITE_REGISTER_BREAK_ADDRESS_2_L = 0x08
    WRITE_REGISTER_BREAK_ADDRESS_2_H = 0x09
    WRITE_REGISTER_BREAK_ADDRESS_2_U = 0x0A
    WRITE_REGISTER_BREAK_ADDRESS_3_L = 0x0C
    WRITE_REGISTER_BREAK_ADDRESS_3_H = 0x0D
    WRITE_REGISTER_BREAK_ADDRESS_3_U = 0x0E
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


