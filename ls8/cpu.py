"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        
        # add ram to hold 256 bytes of memory
        self.ram = [0] * 256

        # add reg to hold 8 general-purpose registers
        self.reg = [0] * 8

        # add pc to hold value of the program counter, initialize to 0
        self.pc = 0

        # add dictionary to hold commands and their values in binary to make run function more readable
        self.instructions = {
            "HLT": 0b00000001,
            "LDI": 0b10000010,
            "PRN": 0b01000111
        }


    def ram_read(self, MAR):
        """should accept the address to read and return the value stored there."""
        # MAR : Memory Address Register - contains the address that's being read
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        """ should accept a value to write, and the address to write it to"""
        # MAR : Memory Address Register - contains the address that's being read
        # MDR : Memory Data Register - contains the data to write
        self.ram[MAR] = MDR   

    def load(self):
        """Load a program into memory."""

        address = 0
        # set executable file equal to the last argument in sys.argv
        executable = sys.argv[-1]
        # open executable and save to 'file' variable            
        with open(executable, "r") as file:
            # loop over every line in the file
            for line in file:
                # if the first character of the line == '0' or '1'...
                if line[0] == '0' or line[0] == '1':
                    # split the line at '#' character to remove comments so that we can just grab the value at the zeroth index of the split line
                    num = line.split('#')[0]
                    # convert to a base-2 int
                    instruction = int(num, 2)
                    # set the value of ram at index of current value of address = instruction
                    self.ram[address] = instruction
                    # increment the value of address by 1
                    address += 1         
            

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # initalise loop to run while 'running' boolean True
        running = True
        while running:
            # read the memory address that’s stored in ram at index of PC, and store that result in IR (Instruction Register)
            IR = self.ram_read(self.pc)
            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a 
            # and operand_b in case the instruction needs them
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # if IR = binary value of HLT command...
            if IR == self.instructions["HLT"]:
                # set running to False to exit loop and stop CPU running
                running = False

            # else if IR = binary value of LDI command...
            elif IR == self.instructions["LDI"]:
                # set register at index of operand_a equal to the value of operand_b
                self.reg[operand_a] = operand_b
                # increment program counter by 3
                self.pc += 3

            # else if IR = binary value of PRN command...
            elif IR == self.instructions["PRN"]:
                # print value of register at index of operand_a
                print(self.reg[operand_a])
                # increment program counter by 2
                self.pc += 2    
