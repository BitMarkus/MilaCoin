###########
# Modules #
###########

# datetime: for timestamp and datetime
# source: https://pynative.com/python-timestamp/
from datetime import datetime
# hashlib: encryption/decryption module
# source: https://datagy.io/python-sha256/
import hashlib
# blm (block module): Own module for block class
import blm
# trm (transaction module). Own module for handeling transactions
from trm import Transaction
# fnc (Module for own functions): Own set of functions
import fnc

#########
# Class #
#########
       
class Blockchain:
    
    ###########
    # Dunders #
    ###########
    
    # Constructor: Instance Variables
    def __init__(self, block_path, mem_path, cred_path, user_path):
        # Paths and directories
        self.block_path = block_path
        self.mem_path = mem_path
        self.cred_path = cred_path
        self.user_path = user_path
        # List of all block objects
        self.blocks = []
        # Error handling
        self.bc_valid = True
        # self.errors = []
               
    # Print Object as formatted string
    def __str__(self):
        blocks_str = ""
        for block in self.blocks:
            # blocks_str += block.__str__('long') 
            blocks_str += block.__str__() 
            # blocks_str += "\n" 
        return blocks_str
    
    ##################
    # Static methods #
    ##################

    # Method loads all transactions of the mempool 
    # in a list of transaction objects
    @staticmethod
    def load_mempool(user_path, mem_path, block_path):
        tx_count = Transaction.get_tx_count_mempool(mem_path)
        tx_mem = []
        for i in range(tx_count):
            tx_mem.append(Transaction(user_path, mem_path, block_path))
            tx_mem[i].load_tx_from_mempool(i) 
        return tx_mem  

    # Find nonce for the given mining difficulty
    # -> actual mining process
    # Concept for "Proof-of-Work"
    @staticmethod
    def get_nonce(number, timestamp, prev_hash, tx_count, tx_hash, difficulty):
        # Create header string of the block WITHOUT the nonce and NO whitespaces
        header_string_1 = f"{number}{timestamp}{prev_hash}{tx_count}{tx_hash}{difficulty}"        
        found_nonce = False
        nonce = -1 
        while not found_nonce: 
            # The nonce starts at 0 and is incremeted after each loop
            # until it results in a hash with the desired amount of leading zeros (= difficulty)
            nonce += 1      
            # Attach the nonce to the incomplete header string
            header_string_2 = f"{header_string_1}{nonce}"
            # Get the SHA-256 Hash in hexadecimal format
            hash_header = hashlib.sha256(header_string_2.encode()).hexdigest()
            # Check if the amount of leading zeros is equal to the difficulty
            if(hash_header[0:difficulty] == '0' * difficulty):
                found_nonce = True 
            # print(hash_header)
        return nonce           
    
    ####################
    # Instance Methods #
    ####################
    
    # Method loads a new block into the blockchain
    def load_block_in_bc(self, block_nr):
        self.blocks.append(blm.Block(self.block_path, self.user_path, self.mem_path)) 
        self.blocks[block_nr].load_block(block_nr)
            
    # Method for loading the whole blockchain in block and transaction objects
    def load_bc(self):
        print("\nLoading blockchain from files into memory...")
        # Read the highest block number in the block folder
        max_block = blm.Block.get_max_block(self.block_path) 
        # If there is any block file in the block folder
        if(max_block < 0):
            print("No block files in block folder: Blockchain empty!")
        else:   
            # Iterate through blocks
            for block_nr in range(max_block + 1):
                self.load_block_in_bc(block_nr)
                # Check if block is valid
                if not(self.blocks[block_nr].block_valid):
                    print(f"BLOCK {block_nr} INVALID!")
                    # Set blockchain as invalid
                    self.bc_valid = False 
                    # Print block error(s)
                    print("Block errors:")
                    for err in self.blocks[block_nr].error:
                        print(f"> {err}")                                        
                    # Print transaction error(s) if occured
                    if(len(self.blocks[block_nr].tx)):
                        # Iterate through transaction objects
                        print("Transaction errors:")
                        for t in self.blocks[block_nr].tx:
                            if(len(t.error)):
                                # Iterate through transaction errors
                                for err_t in t.error:
                                    print(f"> {err_t}")
                else:
                    print(f"Block {block_nr} of {max_block} successfully loaded...")
            print("Loading blocks finished")
            if(self.bc_valid):
                print("Blockchain successfully loaded")
            else:
                print("LOADING BLOCKCHAIN FAILED!")
                print("\nTerminating program...")
                
    # Method returns the previous hash in the block header of the next block
    # If there is no next block the method returns an empty string
    # Like the method in blm.py, but data is taken from blockchain objects instead of block files
    def get_next_header_hash(self, block_number):    
        # Next block number
        next_number = block_number + 1   
        next_hash = ""
        # Iterate through all blocks, find the one with the right number
        # and get the previous hash from the header
        # If there is no next block the variable next_hash is an empty string
        for block in self.blocks:
            if(block.number == next_number):
                next_hash = block.prev_hash
        return next_hash                                
                
    # Method validates the blockchain
    # That means:
    # 1. Check if the hash of a block matches the hash in the header of the next block
    # 2. Check for every transaction in a block if its hash = ID is correct
    # 3. Check if the transaction hash in the block header is correct 
    # Does NOT validate transactions in terms of signature checking!!!
    # All data comes fron the blockchain object and not from the text files
    def validate_bc(self): 
        print("\nValidating blockchain...")        
        # If there are any block objects in the blockchain
        if not(len(self.blocks)):
            print("No block files in block folder: Blockchain empty!")
        else:   
            # Iterate through blocks
            for block in self.blocks:                
                # Check if the block hash is the same as the previous hash in the next block header
                # In case there is no next block the method returns an empty string
                # block_hash = calculated from current block header
                # next_hash = read from next block header
                block_hash = block.get_header_hash()
                next_hash = self.get_next_header_hash(block.number)
                # print(block_hash)
                # print(next_hash)
                # If the hash of the block doesn't matche the hash in the header of the next block
                # If there is no next block or no block at all, the function returns an empty string
                if(next_hash != "" and block_hash != next_hash):
                    # Set block as invalid and error message
                    block.error.append(f"Hash of block {block.number} does not match the hash in header of block {block.number + 1}!")
                    block.block_valid = False  
                    # Set blockchain as invalid
                    self.bc_valid = False 
                else:  
                    # Go through all transactions in the block and check,
                    # if the hash = ID of transactions are correct
                    for tx in block.tx:
                        # Calculate transaction hash
                        tx_id = tx.get_tx_id()
                        # print(tx_id)
                        # print(tx.tx_id)
                        # Compare to tx hash written in the transaction object
                        if not(tx_id == tx.tx_id):
                            tx.error.append(f"Transaction hash of tx {tx.tx_id} in block {block.number} is corrupted!")
                            block.block_valid = False  
                            tx.tx_valid = False
                            # Set blockchain as invalid
                            self.bc_valid = False 
                        else:
                            # Check if the transaction hash in the block header is correct
                            # print(block.tx_hash)
                            # print(block.get_tx_hash_block())
                            if not(block.tx_hash == block.get_tx_hash_block()):
                                tx.error.append(f"Transaction hash in block {block.number} header does not match the actual transaction hash!")
                                block.block_valid = False 
                                # Set blockchain as invalid
                                self.bc_valid = False 
                # Print block error(s)
                if(len(block.error)):
                    print("Block errors:")
                    for err in block.error:
                        print(f"> {err}")                                        
                # Print transaction error(s) if occured
                # First check if an error occurred in any transaction of the block
                tx_error = False
                for t in block.tx:
                    if(len(t.error)):
                        tx_error = True
                if(tx_error):       
                    print("Transaction errors:")
                    for t in block.tx:
                        if(len(t.error)):
                            # Iterate through transaction errors
                            for err_t in t.error:
                                print(f"> {err_t}")
                # Output messages for block
                if(block.block_valid):
                    print(f"Block {block.number} of {len(self.blocks) - 1} successfully validated...")  
                else:
                    print(f"BLOCK {block.number} INVALID!")
            # Output mssages for blockchain
            print("Validating blocks finished")
            if(self.bc_valid):
                print("Blockchain successfully validated")
            else:
                print("VALIDATING BLOCKCHAIN FAILED!")
                print("\nTerminating program...")                                                   
        
    # Method validates transactions
    # That means that only the the user who has the private key to an address (public key)
    # in the input UTXOs can transfer the coins to the next address
    def validate_tx(self, tx_id, tx_inputs):
        # If transaction is a coinbase transaction
        if not(len(tx_inputs)):
            # print(f"Transaction {tx_id} is a coinbase transaction and cannot be validated!")
            return True           
        else:
            # Load mempool transactions into a list
            mem_tx = self.load_mempool(self.user_path, self.mem_path, self.block_path)  
            # Get number of inputs
            tx_input_count = len(tx_inputs)
            # Generate a list, which contains: 
            # verify[0]: input public key
            # verify[1]: input signature
            # verify[2]: output address
            verify = []
            # Iterate through all transaction inputs
            for inputs in tx_inputs:
                # Get public key and signature ("unlocking script") from inputs
                tx_id_inp = inputs[0]
                index_inp = inputs[1]
                public_key_inp = inputs[2]
                signature_inp = inputs[3]
                # Look for the output of a previous transaction 
                # where the input is referencing to
                # and get the address to generate the public key hash
                # Iterate through all blocks to find the output
                for block in self.blocks:
                    # Iterate through all transactions of the block
                    for tx in block.tx:
                        # Iterate through all outputs of the transaction
                        for outputs in tx.outputs:
                            # outputs[0]: Index Output
                            # outputs[1]: Address
                            # outputs[2]: Volume
                            # If the right output was found
                            # print(tx_id_inp)
                            # print(tx.tx_id)
                            if(tx_id_inp == tx.tx_id and index_inp == outputs[0]):
                                verify.append([public_key_inp, signature_inp, outputs[1]])
                                # print("found block")
                # If not all outputs weren't found in blocks search in mempool
                if(len(verify) < tx_input_count):
                    # Iterate through all transactions in mempool
                    for tx in mem_tx:                    
                        # Iterate through all outputs of the transaction
                        for outputs in tx.outputs:                                
                            # If the right output was found
                            if(tx_id_inp == tx.tx_id and index_inp == outputs[0]):
                                verify.append([public_key_inp, signature_inp, outputs[1]])  
                                # print("found mem")
            # Check if outputs could be found
            if(len(verify) != tx_input_count):
                # print(verify)
                print("Output for transaction input could not be found!")
                return False  
            else:
                # Actual veryfying process
                # 1. Check if public key from inputs leads to same address as in outputs
                # -> Output was directed to sender
                for ver in verify:
                    if not(ver[2] == fnc.get_wallet_address(ver[0])):
                        print(f"Public key in transaction input does not result in address of output ({ver[2]})!")
                        return False  
                    else:
                        # 2. Ckeck signature
                        # -> Sender has the private key to spend the output UTXO
                        result = fnc.verify_ECDSA_str(public_key_inp, signature_inp, tx_id)
                        if not(result):
                            print("Signature ({signature_inp}) not valid!")
                            return False  
                        else:
                            return True  
 
    # Method prints mempool transactions
    def print_mempool(self):
        tx_mem = self.load_mempool(self.user_path, self.mem_path, self.block_path)
        # Check amount of transactions in mempool
        tx_count = len(tx_mem)
        if(tx_count > 0):
            print(f"Number of transactions in mempool: {tx_count}")
            for tx in tx_mem:
                print(tx.__str__(), end='') 
        else:
            print("No transactions in mempool")
            
            
    # Method to mine a block
    def mine_block(self, wallet, difficulty, mining_reward, min_tx_mine):  
        ####################################
        # Load and verify txs from mempool #
        ####################################
        # Check, if there are transactions in mempool
        tx_count_mem = Transaction.get_tx_count_mempool(self.mem_path) 
        # min_tx_mine ist the least amount of transactions in mempool before a new block can be mined
        # Coinbase transactions do not count here
        if(tx_count_mem < min_tx_mine):
            print(f"Next block cannot be mined: At least {min_tx_mine} valid transactions need to be in mempool!") 
        else:
            # Create a list wit all VALID transactions in mempool
            tx_mem = []
            # Iterate through transactions in mempool
            for i in range(tx_count_mem):
                # Create an empty transaction object
                tx = Transaction(self.user_path, self.mem_path, self.block_path)
                # Load transaction data in object
                tx.load_tx_from_mempool(i)
                # If the transaction couldn't be loaded
                if not(tx):
                    print(f"Transaction {i} in mempool is corrupted and cannot be loaded!") 
                else:
                    # Validate signature of transaction
                    if not(self.validate_tx(tx.tx_id, tx.inputs)):
                        print(f"Signature not valid! Transaction {i} not accepted by the system")   
                    else:
                        # Include transaction in validated list
                        tx_mem.append(tx)
        # Check, how many valid transactions are still left
        tx_count_val = len(tx_mem)
        # If there are no valid transactions left
        if(tx_count_val < min_tx_mine):
            print(f"Next block cannot be mined: At least {min_tx_mine} valid transactions need to be in mempool!") 
        else:
            if(tx_count_mem):
                print(f"{tx_count_val} transactions successfully loaded from mempool and verified!") 
                # As all valid transactions are loaded from mempool it can be cleared
                # This way new transactions can be added to mempool during the mining process            
                print("Mempool cleared")  
            Transaction.clear_mempool(self.mem_path)            
            ####################
            # Create new block #
            ####################           
            # Create a block object                  
            bl = blm.Block(self.block_path, self.user_path, self.mem_path)
            # Read the highest block number in the block folder
            max_block = blm.Block.get_max_block(self.block_path) 
            # If the highest block is not present in the directory (-2)
            if(max_block == -2):
                print(f"Next block {max_block+1} cannot be mined: Last block {max_block} is missing!") 
                return False
            else:      
                ### Generate block header data ###                
                # If there is no block file in the directory yet (-1), genesis block needs to be created
                if(max_block == -1):
                    bl.number = 0
                    # Hash for previous hash in block header as there is no previous block 
                    bl.prev_hash = bl.get_genesis_hash() 
                else:
                    bl.number = max_block + 1
                    # Generate the hash of the block header of the previous file
                    bl.prev_hash = bl.get_block_header_hash(max_block, self.block_path)                        
            # Add coinbase transaction to transaction count
            bl.tx_count = tx_count_val + 1                     
            # Timestamp of the beginning of the mining process
            bl.timestamp = datetime.timestamp(datetime.now())              
            # Mining difficulty as instance variable
            bl.difficulty = difficulty 
            # Transfer transaction to block
            # Get conbase transaction
            coinbase = Transaction(self.user_path, self.mem_path, self.block_path) 
            coinbase.get_coinbase_data(wallet, mining_reward, bl.timestamp)
            # Add coinbase to block transactions
            bl.tx.append(coinbase)    
            # Add the other verified transactions from mempool
            for tx in tx_mem:
                bl.tx.append(tx) 
            # Get transaction hash and wirte it to block header   
            bl.tx_hash = bl.get_tx_hash_block()
            # Set block to valid
            bl.block_valid = True
            ##############
            # Mine block #
            ##############
            # Find nonce for the given mining difficulty            
            # -> actual mining process
            print(f"Start minig block {bl.number}...")
            bl.nonce = self.get_nonce(bl.number, bl.timestamp, bl.prev_hash, bl.tx_count, bl.tx_hash, bl.difficulty)
            print(f"Block {bl.number} was sucessfully mined!")
            print(f"It took {bl.nonce} attempts at mining difficulty {bl.difficulty}")             
            # print(bl.get_header_hash())  
            # Write block object to file
            bl.write_block_to_file()
            # Add new block to blockchain
            self.blocks.append(bl)            























            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    
    