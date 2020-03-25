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

        # set R7 equal to 0xf4 (this will be initial value of sp)            
        self.reg[7] = 0xf4  

        # add pc to hold value of the program counter, initialize to 0
        self.pc = 0

        # add stack pointer internal register, initialize to 0
        self.sp = 0

        # boolean to track whether CPU is running or not, initialize to True
        self.running = True

        # variables that will be used to hold the bytes at PC+1 and PC+2 in RAM while cpu is running
        self.operand_a = None
        self.operand_b = None

        # add dictionary to hold commands and their values in binary 
        self.instructions = {
            0b00000001: "HLT",
            0b10000010: "LDI",
            0b01000111: "PRN",
            0b10100010: "MUL",
            0b01000101: "PUSH",
            0b01000110: "POP",
            0b00000101: "PRINT_REG"
        }

        # add branchtable to link commands with functions to execute while cpu running
        self.branchtable = {
            "HLT": self.halt,
            "LDI": self.ldi,
            "PRN": self.prn,
            "MUL": self.mul,
            "PUSH": self.push,
            "POP": self.pop,
            "PRINT_REG": self.print_reg
        }

    def ram_read(self, MAR):
        # accepts MAR as the address to read (Memory Address Register) and returns the value stored there
        return self.ram[MAR]

    def print_reg(self):
        print(self.reg)

    def ram_write(self, MAR, MDR):
        # accepts MAR (Memory Address Register) as the address to write to and sets its value to MDR (Memory Data Register)
        self.ram[MAR] = MDR     

    def load(self):
        """Load a program into memory."""
        address = 0
        # try to open file passed in command line
        try:
            # Print error and usage statement if length of argv != 2 (no file has been provided to extract instructions to process in the CPU)
            if len(sys.argv) != 2:
                print("Invalid number of arguments. Usage: python ls8.py examples/<filename>")
                sys.exit(1)
            # set executable file equal to the last argument in sys.argv
            executable = sys.argv[1]
            # open executable and save to 'file' variable            
            with open(executable, "r") as file:
                # loop over every line in the file
                for line in file:
                    # if the first character of the line == '0' or '1'...
                    if line[0] == '0' or line[0] == '1':
                        # split the line at '#' character to remove comments so that we can just grab the value at the zeroth index of the split line
                        num = line.split('#')[0].strip()
                        # convert to a base-2 int
                        instruction = int(num, 2)
                        # set the value of ram at index of current value of address = instruction
                        self.ram[address] = instruction
                        # increment the value of address by 1
                        address += 1                   
        # if this fails and the user has entered the name of a file that doesn't exist (a FileNotFoundError is thrown)..
        except FileNotFoundError:
            # print error message and usage statement
            print("File not found. Usage: python ls8.py examples/<filename>") 
            # exit
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        # set the value of register at index of reg_a equal to the value of reg_a * reg_b    
        elif op == "MUL": 
            self.reg[reg_a] *= self.reg[reg_b]
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

    def halt(self): 
        # set running to False to exit loop and stop CPU running
        self.running = False

    def ldi(self):
        # set register at index of operand_a equal to the value of operand_b
        self.reg[self.operand_a] = self.operand_b

    def prn(self):
        # print value of register at index of operand_a
        print(self.reg[self.operand_a])

    def mul(self):
        # pass operand_a and operand_b in alu method with "MUL" as the opcode
        self.alu("MUL", self.operand_a, self.operand_b)

    def push(self):
        # decrement value of register at index 7
        self.reg[7] -= 0x1
        # set the sp equal to the value at register 7
        self.sp = self.reg[7]
        # set value in ram at index of stack pointer equal to the value stored in register at index of program counter + 1 (operand_a)
        self.ram_write(self.sp, self.reg[self.operand_a])

    def pop(self):
        # set the sp equal to the value at register 7
        self.sp = self.reg[7]
        # read value in ram at index of sp into variable
        val = self.ram_read(self.sp)
        # set value of register at index of operand_a equal to value
        self.reg[self.operand_a] = val
        # increment value of register at index 7
        self.reg[7] += 0x1

    def run(self):
        """Run the CPU."""
        while self.running:
            # read the memory address that’s stored in ram at index of PC, and store that result in IR (Instruction Register)
            IR = self.ram_read(self.pc)

            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            # execute the function within the brachtable at the index of the command within the instruction table at the index of IR
            self.branchtable[self.instructions[IR]]()   

            # increment program counter by the value of the first two digits in IR + 1
            self.pc += (IR >> 6) + 0b00000001