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

        # add flag initialized to 0
        self.FL = 0b00000000

        # boolean to track whether CPU is running or not, initialize to True
        self.running = True

        # variables that will be used to hold the bytes at PC+1 and PC+2 in RAM while cpu is running
        self.operand_a = None
        self.operand_b = None

        # add branchtable to link binary values of instructions with functions to execute while cpu running 
        # and whether/not the program counter will need to be altered after the function is executed
        self.branchtable = {
            # HLT
            0b00000001: {"function" : self.halt, "increment": False},
            # LDI
            0b10000010: {"function" : self.ldi, "increment": True},
            # PRN
            0b01000111: {"function" : self.prn, "increment": True},
            # PRA
            0b01001000 : {"function" : self.pra, "increment": True},
            # ADD 
            0b10100000: {"function" : self.add, "increment": True},
            # MUL
            0b10100010: {"function" : self.mul, "increment": True},
            # PUSH
            0b01000101: {"function" : self.push, "increment": True},
            # POP
            0b01000110: {"function" : self.pop, "increment": True},
            # CALL
            0b01010000: {"function" : self.call, "increment": False},
            # RET
            0b00010001: {"function" : self.ret, "increment": False},
            # JMP
            0b01010100: {"function" : self.jump, "increment": False},
            # ST
            0b10000100: {"function" : self.st, "increment": True},
            # CMP
            0b10100111: {"function" : self.compare, "increment": True},
            # JEQ
            0b01010101: {"function" : self.jeq, "increment": False}
        }

    def ram_read(self, MAR):
        # accepts MAR as the address to read (Memory Address Register) and returns the value stored there
        return self.ram[MAR]

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

        elif op == "CMP":
            # determine whether value in register a is less than val in register b, convert to 1 if true 0 if false
            L = int(self.reg[reg_a] < self.reg[self.operand_b])
            # determine whether value in register a is greater than val in register b, convert to 1 if true 0 if false
            G = int(self.reg[reg_a] > self.reg[self.operand_b])
            # determine whether value in register a is equal to val in register b, convert to 1 if true 0 if false
            E = int(self.reg[reg_a] == self.reg[self.operand_b])
            # generate string of the binary value that the flag should have
            flag_string = f'0b00000{L}{G}{E}'
            # convert string to integer base 2 and set the flag equal to it
            self.FL = int(flag_string, 2)

            # print(f'{self.FL:08b}')
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

    def pra(self):
        # print ASCII value of register at index of operand_a
        print(chr(self.reg[self.operand_a]))

    def mul(self):
        # pass operand_a and operand_b in alu method with "MUL" as the opcode
        self.alu("MUL", self.operand_a, self.operand_b)

    def add(self):
        # pass operand_a and operand_b in alu method with "MUL" as the opcode
        self.alu("ADD", self.operand_a, self.operand_b)

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

    def call(self):
        # push current value of pc + 2 to stack, 
        # this will be the value that the program counter should be after executing subroutine
        self.reg[7] -= 0x1
        self.sp = self.reg[7]
        self.ram_write(self.sp, (self.pc + 2))        
        # set the pc equal to the value in register at index of operand_a 
        self.pc = (self.reg[self.operand_a]) 

    def ret(self):
        # grab the value from top of stack
        self.sp = self.reg[7]
        val = self.ram_read(self.sp)
        # set the program counter equal to the value 
        self.pc = val 
        # increment sp
        self.reg[7] += 0x1

    def jump(self):
        # set the value of pc equal to the value of register at index of operand_a minus 2 (run function will add 2 when function finished executing)
        self.pc = (self.reg[self.operand_a])    

    def st(self):
        # Store value in registerB in the address stored in registerA.
        # set val equal to the value stored in register at index of operand b
        val = self.reg[self.operand_b]
        # set address equal to the value stored in register at index of operand a
        address = self.reg[self.operand_a]
        # set value in ram at adrress equal to value
        self.ram_write(address, val)

    def compare(self):
        """        
        Compare the values in two registers.
            - If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.
            - If registerA is less than registerB, set the Less-than `L` flag to 1,
              otherwise set it to 0.
            - If registerA is greater than registerB, set the Greater-than `G` flag
              to 1, otherwise set it to 0. 
        """
        # pass operand_a and operand_b to compare function in alu
        self.alu("CMP", self.operand_a, self.operand_b)   

    def jeq(self):
        # If `equal` flag is set (true), jump to the address stored in the given register.
        if self.FL[-3] == 1:
            self.jump()
        # else continue program    
        else:
            self.pc += 2    

    def run(self):
        """Run the CPU."""
        while self.running:
            # read the memory address that’s stored in ram at index of PC, and store that result in IR (Instruction Register)
            IR = self.ram_read(self.pc)

            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            # execute the function within the branchtable at the index of IR
            self.branchtable[IR]["function"]()   

            # if the program counter needs to be altered..
            if self.branchtable[IR]["increment"] is True:
                # increment by the value of the first two digits in IR + 1
                self.pc += (IR >> 6) + 0b00000001