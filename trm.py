###########
# Modules #
###########

# hashlib: encryption/decryption module
# source: https://datagy.io/python-sha256/
import hashlib
# datetime: for timestamp and datetime
# source: https://pynative.com/python-timestamp/
from datetime import datetime
# exists: check, if file in a directory exists
# source: https://www.pythontutorial.net/python-basics/python-check-if-file-exists/
from os.path import exists
# fnc (Module for own functions): Own set of functions
import fnc
# usr (user module): Own module for login/out, session, and user handling
# from usr import User
# blm (block module): Own module for block class
# import like this due to circular import with class block
import blm
# wlm (wallet module). Own module for wallet handling
# from wlm import Wallet

#########
# Class #
#########
     
class Transaction():

    ###########
    # Dunders #
    ###########
    
    # Constructor: Instance Variables
    def __init__(self, user_path, mem_path, block_path): 
        self.user_path = user_path
        self.mem_path = mem_path
        self.block_path = block_path
        self.block_nr = None
        # Tx header
        self.tx_id = ""        
        self.timestamp = 0
        self.input_count = 0
        self.output_count = 0
        # Input list
        self.inputs = []
        # Output list
        self.outputs = []        
        # Error handling
        self.tx_valid = False
        self.error = []
        # Temporary variables for key generation
        self.private_key = ""
        self.public_key = ""
        self.address = ""       
        
    # Print Object as formatted string
    def __str__(self, version = 'long'):
        # in dex of transaction in mempool or block
        tx_str = f"> Tx {self.tx_id}\n"
        ### Header ###
        tx_str += "\tTransaction header:\n"    
        # Timestamp
        # convert timestamp to datetime and datetime to string in dd-mm-yyyy HH:MM:SS format
        if(self.timestamp != 0):
            date_time = datetime.fromtimestamp(self.timestamp)
            d = date_time.strftime("%d.%m.%y %H:%M:%S") 
            tx_str += f"\t\t{'Date/Time':11}: {d}\n"
        else:
            tx_str += f"\t\t{'Date/Time':11}: None\n" 
        # Input count
        tx_str += f"\t\t{'Inputs':11}: {self.input_count}\n"    
        # Output count
        tx_str += f"\t\t{'Outputs':11}: {self.output_count}\n"         
        ### Inputs ###
        tx_str += "\tInputs:\n"
        if(self.input_count > 0):
            for inp in self.inputs:
                tx_str += f"\t\t{'> Tx ID':11}: {inp[0]}\n" 
                tx_str += f"\t\t{'Index':11}: {inp[1]}\n"
                tx_str += f"\t\t{'Public key':11}: {inp[2]}\n"
                tx_str += f"\t\t{'Signature':11}: {inp[3]}\n"
        else:
            tx_str += "\t\tNone\n"             
        ### Outputs ###
        tx_str += "\tOutputs:\n"
        for out in self.outputs:
            tx_str += f"\t\t{'> Index':11}: {out[0]}\n" 
            tx_str += f"\t\t{'Address':11}: {out[1]}\n"
            tx_str += f"\t\t{'Volume':11}: {out[2]:5.3f}\n"
        ### Tx check
        tx_str += "\tTx check:\n"
        tx_str += f"\t\t{'Tx valid':11}: "
        if(self.tx_valid):
            tx_str += "yes\n"  
        else:
            tx_str += "NO!\n"
        if len(self.error):
            tx_str += f"\t\t{'Error':11}: "
            tx_str += ', '.join(self.error)
            tx_str += "\n"
        return tx_str
    
    ##################
    # Static methods #
    ##################
    
    # Method checks, if mempool file exists
    @staticmethod
    def check_mempool_file(mem_path):
        if not(exists(mem_path)): 
            print("Error: Mempool file not found!")
            return False  
        else: 
            return True   
        
    # Returns the number of transactions = lines in the mempool
    # Existence of mempool file needs to be checked here too, 
    # but using above function does not work in static methods
    @staticmethod
    def get_tx_count_mempool(mem_path):
        if not(exists(mem_path)): 
            print("Error: Mempool file not found!")
            return 0  
        else:
            with open(mem_path, "r") as handle:
                # remove first line = delimiter {tx:}
                handle.readline()
                # read the rest of the file as string
                mem_string = handle.read()                                 
                # Split Tx, delimiter: {tx:}
                tx_list = mem_string.split("{tx:}")  
            # If there are no transactions in the file, the result is NOT an empty list
            # Instead it's a list with an empty string
            if(tx_list == ['']):
                count = 0
            else: 
                count = len(tx_list)
            return count  
    
    # Clear mempool
    @staticmethod
    def clear_mempool(mem_path):
        with open(mem_path, 'w'):
            pass  
    
    ####################
    # Instance Methods #
    ####################
        
    # Method returns the SHA256 hash = ID of a transaction
    # Hash of all transaction data except signature and public key in inputs
    def get_tx_id(self):
        # 1. Transaction header
        header_string = f"{self.timestamp}{self.input_count}{self.output_count}"
        # print(header_string)
        # 2. Transaction Inputs
        input_string = ""
        if(self.input_count > 0):
            for inp in self.inputs:
                # inp[0]: Tx ID Output
                # inp[1]: Index Output (UTXO)
                # NOT:
                # inp[2]: Public key
                # inp[3]: Signature
                input_string += f"{inp[0]}{inp[1]}"
        # print(input_string)
        # 3. Transaction Outputs
        output_string = ""
        for out in self.outputs:
            # out[0]: Index Output
            # out[1]: Address
            # out[2]: Volume
            output_string += f"{out[0]}{out[1]}{out[2]:5.3f}" 
        # print(output_string)
        # Connect all strings
        tx_string = header_string + input_string + output_string
        # print(tx_string)
        # Get and return the double SHA256 hash of the transaction string
        hash1 = hashlib.sha256(tx_string.encode()).hexdigest()
        return hashlib.sha256(hash1.encode()).hexdigest() 

    # Method generates the string from the transaction object
    # to write a transaction to mempool or block file
    def get_tx_string(self):
        # Transaction delimiter
        tx_string = "{tx:}\n"
        # Transaction header
        tx_string += f"{self.tx_id}|{self.timestamp}|{self.input_count}|{self.output_count}\n"
        # Transaction element delimiter
        tx_string += "[x]\n"
        # Inputs -> None
        if(self.input_count > 0):
            for inp in self.inputs:
                # inp[0]: Tx ID Output
                # inp[1]: Index Output (UTXO)
                # inp[2]: Public key
                # inp[3]: Signature
                tx_string += f"{inp[0]}|{inp[1]}|{inp[2]}|{inp[3]}\n"
        # Transaction element delimiter
        tx_string += "[x]\n"
        # Outputs
        for out in self.outputs:
            # out[0]: Index Output
            # out[1]: Address
            # out[2]: Volume
            tx_string += f"{out[0]}|{out[1]}|{out[2]:5.3f}\n"
        return tx_string 

    # Method loads coinbase data into a transaction object 
    def get_coinbase_data(self, wallet, mining_reward, timestamp):
        # Make a new key pair and create the receiving address for the miner  
        if not(wallet.generate_keys()):
            return False   
        else: 
            ### 1. Transaction header ###            
            # Set timestamp = same as timestamp in block header
            self.timestamp = timestamp
            # Set input count = 0
            self.input_count = 0
            # Set output count = 1
            self.output_count = 1         
            ### 2. Transaction Inputs (= 0) ###
            # -> empty!
            self.inputs = []                       
            ### 3. Transaction outputs (= 1: Miner) ###
            # Set volume = mining reward
            self.volume = mining_reward
            # Write Coinbase Output
            self.outputs = [[0, wallet.get_address(), self.volume]]
            ### Transaction ID ###
            self.tx_id = self.get_tx_id() 
            ### Transaction valid ###
            self.tx_valid = True
    
    # Method writes a transaction string to the mempool
    def tx_to_mempool(self, tx_string):
        # Check, if mempool file exists
        if(self.check_mempool_file(self.mem_path)): 
            # open mempool in append mode
            with open(self.mem_path, "a") as handle:
                # add transaction to mempool
                handle.write(tx_string)
            print("Transaction successfully written to mempool!")
        else:
            print("Transaction failed!")  
     
    # Method takes a string with one or more transactions in transaction format 
    # from either the mempool or a block
    # Index is the index of the transactions within the block or mempool (from top to bottom 0-x)
    # from_path: 'block' or 'mempool'
    # tx_string: first {tx:} delimiter needs to be already removed
    def load_tx(self, from_path, tx_string, index, block_number = ''):  
        # Set parameters if transactions are loaded from a block or from mempool
        if(from_path == "block" and block_number != ''):
            path = "block " + str(block_number)
        elif(from_path == "mempool" and block_number == ''): 
            path = "mempool"
        else:
            print("Loading of transactions failed: Wrong function input!")
            return False                        
        # Split Tx, delimiter: {tx:}
        tx_list = tx_string.strip().split("{tx:}")  
        # Count transactions from file                              
        tx_count_file = len(tx_list) 
        # If there are no transactions in the string
        if(tx_count_file == 0):
            print("Loading of transactions failed: No transactions in {path}!")
            return False 
        else:
            # Split transaction elements (= header line, inputs, outputs), delimiter [x]
            tx_elements = tx_list[index].strip().split("[x]")   
            # Check, if tx_elements has 3 elements (= header line, inputs, outputs)
            if(len(tx_elements) != 3):
                self.error.append(f"Transaction {index} in {path} corrupted!")
                self.tx_valid = False  
                return False 
            else: 
                #############
                # Tx Header #
                #############
                # Block number
                self.block_nr = block_number
                # Split transaction header data
                tx_header = tx_elements[0].strip().split("|")
                # print(tx_header)
                # Check, if tx header has 4 elements (= ID, Timestamp, input ans output count)
                if(len(tx_header) != 4):
                    self.error.append(f"Header of transaction {index} in {path} corrupted!")
                    self.tx_valid = False  
                    return False 
                else:
                    # Check header elements
                    # 0) The SHA256 double hash of the transaction data = ID
                    if not(fnc.check_prk_hash(tx_header[0].strip())):
                        self.error.append(f"ID of transaction {index} in {path} is corrupted!")
                        self.tx_valid = False  
                    else:
                        self.tx_id = str(tx_header[0])
                        # print(tx_header[0])
                    # 1) Timestamp of transaction
                    if not(fnc.check_float(tx_header[1])):
                        self.error.append(f"Timestamp of transaction {index} in {path} is corrupted!")
                        self.tx_valid = False 
                    else:                                 
                        self.timestamp = float(tx_header[1]) 
                        # print(tx_header[1])
                    # 2) Input count
                    if not(fnc.check_int(tx_header[2])):
                        self.error.append(f"Input count of transaction {index} in {path} is corrupted!")
                        self.tx_valid = False 
                    else:                                 
                        self.input_count = int(tx_header[2])   
                        # print(tx_header[2])
                    # 3) Output count
                    if not(fnc.check_int(tx_header[3])):
                        self.error.append(f"Output count of transaction {index} in {path} is corrupted!")
                        self.tx_valid = False 
                    else:                                 
                        self.output_count = int(tx_header[3])
                        # print(tx_header[3])
                    ##########
                    # Inputs #
                    ########## 
                    # Split inputs
                    inp = tx_elements[1].strip().split("\n")
                    # If there are no inputs in the transaction AND
                    # if the transaction is NOT a coinbase (index 0), an error occures   
                    if(inp == [''] and index != 0):
                        self.error.append(f"Transaction {index} in {path} does not have inputs!")  
                        self.tx_valid = False
                        icount = 0                                                                                           
                    # Coinbase transactions
                    elif(inp == [''] and index == 0):
                        icount = 0
                    # Normal transactions (must have inputs!)
                    else:
                        icount = len(inp)                                    
                        # Check if input count in block header is the same as the actual amount of inputs
                        if(icount != self.input_count):
                            self.error.append(f"Number of Inputs in in transaction {index} header does not match the actual number of inputs!")
                            self.tx_valid = False 
                        input_index = -1
                        # Iterate through all inputs of this transaction
                        for i in inp:
                            input_index += 1
                            # Split input elements
                            inp[input_index] = i.strip().split("|")
                            # Check, if all inputs have 4 elements
                            if(len(inp[input_index]) != 4):
                                self.error.append(f"Input {input_index} of transaction {index} in {path} is corrupted!")
                                self.tx_valid = False
                            else:                                                
                                # Check all input elements
                                # 0) Transaction ID of former output (UTXO) = hash
                                if not(fnc.check_prk_hash(inp[input_index][0].strip())):
                                    self.error.append(f"ID of input {input_index} in transaction {index} in {path} is corrupted!")
                                    self.tx_valid = False  
                                # 1) Index of UTXO output
                                if not(fnc.check_int(inp[input_index][1].strip())):
                                    self.error.append(f"Output index of input {input_index} in transaction {index} in {path} is corrupted!")
                                    self.tx_valid = False                                               
                                # 2) Public key    
                                if not(fnc.check_puk_sig(inp[input_index][2].strip())):
                                    self.error.append(f"Public key of input {input_index} in transaction {index} in {path} is corrupted!")
                                    self.tx_valid = False 
                                # 3) Signature                                                  
                                if not(fnc.check_puk_sig(inp[input_index][3].strip())):
                                    self.error.append(f"Signature of input {input_index} in transaction {index} in {path} is corrupted!")
                                    self.tx_valid = False 
                                # create intput list                                
                                self.inputs.append([str(inp[input_index][0].strip()), int(inp[input_index][1].strip()), str(inp[input_index][2].strip()), str(inp[input_index][3].strip())])                                                   
                    ###########
                    # Outputs #
                    ########### 
                    # Split outputs
                    out = tx_elements[2].strip().split("\n")
                    # print(out)
                    # Check for outputs: every transaction has to have outputs! 
                    if(out == ['']):
                        self.error.append(f"Transaction {index} in {path} does not have outputs!")  
                        self.tx_valid = False
                        ocount = 0                                                                                           
                    else:
                        ocount = len(out)
                        # print(ocount)
                        # Check if input count in block header is the same as the actual amount of inputs
                        if(ocount != self.output_count):
                            self.error.append(f"Number of Outputs in in transaction {index} header does not match the actual number of outputs!")
                            self.tx_valid = False 
                        output_index = -1
                        # Iterate through all outputs of this transaction
                        for o in out:
                            # print(o)
                            output_index += 1
                            # Split output elements
                            out[output_index] = o.strip().split("|")
                            # print(out[output_index])
                            # Check, if all oututs have 3 elements
                            if(len(out[output_index]) != 3):
                                self.error.append(f"Output {output_index} of transaction {index} in {path} is corrupted!")
                                self.tx_valid = False     
                            else:
                                # Check all output elements    
                                # 0) UTXO = Output index
                                if not(fnc.check_int(out[output_index][0].strip())):
                                    self.error.append(f"Output index of output {input_index} in transaction {index} in {path} is corrupted!")
                                    self.tx_valid = False   
                                # 1) Address
                                if not(fnc.check_address(out[output_index][1].strip())):
                                    self.error.append(f"Address of output {output_index} in transaction {index} in {path} is corrupted!")
                                    self.tx_valid = False 
                                # 2) Volume
                                if not(fnc.check_float(out[output_index][2].strip())):                                                   
                                    self.error.append(f"Volume of output {output_index} in transaction {index} in {path} is corrupted!")
                                    self.tx_valid = False 
                                # create output list                                
                                self.outputs.append([int(out[output_index][0].strip()), str(out[output_index][1].strip()), float(out[output_index][2].strip())])  

    # Method to load a transaction from mempool into an transaction object
    # Index is the index of the transactions within the file (from top to bottom 0-x)
    def load_tx_from_mempool(self, index):
        # Check, if mempool contains transactions
        tx_count_mem = self.get_tx_count_mempool(self.mem_path)
        if(tx_count_mem == False):
            return False 
        elif(tx_count_mem == 0):
            print("No transactions in mempool")
            return False 
        else:
            # Check index (in this case the position of the transaction within mempool)
            if(index < 0 or index > tx_count_mem  - 1):
                print(f"Index {index} out of range (0 - {tx_count_mem - 1})!")
                return False 
            else:              
                # Open mempool file and read lines
                with open(self.mem_path, "r") as handle:
                    # remove first line (first tx delimiter)
                    handle.readline()
                    # read the rest of the file string
                    tx_string = handle.read()
                    # Load transaction into an object
                    self.load_tx("mempool", tx_string, index) 
                    # If there are no error messages, the transaction is valid in terms of a correct format
                    if not(len(self.error)):                              
                        self.tx_valid = True
                        return True
                    ### Check also if transaction has no inputs!!!
                    ### Coinbase transactions are never found in mempool ###############
        
    # Method to load a transaction from a block file into an transaction object
    # Index is the index of the transactions within the block (from top to bottom 0-x)
    def load_tx_from_block(self, block_number, index):
         # Check, if Block file exists
         if not(blm.Block.check_block_file(self.block_path, block_number)):
             # Set transaction as invalid and write error message
             self.error.append(f"Block file for block {block_number} not found!")
             self.tx_valid = False  
             return False
         else:
             # Open block file for reading
             with open(f"{self.block_path}/{block_number}.bl", "r") as handle:
                 # Get header line = first line of a block file
                 bl_header_line = handle.readline()  
                 # remove second line (first tx delimiter)
                 handle.readline()
                 # read the rest of the file string
                 tx_string = handle.read()                                    
             ### Block header ### 
             # Split header elements                             
             bl_header = bl_header_line.strip().split("|")   
             # print(bl_header)               
             # if header list does not contain 7 elements
             if(len(bl_header) != 7):
                 # Set transaction as invalid and write error message
                 self.error.append(f"Header of block {block_number} corrupted!")
                 self.tx_valid = False                
                 return False  
             else:
                 # Get the number of transactions from the block header 
                 # and check if it is an integer number
                 if not(fnc.check_int(bl_header[3].strip())):
                     # Set transaction as invalid and write error message
                     self.error.append(f"Number of transactions in header of block {block_number} corrupted!")
                     self.tx_valid = False 
                     return False
                 else:
                    tx_count_header = int(bl_header[3].strip())
                    # print(tx_count_header)
                    # Split transactions, delimiter: {tx:}
                    tx_list = tx_string.strip().split("{tx:}") 
                    # Get the number of transactions from the block file
                    tx_count_file = len(tx_list)  
                    # If there are no transactions in the string
                    if(tx_count_file == 0):
                        print("Loading of transactions failed: No transactions in block {block_number}!")
                        self.tx_valid = False 
                        return False 
                    else:                
                        # If they are not the same
                        if(tx_count_header != tx_count_file):
                            # Set transaction as invalid and write error message
                            self.error.append(f"Transaction count in block {block_number} header ({tx_count_header}) does not match the number of transactions in the block {block_number} file ({tx_count_file})!")          
                            self.tx_valid = False    
                            return False
                        else:
                            # Check index (in this case the position of the transaction within the block file)
                            if(index < 0 or index > tx_count_header - 1):
                                # Set transaction as invalid and write error message
                                self.error.append(f"Index {index} out of range (0 - {tx_count_header - 1})!")
                                self.tx_valid = False  
                                return False 
                            else:      
                               # Load transaction into an object
                               self.load_tx("block", tx_string, index, block_number)  
                               # If there are no error messages, the transaction is valid in terms of a correct format
                               if not(len(self.error)):                              
                                   self.tx_valid = True
                                   return True




































        
        
        
        
            
