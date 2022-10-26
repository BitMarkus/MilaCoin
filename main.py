###########
# Modules #
###########

# fnc (Module for own functions): Own set of functions
import fnc
# blm (block module): Own module for block class
# from blm import Block
# usr (user module): Own module for login/out, session, and user handling
from usr import User
# wlm (wallet module). Own module for wallet handling
from wlm import Wallet
# trm (transaction module). Own module for handeling transactions
# from trm import Transaction
# bcm (blockchain module). Own module for blockchain
from bcm import Blockchain

print("\n.::PROJECT MILACOIN::.")

############
# Settings #
############

# File path to blocks folder
block_path = './blocks'
# File path to mempool
mem_path = './mem/mempool.mem'
# File path to login credentials
cred_path = "./user/credentials.txt"
# File path to user folder
user_path = './user'
# Set mining difficulty (temporary!)
mining_diff = 6
# Set mining reward
mining_reward = 10.000
# Number of transactions in mempool (excluding coinbase) in order to mine a block
# 0 means that a block can be mined without any transactions
min_tx_mine = 0

###########
# Objects #
###########

# Create list of all Block-objects
bc = Blockchain(block_path, mem_path, cred_path, user_path)
bc.load_bc()
# Validate blockchain hashes
# Does not validate transaction signatures!
bc.validate_bc()  
# create empty user object for user login
user = User(cred_path, user_path)

#############
# Main Code #
############# 

# If Blockchain is valid, go to login menue
if(bc.bc_valid):
#if(True):
#if(False):    
    ##############
    # Login Menu #
    ##############
    while(True):
        # If no user is logged in, show login menu
        if not(user.is_loggedin()):
            print("\n:LOGIN MENU:")            
            print("1) Login")
            print("2) Signup")
            print("3) Exit")         
            menu1 = int(fnc.input_int("Please choose: "))

            ##### Login #####
            if(menu1 == 1):  
                print("\n:LOGIN:")
                if(user.login()):
                    # Get user name and ID
                    user_data = user.get_user_data()
                    # Create a wallet object for the logged in user
                    wallet = Wallet(user_path, block_path, mem_path, user_data[0], user_data[1])  
                    print("Wallet successfully loaded") 
                    wallet.load_user_utxos(bc)
                    print(f"UTXO set for {user_data[0]} successfully loaded") 
                    balance = wallet.get_user_balance()
                    print(f"Current balance: {balance:5.3f} MiC")
                else:
                    user.clear_user()

            ##### Signup #####                
            elif(menu1 == 2):     
                print("\n:SIGNUP:")
                user.signup()                                  
                
            ##### Exit Program #####
            elif(menu1 == 3):
                print("\nExit program...")
                break 
            
            ##### Wrong Input #####  
            else:
                print("Not a valid option!")   
                
        # If a user is logged in, show main menu
        else:
            #############
            # Main Menu #
            #############
            while(True):  
                print("\n:MAIN MENU:")
                print("1) Send Transaction")
                print("2) Receive Transaction")
                print("3) Mine Next Block")
                print("4) View Blockchain")
                print("5) View Mempool")
                print("6) View Balance and UTXO set")
                print("7) Logout")
                menu2 = int(fnc.input_int("Please choose: "))
            
                ##### Send Transaction #####  
                if(menu2 == 1):       
                    print("\n:SEND TRANSACTION:")  
                    wallet.send_tx(mem_path, block_path, bc)
                    # Reload user UTXOs
                    wallet.load_user_utxos(bc)
                    # Print new user balance
                    balance = wallet.get_user_balance()
                    print(f"New balance: {balance:5.3f} MiC")
                    
                ##### Receive Transaction #####  
                elif(menu2 == 2):       
                    print("\n:RECEIVE TRANSACTION:") 
                    # Get receiver address
                    wallet.receive_tx()                  
                 
                ##### Mine Next Block #####            
                elif(menu2 == 3):
                    print("\n:MINE NEXT BLOCK:") 
                    bc.mine_block(wallet, mining_diff, mining_reward, min_tx_mine) 
                    # Reload UTXO set of user
                    wallet.load_user_utxos(bc)
                    # Print new balance
                    balance = wallet.get_user_balance()
                    print(f"New balance: {balance:5.3f} MiC")
                    
                ##### View Blockchain #####
                elif(menu2 == 4):
                    print("\n:VIEW BLOCKCHAIN:") 
                    print(bc)
                    
                ##### View Mempool #####
                elif(menu2 == 5):
                    print("\n:VIEW MEMPOOL:") 
                    bc.print_mempool()
            
                ##### View Balance #####
                elif(menu2 == 6):
                    print("\n:VIEW BALANCE AND UTXO SET:")
                    balance = wallet.get_user_balance()
                    print(f"Current balance: {balance:5.3f} MiC\n")
                    print(wallet.print_user_utxos(), end='')
                    
                ##### Logout #####
                elif(menu2 == 7):
                    user.logout()
                    break
                
                ##### Wrong Input #####  
                else:
                    print("Not a valid option!")        





























































        
        
        
        
        
        
        
        
        
        
        