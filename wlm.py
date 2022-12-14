###########
# Modules #
###########

# pyperclip: Copy content to clipboard
# source: https://www.codingem.com/copy-text-to-clipboard-in-python/
# to copy receiver addresses to clipboard
import pyperclip
# hashlib: encryption/decryption module
# source: https://datagy.io/python-sha256/
# import hashlib
# datetime: for timestamp and datetime
# source: https://pynative.com/python-timestamp/
from datetime import datetime
# time: For inserting breaks
# If I don't insert a small break (0.2s) before an input, 
# the promt of the input is randomly insertet in the printed text
# source: https://realpython.com/python-sleep/
# import time
# exists: check, if file in a directory exists
# source: https://www.pythontutorial.net/python-basics/python-check-if-file-exists/
from os.path import exists
# itemgetter: required to sort a list in a list
# source: https://www.delftstack.com/de/howto/python/sort-list-of-lists-in-python/
# from operator import itemgetter
# fnc (Module for own functions): Own set of functions
import fnc
# bcm (blockchain module). Own module for blockchain
# from bcm import Blockchain
# trm (transaction module). Own module for handeling transactions
from trm import Transaction
# usr (User module): Own module for user handling
# import usr
# blm (block module): Own module for block class
# from blm import Block

#########
# Class #
#########
       
class Wallet():
    
    ###########
    # Dunders #
    ###########
    
    # Constructor: Instance Variables
    # Wallets are always connected to users! 
    # That means a wallet object must be initialized with a user name and ID
    def __init__(self, user_path, block_path, mem_path, user_name, user_id): 
        self.block_path = str(block_path)
        self.user_path = str(user_path)
        self.mem_path = str(mem_path)
        self.user_name = user_name
        # Set user id = SHA256 hash of user name
        self.user_id = user_id
        # UTXO set of logged in user as list
        self.utxo_user = []
        # Temporary variables for key generation
        self.private_key = ""
        self.public_key = ""
        self.address = ""
        
    # Print Object as formatted string
    def __str__(self):
        string = f"Wallet of user {self.user_name} (ID: {self.user_id})"
        return string  
    
    ##################
    # Static methods #
    ##################
    
    # Method creates a new wallet for a new registered user
    @staticmethod
    def new_wallet(user_path, user_id):
        # Create a new wallet file with the user name ID for the file name
        with open(f"{user_path}/{user_id}.wlt", "w"):
            print("Wallet file successfully created!")
    
    # Method generates a signature from transaction hash = ID
    # returns the signature as base58 encoded string (88 letters) 
    @staticmethod
    def get_tx_signature(tx_id, private_key):
        return fnc.sign_ECDSA_str(private_key, tx_id)  
    
    ####################     
    # Instance Methods # 
    ####################
    
    # Method for creating a private/public key pair and
    # store it in the wallet of the logged in user
    # returns False if the wallet file is not found
    # returns True if everythong is ok
    def generate_keys(self):  
        # Open wallet file of user
        # Check first if wallet file exists
        if not(self.check_wallet_file()): 
            print(f"Error: Wallet file for user {self.user_name} not found!")
            return False
        else: 
            # Create a private/public key pair
            keys = fnc.generate_ECDSA_keys()
            self.private_key = keys[0]
            self.public_key = keys[1]
            self.address = fnc.get_wallet_address(keys[1])              
            with open(f"{self.user_path}/{self.user_id}.wlt", "a") as handle:
                # The wallet contains three data points:
                # 1) the wallet address: not necessary as it is calculated from the private key
                # 2) The private key (string in hex format, 64 letters): necessary!
                # 3) the public key (string base58 encoded, 88 letters): not necessary as it can be recreated from the message and signature                
                # Delimiter: |                
                wlt_string = f"{self.address}|{self.private_key}|{self.public_key}\n"
                handle.write(wlt_string)  
            return True 
        
    # Method returns the address, generated by the method generate_keys()
    def get_address(self):
        return self.address
        
    # Method checks, if a wallet file for the logged in user exists
    def check_wallet_file(self):
        if not(exists(f"{self.user_path}/{self.user_id}.wlt")): 
            print(f"Error: Wallet file for user {self.user_name} not found!")
            return False  
        else: 
            return True 
        
    # Returns a list with all addresses in the wallet of the loggen in user
    def get_addr_list(self):
        # Check if logged in user has a wallet file
        if not(self.check_wallet_file()):
            return False
        else:  
            # Create a list with all addresses in the user wallet
            addr_list = []
            # Open wallet file for reading and get lines
            with open(f"{self.user_path}/{self.user_id}.wlt", "r") as handle: 
                addr_line = list(handle)   
            # iterate through lines
            for addr in addr_line:
                # Split line into elements
                addr_elem = addr.split("|")
                # Check if the list contains 3 elements:
                # 0: address, 1: private key, 2: public key
                if(len(addr_elem) != 3):
                    print(f"Error: Wallet file of user \"{self.name}\" corrupted!")
                    return False
                else:
                    # Add address to address list
                    ### Check for address format ############################################
                    addr_list.append(addr_elem[0])
            return addr_list
        
    # Method returns the Public and the Private key to an address in the user wallet file
    # Returns 0 if the address was not found
    # Or else a tuple of (private key, public key)
    def get_keys_for_address(self, address):
        # Check if logged in user has a wallet file
        if not(self.check_wallet_file()):
            return False
        else:  
            with open(f"{self.user_path}/{self.user_id}.wlt", "r") as handle: 
                 line = list(handle)   
            # iterate through lines
            for l in line:
                # Split line into elements
                elem = l.strip().split("|")  
                # print(elem)                 
                # Check if the list contains 3 elements:
                # 0: address, 1: private key, 2: public key
                if(len(elem) != 3):
                    print(f"Error: Wallet file of user \"{self.name}\" corrupted!")
                    return False
                else:  
                    # print(elem[0])
                    # print(address)
                    # Check the address
                    if(elem[0].strip() == address.strip()):
                        # Return tuple of (private key, public key)
                        # if address was found
                        ### Check for address and keys format ############################################
                        return(elem[1].strip(), elem[2].strip())
            # Return zero if address was NOT found
            return(0)                        
                  
    # Method clears the UTXO list
    def clear_user_utxos(self):
        self.utxo_user = []  
        
    # Method loads all UTXOs for the logged in user into memory
    # The data is extracted from the blockchain object, not from the text files
    # The following information is loaded:
    # 1. Address
    # 2. Block (in which the output is found)
    # 3. Transaction ID (in which the output is found)
    # 4. Output Index
    # 5. Volume of the UTXO
    # Also transactions in mempool MUST be taken into account
    # Or else an UTXO can be double-spent while still in mempool    
    def load_user_utxos(self, blockchain):  
        # Load all transactions in mempool to a list of transaction objects
        tx_mem = blockchain.load_mempool(self.user_path, self.mem_path, self.block_path)
        tx_mem_count = len(tx_mem)
        # print(tx_mem)      
        # Clear UTXO list, or else loading will append, not reload
        self.clear_user_utxos()
        # 1. load all outputs which were send to a users address
        user_outputs = []
        # Get a list with all addresses in user wallet
        addr_list = self.get_addr_list()       
        # Iterate through all blocks
        for block in blockchain.blocks:           
            # Iterate through all transactions of the block
            for tx in block.tx:  
                # Iterate through all outputs of the transaction
                for out in tx.outputs:
                    # Iterate through all addresses
                    for addr in addr_list:
                        # out[0]: Index Output
                        # out[1]: Address
                        # out[2]: Volume
                        if(addr == out[1]):
                            # user_outputs[0]: Address
                            # user_outputs[1]: Block
                            # user_outputs[2]: Tx ID
                            # user_outputs[3]: Output index
                            # user_outputs[4]: Volume
                            user_outputs.append([addr, block.number, tx.tx_id, int(out[0]), float(out[2])]) 
        # Iterate through all transactions in mempool
        if(tx_mem_count > 0):
            for tx in tx_mem:  
                # Iterate through all outputs of the transaction
                for out in tx.outputs:
                    # Iterate through all addresses
                    for addr in addr_list:
                        if(addr == out[1]):
                            user_outputs.append([addr, 'mem', tx.tx_id, int(out[0]), float(out[2])])                         
        # 2. Check, if one of these outputs are referenced in any inputs (Tx ID and index)
        # If no, the transaction is an UTXO and is appended to the UTXO list
        # If yes, it's a STXO and is not included
        # Iterate through all user outputs
        for out in user_outputs: 
            output_found = False
            # Iterate through all blocks
            for block in blockchain.blocks:           
                # Iterate through all transactions of the block
                for tx in block.tx:  
                    # Iterate through all inputs of the transaction
                    for inp in tx.inputs:
                        # Tx ID: out[2] = inp[0]
                        # Output index: out[3] = inp[1]
                        # print(f"TxID: out[2]: {out[2]} = inp[0]: {inp[0]}")
                        # print(f"Output index: out[3]: {out[3]} = inp[1]: {inp[1]}")
                        if(out[2].strip() == inp[0].strip() and int(out[3]) == int(inp[1])):
                            output_found = True                            
            # Iterate through all transactions in mempool
            if(tx_mem_count > 0):
                for tx in tx_mem:                             
                    # Iterate through all inputs of the transaction
                    for inp in tx.inputs:  
                        if(out[2].strip() == inp[0].strip() and int(out[3]) == int(inp[1])):
                            output_found = True                                                            
            if not(output_found):
                self.utxo_user.append(out)  
        # print(self.utxo_user)
        
    # Method returns a string of the user UTXO set of the logged in user
    # For printing
    def print_user_utxos(self):
        # Number of UTXOs in user UTXO set
        utxo_count = len(self.utxo_user)
        utxo_string = ""
        utxo_string += f"UTXO set ({utxo_count}):\n"
        if(utxo_count <= 0):
            utxo_string += "UTXO set is empty!\n"
        else:
            for utxo in self.utxo_user:
                utxo_string += f"> {'Output address':14}: {utxo[0]}\n"
                utxo_string += f"{'Block':16}: {utxo[1]}\n"
                utxo_string += f"{'Tx ID':16}: {utxo[2]}\n"
                utxo_string += f"{'Output index':16}: {utxo[3]}\n"
                utxo_string += f"{'Volume':16}: {utxo[4]} MiC\n"
        return utxo_string
        
    # Method calculates user balance based on UTXO set
    def get_user_balance(self):
        balance = 0
        # Iterate through UTXO set
        for utxo in self.utxo_user:
            balance += utxo[4]
        return balance
    
    # Method for receiving a transaction
    # Creates a wallet address for the logged in user
    def receive_tx(self):       
        # Get address and create a new key pair  
        if(self.generate_keys()):
            print(f"Receiver address: {self.address}")
            # Copy address to clipboard
            pyperclip.copy(self.address)
            print("Address copied to clipboard")
        else:
            return False
        
    # Method selects the right UTXOs of a user for a transaction
    # Right now it has no real system. It just selects UTXOs from the 
    # beginning of the UTXO set until the transaction volume is reached
    # When the volume of the UTXO is greater than the tx volume, 
    # a change needs to be sent back to the sender
    # If the sum of all UTXOs of the user is less than the tx volume,
    # the transaction cannot be done
    # Returns a tuple with:
    # 1. List of UTXOs (if empty, not enough coins for the tx)
    # 2. Change
    def get_tx_input(self, sender_volume):
        # Get user balance
        total_volume = self.get_user_balance()
        # If there are not enough coins for the transaction
        if(sender_volume > total_volume):
            return([], 0)
        else:
            # Creaete an input list
            inputs = []
            # Total input volume
            input_volume = 0
            # Iterate through UTXO set of user
            for utxo in self.utxo_user:
                # utxo[4]: Volume
                input_volume += utxo[4]
                inputs.append(utxo)
                if(input_volume >= sender_volume):
                    return(inputs, (input_volume - sender_volume))
                
    # Method for sending a transaction
    def send_tx(self, mem_path, block_path, bc):
        # Message for exit menues
        fnc.exit_menu_msg()   
        # Enter address
        address = fnc.input_addr("Receiver address: ") 
        if not(address): return False # Exit input
        # Enter voume
        volume = fnc.input_volume("Transaction volume: ")
        if not(volume): return False # Exit input
        # Get possible UTXOs of the user for the transaction
        input_utxos = self.get_tx_input(volume)
        input_count = len(input_utxos[0])
        # If there are not enough coins for the transaction
        if(input_count == 0):
            print("Not enough coins for transaction!")
            return False
        else:          
            # Create a temporary transaction object
            tx = Transaction(self.user_path, mem_path, block_path)         
            tx.timestamp = datetime.timestamp(datetime.now())
            tx.input_count = input_count                                  
            ### Outputs  
            # Add output to receiver
            # outputs[0]: Index Output
            # outputs[1]: Address
            # outputs[2]: Volume
            tx.outputs.append([0, address, volume]) 
            # If there is a change, an output back to the sender needs to be created
            change = input_utxos[1]
            if(change != 0):
                # Make a new key pair and create the receiving address for the sender 
                if not(self.generate_keys()):
                    return False   
                else: 
                    tx.outputs.append([1, self.address, change])                         
            tx.output_count = len(tx.outputs) 
            ### Inputs
            # Iterate through input_utxos
            for utxo in input_utxos[0]:
                # utxo[0]: Address
                # utxo[2]: Tx ID
                # utxo[3]: Output index
                # tx.inputs[0]: Tx ID Output
                # tx.inputs[1]: Index Output (UTXO)
                # tx.inputs[2]: Public key
                # tx.inputs[3]: Signature                                           
                tx.inputs.append([utxo[2], utxo[3], "", ""]) 
            ### Transaction hash = ID 
            tx.tx_id = tx.get_tx_id()
            ### Public key and Signature 
            # Index for input list
            input_index = -1
            # Iterate through input_utxos
            for utxo in input_utxos[0]:
                input_index += 1
                # utxo[0]: Address
                # tx.inputs[2]: Public key
                # tx.inputs[3]: Signature
                # Get keys for UTXO address from user wallet
                # Return tuple of (private key, public key)
                keys = self.get_keys_for_address(utxo[0]) 
                if(keys == 0):
                    print(f"Error: Keys for address {utxo[0]} can not be loaded!")
                    return False
                else:
                    private_key = keys[0]
                    public_key = keys[1] 
                    # print(f"Private key: {private_key}")
                    # print(f"Public key: {public_key}") 
                    # Update inputs list with public key
                    tx.inputs[input_index][2] = public_key
                    # Generate Signature
                    signature = self.get_tx_signature(tx.tx_id, private_key)
                    # Update inputs list with signature
                    tx.inputs[input_index][3] = signature  
                    # Set transaction status to valid
                    ##################### Error code could be written here
                    tx.tx_valid = True                    
            # Check signature
            print("Checking signatures....")
            if not(bc.validate_tx(tx.tx_id, tx.inputs)):
                print("Signatures not valid!")
                return False
            else:
                print("Transaction signatures valid!")
                tx_string = tx.get_tx_string()
                # print(tx_string)                
                # Write Transaction to mempool
                tx.tx_to_mempool(tx_string)                 
            # print(tx)
            # Delete temporary transaction object
            del tx            
            
        
        















                            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        