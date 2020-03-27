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

        # IS to hold value of interrupt status
        self.IS = 0
        # IM to hold value of interrupt mask
        self.IM = 0

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
            0b00000001: self.halt,
            # LDI
            0b10000010: self.ldi,
            # PRN
            0b01000111: self.prn,
            # PRA
            0b01001000: self.pra,
            # ADD 
            0b10100000: self.add,
            # MUL
            0b10100010: self.mul,
            # PUSH
            0b01000101: self.push,
            # POP
            0b01000110: self.pop,
            # ST
            0b10000100: self.st,
            # CMP
            0b10100111: self.compare,
            # AND
            0b10101000: self.bit_and,
            # OR
            0b10101010: self.bit_or,
            # XOR
            0b10101011: self.bit_xor,
            # NOT
            0b01101001: self.bit_not,
            # SHL
            0b10101100 : self.bit_shl,
            # SHR
            0b10101101: self.bit_shr,
            # MOD
            0b10100100: self.mod,

            # PC MUTATORS:
            # CALL
            0b01010000: self.call,
            # RET
            0b00010001: self.ret,
            # JMP
            0b01010100: self.jump,
            # JEQ
            0b01010101: self.jeq,
            # JNE
            0b01010110: self.jne,
            # JGE
            0b01011010: self.jge,
            # JGT
            0b01010111: self.jgt,
            # JLE
            0b01011001: self.jle,
            # JLT
            0b01011000: self.jlt
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

        elif op == "BIT-AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

        elif op == "BIT-OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

        elif op == "BIT-XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]    

        elif op == "BIT-NOT":
            self.reg[reg_a] = ~self.reg[reg_a]   

        elif op == "BIT-SHL":
            num_bits = self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] << num_bits   

        elif op == "BIT-SHR":
            num_bits = self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] >> num_bits
        elif op == "MOD":
            if self.reg[reg_a] != 0:
                self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
            else:
                self.halt()    
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

    def bit_and(self):
        self.alu("BIT-AND", self.operand_a, self.operand_b)

    def bit_or(self):
        self.alu("BIT-OR", self.operand_a, self.operand_b)

    def bit_xor(self):
        self.alu("BIT-XOR", self.operand_a, self.operand_b)    

    def bit_not(self):
        self.alu("BIT-NOT", self.operand_a)

    def bit_shl(self):
        # Shift the value in registerA left by the number of bits specified in registerB, filling the low bits with 0.
        self.alu("BIT-SHL", self.operand_a, self.operand_b)

    def bit_shr(self):
        # Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0.
        self.alu("BIT-SHR", self.operand_a, self.operand_b)    
    
    def mod(self):
        # Divide the value in the first register by the value in the second,
        # storing the _remainder_ of the result in registerA.
        self.alu("MOD", self.operand_a, self.operand_b)   
    
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
        # If `equal` flag is set true, jump to the address stored in the given register.
        # the equal falg is the last character in the 8-bit val of flag ->
        # convert flag to string and check if last character is 1...
        if f'{self.FL:08b}'[-1] == '1':
            # if so jump
            self.jump()
        # else continue program    
        else:
            self.pc += 2    

    def jne(self):
        # If `equal` flag is clear, jump to the address stored in the given register.
        # the equal falg is the last character in the 8-bit val of flag ->
        # convert flag to string and check if last character is 0... 
        if f'{self.FL:08b}'[-1] == '0':
            # if so jump
            self.jump()
        # else continue program    
        else:
            self.pc += 2          

    def jge(self):
        # If `greater-than` flag or `equal` flag is set (true), jump to the address stored in the given register.
        # get 8-bit string of flag
        flag_str = f'{self.FL:08b}'
        # the greater-than flag will be the second last value of the flag_str and the equal flag will be the last value of the flag_str ->
        # check if last or second-last character in flag_str is 1...
        if flag_str[-2] or flag_str[-1] == '1':
            # if so, jump
            self.jump()
        # else continue program    
        else:
            self.pc += 2 

    def jgt(self):
        # If `greater-than` flag is set (true), jump to the address stored in the given register.
        # get 8-bit string of flag
        flag_str = f'{self.FL:08b}'
        # the greater-than flag will be the second last value of the flag_str
        # check if second-last character in flag_str is 1...
        if flag_str[-2] == '1':
            # if so, jump
            self.jump()
        # else continue program    
        else:
            self.pc += 2    

    def jle(self):
        # If `less-than` flag or `equal` flag is set (true), jump to the address stored in the given register.
        # get 8-bit string of flag
        flag_str = f'{self.FL:08b}'
        # the less-than flag will be the third last value of the flag_str and the equal flag will be the last value of the flag_str ->
        # check if last or third-last character in flag_str is 1...
        if flag_str[-3] or flag_str[-1] == '1':
            # if so, jump
            self.jump()
        # else continue program    
        else:
            self.pc += 2   

    def jlt(self):
        # If `less-than` flag is set (true), jump to the address stored in the given register.
        # get 8-bit string of flag
        flag_str = f'{self.FL:08b}'
        # the less-than flag will be the second last value of the flag_str
        # check if second-last character in flag_str is 1...
        if flag_str[-3] == '1':
            # if so, jump
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
            self.branchtable[IR]()   

            # if the program counter needs to be altered..
            # use bitwise AND and bitshift result to the right by 4 bits, if not equal to 1 ...
            if (IR & 0b00010000) >> 4 != 0b00000001:
                # increment by the value of the first two digits in IR + 1
                self.pc += (IR >> 6) + 0b00000001