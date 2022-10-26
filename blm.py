###########
# Modules #
###########

# datetime: for timestamp and datetime
# source: https://pynative.com/python-timestamp/
from datetime import datetime
# os: "The os module provides many functions for interacting with the operating system. 
# Using the os module, we can perform many file-related operations such as moving, copying, renaming, and deleting files"
# source: https://pynative.com/python-count-number-of-files-in-a-directory/
import os
# exists: check, if file in a directory exists
# source: https://www.pythontutorial.net/python-basics/python-check-if-file-exists/
from os.path import exists
# hashlib: encryption/decryption module
# For this project the SHA-256 encryprion function is needed (also used for Bitcoin)
# It converts a series of bits/bytes (e.g. a text) in a 256 bit long binary number, which is called the hash
# Normally this hash is displayed as a hexadecimal number with 64 digits (4 bits per digit or two digits per byte)
# The hash has the following features:
# 1) It is one way. A hash can be created from e.g. a string, but its not possible to recreate the string from the hash
# 2) Every string leads to a unique hash (-> cannot be proofen!) and the same string always gives the same hash
# 3) Small changes in the string lead to a completely different hash
# This way the string can't be recreated from the hash by repeatetly changing one letter for example
# source: https://datagy.io/python-sha256/
import hashlib
# fnc (Module for own functions): Own set of functions
import fnc
# trm (transaction module). Own module for handeling transactions
# import like this due to circular import with class transaction
import trm

#########
# Class #
#########
       
class Block():
   
    ###########
    # Dunders #
    ###########
    
    # Constructor: Instance Variables
    # Creates an empty block object
    def __init__(self, block_path, user_path, mem_path):
        self.block_path = str(block_path)
        self.user_path = str(user_path)
        self.mem_path = str(mem_path)
        self.number = None
        self.timestamp = 0
        # Transaction hash in the block header
        self.tx_hash = ""
        self.tx_count = 0
        self.difficulty = 0
        self.nonce = 0
        # Hash of the previous block header
        self.prev_hash = ""
        # Hash of the current block header
        # Should be identical to the hash in the previous block header
        self.block_hash = ""
        # Hash of the next block header
        self.next_hash = ""
        # Error handling
        self.block_valid = False
        self.error = []
        # List of all transactions in the block
        self.tx = []
                        
    # Print Object as formatted string
    def __str__(self, version = 'long'):
        # Header data
        # 0: Block number
        # 1: Timestamp of block creation
        # 2: Hash of previous block header
        # 3: Number of transactions in block
        # 4: Hash of all transaction hashes in the block
        # 5: Mining difficulty
        # 6: Nonce
        bl_str = "\n::: BLOCK " + str(self.number) + " :::\n"
        bl_str += "HEADER:\n"
        # convert timestamp to datetime and datetime to string in dd-mm-yyyy HH:MM:SS format
        if(self.timestamp != 0):
            date_time = datetime.fromtimestamp(self.timestamp)
            d = date_time.strftime("%d.%m.%y %H:%M:%S") 
            bl_str += f"\t{'Date/Time':11}: {d}\n"
        else:
            bl_str += f"\t{'Date/Time':11}: None\n"  
        bl_str += f"\t{'Prev hash':11}: {self.prev_hash}\n"
        bl_str += f"\t{'Tx count':11}: {self.tx_count}\n"
        bl_str += f"\t{'Tx hash':11}: {self.tx_hash}\n"
        bl_str += f"\t{'Difficulty':11}: {self.difficulty}\n"
        bl_str += f"\t{'Nonce':11}: {self.nonce}\n"
        # Short and long version                         
        bl_str += f"\t{'Block valid':11}: "
        if(self.block_valid):
            bl_str += "yes\n"  
        else:
            bl_str += "NO!\n"
        if len(self.error):
            bl_str += f"\t{'Error':11}: "
            bl_str += ', '.join(self.error)
            bl_str += "\n"       
        # Transactions
        bl_str += "TRANSACTIONS:\n"        
        for t in self.tx:
            bl_str += t.__str__('long')
            # bl_str += t.__str__('short')
        return bl_str
   
    ##################
    # Static methods #
    ##################
    # = Block related functions that do not require an Block object
    
    # Returns the number of the highest block in the block folder
    # Blocks start with 0! The name of the files are [block_nr].bl
    # If there is no block yet the function will return -1
    # If the block is not present in the folder, return -2
    # Highest block is determined by the amount of files in the block folder
    # In addition it will be checked if there is a file with this name 
    @staticmethod
    def get_max_block(block_path):
        # Iterate block directory
        block_count = 0
        for path in os.listdir(block_path):
            # Check if current path is a file
            if(os.path.isfile(os.path.join(block_path, path))):
                block_count += 1
        # If there is any (block) file in the folder
        if(block_count > 0):
            max_block = block_count - 1           
            # Check here if the filename (the block number in the block header and maybe the latest timestamp) is correct
            block_exists = exists(block_path + '/' + str(max_block) + '.bl')
            if(block_exists):                
                return max_block
            else:
                # If the block is not present in the folder, return -2
                return -2
        # If there is no (block) file in the folder at all, return -1
        else:
            return -1  
        
    # Previous hash for the header of Block 0 (genesis block)
    # For creation of the genesis block, the hash of some random string needs to be generated
    # As there is no pervious block
    # SHA-256 Hash in hexadecimal format as string
    @staticmethod
    def get_genesis_hash():
        genesis_string = "Bitcoin: A Peer-to-Peer Electronic Cash System"
        return hashlib.sha256(genesis_string.encode()).hexdigest()   
        
    # Returns the hash of the block header = line 1 of each block file
    # Without the line break at the end!
    # SHA-256 Hash in hexadecimal format as string
    @staticmethod
    def get_block_header_hash(block_nr, block_path): 
        with open(f"{block_path}/{block_nr}.bl", "r") as handle:
            # Read first line of block and remove line break at the end of the line
            header_line = handle.readline().strip()     
        header_list = header_line.split("|")
        # If header missing entries
        if(len(header_list) != 7):
            print(f"Error: Block header in block {block_nr} corrupted!")
            return False
        else:
            # Create a string with each element of the header without whitespaces and line breaks
            header_string = ""
            ### 0: Block number ###
            header_string += header_list[0].strip()              
            ### 1: Timestamp of start mining of the block ### 
            header_string += header_list[1].strip()
            ### 2: Hash of the previous block ### 
            header_string += header_list[2].strip() 
            ### 3: Number of transactions in block ###
            header_string += header_list[3].strip()           
            ### 4: Hash of transactions in the block ###                
            header_string += header_list[4].strip() 
            ### 5: Mining difficulty ### 
            header_string += header_list[5].strip()           
            ### 6: Nonce ### 
            header_string += header_list[6].strip()
            # Return hash                         
            return hashlib.sha256(header_string.encode()).hexdigest()
    
    # Method checks, if the block file for a given block number is existent
    @staticmethod
    def check_block_file(block_path, block_number):
        if not(exists(f"{block_path}/{block_number}.bl")):  
            return False  
        else: 
            return True                          
           
    ####################
    # Instance Methods #
    ####################
    
    # Method loads a block from the block file into an block object
    # Validates right formats
    def load_block(self, block_number):
        # Check, if Block file exists
        if not(self.check_block_file(self.block_path, block_number)):
            # Set block as invalid and write error message
            self.error.append(f"Block file for block {block_number} not found!")
            self.block_valid = False 
            return False
        else:
            # Set block number
            self.number = block_number
            # Open block file for reading and get the header line = first line in block
            with open(f"{self.block_path}/{self.number}.bl", "r") as handle: 
                # Read first line of block, remove line break at the end and create a list from it
                header_line = handle.readline().strip()
            # Split header line into list
            header_list = header_line.split("|")
            # Check, if the resulting list has exactly 7 elements
            # 0: Block number
            # 1: Timestamp of block creation
            # 2: Hash of previous block header
            # 3: Number of transactions in block
            # 4: Hash of all transaction hashes in the block
            # 5: Mining difficulty
            # 6: Nonce
            if(len(header_list) != 7):
                # Set block as invalid and error message
                self.error.append(f"Corrupted header in block {self.number}! Number of elements in header is wrong")
                self.block_valid = False
                return False
            else:
                # 0: Block number
                if not(fnc.check_int(header_list[0])):
                    self.error.append(f"Block number in block {self.number} header is corrupted!")
                    self.block_valid = False 
                    return False
                else:
                    # Check, if block number in header is the same as the file name                
                    if(int(header_list[0]) != self.number):
                        # Set block as invalid and error message
                        self.error.append(f"Contradictory block number in block {self.number}!")
                        self.block_valid = False 
                        return False
                    else:
                        # Load block header data into instance variables
                        # 1: Timestamp of block creation
                        if not(fnc.check_float(header_list[1])):
                            self.error.append(f"Timestamp in block {self.number} header is corrupted!")
                            self.block_valid = False 
                        else:
                            self.timestamp = float(header_list[1])
                        # 2: Hash of previous block header
                        if not(fnc.check_prk_hash(header_list[2])):
                            self.error.append(f"Previous hash in block {self.number} header is corrupted!")
                            self.block_valid = False 
                        else:
                            self.prev_hash = header_list[2]
                        # 3: Number of transactions in block   
                        if not(fnc.check_int(header_list[3])):
                            self.error.append(f"Transaction count in block {self.number} header is corrupted!")
                            self.block_valid = False 
                        else:
                            self.tx_count = int(header_list[3])
                        # 4: Hash of all transaction hashes in the block                                
                        if not(fnc.check_prk_hash(header_list[4])):
                            self.error.append(f"Transaction hash in block {self.number} header is corrupted!")
                            self.block_valid = False 
                        else:
                            self.tx_hash = header_list[4]  
                        # 5: Mining difficulty                                    
                        if not(fnc.check_int(header_list[5])):
                            self.error.append(f"Mining difficulty in block {self.number} header is corrupted!")
                            self.block_valid = False 
                        else:
                            self.difficulty = int(header_list[5])
                        # 6: Nonce                                        
                        if not(fnc.check_int(header_list[6])):
                            self.error.append(f"Nonce in block {self.number} header is corrupted!")
                            self.block_valid = False 
                        else:
                            self.nonce = int(header_list[6])  
                            # Check if the block hash is the same as the previous hash in the next block header
                            # In case there is no next block the method returns an empty string
                            self.block_hash = self.get_block_header_hash(self.number, self.block_path)
                            self.next_hash = self.get_next_header_hash()
                            # If next hash cannot be read from file
                            if(self.next_hash == False):
                                # Set block as invalid and error message
                                self.error.append(f"Missing block {self.number + 1} or corrupted header!")                            
                                self.block_valid = False
                                return False
                            else:
                                # If the hash of the block doesn't matche the hash in the header of the next block
                                # If there is no next block or no block at all, the function returns an empty string
                                if(self.next_hash != "" and self.block_hash != self.next_hash):
                                    # Set block as invalid and error message
                                    self.error.append(f"Hash of block {self.number} does not match the hash in header of block {self.number + 1}!")
                                    self.block_valid = False  
                                else:   
                                    # Load transactions of the block as transaction objects
                                    for i in range(self.tx_count):
                                        # Create a transaction object 
                                        self.tx.append(trm.Transaction(self.user_path, self.mem_path, self.block_path))
                                        # If loading of transaction object is not possible or if it causes errors
                                        if not(self.tx[i].load_tx_from_block(self.number, i) or len(self.tx[i].error) == 0):
                                            # If transaction cannot be loaded, set block as invalid and error message
                                            self.error.append(f"Transaction {i} in block {self.number} is corrupted!")
                                            self.block_valid = False
        # If there are no error messages, the block is valid in terms of a correct format
        if not(len(self.error)):                              
            self.block_valid = True
            return True
    
    # Method returns the hash of the block header written in the next block
    # If there is no next block the method returns an empty string
    # Returns False if the block header is corrupted
    def get_next_header_hash(self):
        # Next block number
        next_number = self.number + 1  
        # Highest block number
        max_block = self.get_max_block(self.block_path)
        # If there is no file in the block folder at all
        if(max_block == -1):
            return ""
        else:            
            # Check, if the block file of the next block exists            
            if not(self.check_block_file(self.block_path, next_number)):
                # Not a problem for the last block
                if(next_number == max_block + 1):
                    return ""
                else:
                    return False
            else:
                # Read the hash from the header of the next block
                with open(f"{self.block_path}/{next_number}.bl", "r") as handle:
                    header = handle.readline().strip()
                header_list = header.split("|")
                # Check, if the header has exactly 7 elements
                if(len(header_list) != 7):
                    return False                
                else:   
                    # Check, if the hash has 64 characters                  
                    if not(fnc.check_prk_hash(header_list[2].strip())):
                        return False
                    else:
                        return header_list[2]
                                    
    # Method returns the hash value of all transactions hashes in a block
    # Data from blockchain object and not from text files
    # = SHA256 hash of all transaction IDs
    def get_tx_hash_block(self): 
        # Generate an empty string for all hashes
        string = ""
        # Iterate through all transactions in the block
        for tx in self.tx:
            string += str(tx.tx_id)
        # Return the hash string (hex) of the all transactions
        return hashlib.sha256(string.encode()).hexdigest()   

    # Method calculates and returns the hash of a block header
    # Data from blockchain object and not from text files
    def get_header_hash(self): 
        header_string = f"{self.number}{self.timestamp}{self.prev_hash}{self.tx_count}{self.tx_hash}{self.difficulty}{self.nonce}" 
        # Return hash                         
        return hashlib.sha256(header_string.encode()).hexdigest()  

    # Method returns the string of a block for writing it to a block file
    def get_block_string(self):
        block_string = ""
        # Block header
        block_string += f"{self.number}|{self.timestamp}|{self.prev_hash}|{self.tx_count}|{self.tx_hash}|{self.difficulty}|{self.nonce}\n"
        # Transactions
        for tx in self.tx:
            block_string += tx.get_tx_string()
        return block_string
        
    # Method writes an entire block object as block string to a block file
    def write_block_to_file(self):
        # Get String of the entire block data
        block_string = self.get_block_string()
        with open(f"{self.block_path}/{self.number}.bl", "w+") as handle:
            handle.write(block_string)        

    # Method clears a block object
    def clear_block(self):
        # No clearing of block_path and user_path
        self.number = None
        self.timestamp = 0
        # Transaction hash in the block header
        self.tx_hash = ""
        self.tx_count = 0
        self.difficulty = 0
        self.nonce = 0
        # Hash of the previous block header
        self.prev_hash = ""
        # Hash of the current block header
        # Should be identical to the hash in the previous block header
        self.block_hash = ""
        # Hash of the next block header
        self.next_hash = ""
        # Error handling
        self.block_valid = False
        self.error = []
        # List of all transactions in the block
        self.tx = []





























                 
                        
                        
                        
                        
                        
                        
                        
                    

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            