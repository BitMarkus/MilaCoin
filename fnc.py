###########
# Modules #
###########

# time: For inserting breaks
# If I don't insert a small break (0.2s) before an input, 
# the promt of the input is randomly insertet in the printed text
# source: https://realpython.com/python-sleep/
import time
# Functions for elyptic curve cryptography
import ecdsa
# Base58 encoding to shorten numbers
import base58
# hashlib: encryption/decryption module
# source: https://datagy.io/python-sha256/
import hashlib

#######################################
# Functions for validating user input #
#######################################

# Check user Input for empty string 
# OR the character |, which is used as a delimiter
# whitespaces are ignored: strip()
# Method returns False when the string is empty 
# OR contains delimiters |, {tx:} or [x]
def input_str(prompt):
    while(True):
        time.sleep(0.2)
        string = input(prompt)
        if(len(string.strip()) == 0):
            print("No input! Try again:")
        elif('{tx:}' in string):
            print("Characters \"{tx:}\" not allowed in input! Try again:")  
        elif('[x]' in string):
            print("Characters \"[x]\" not allowed in input! Try again:")   
        elif('|' in string):
            print("Character \"|\" not allowed in input! Try again:")   
        else:
            return string.strip()
        
# Creates an input with prompt
# which is checked, if the input is an integer number
# If not, the loop will continue until a valid number is entered
def input_int(prompt):
    while(True):
        time.sleep(0.2)
        nr = input(prompt)
        if not(check_int(nr)):
            print("Input is not an integer number! Try again:")
        else:
            return int(nr)   
        
# Creates an input with prompt
# which is checked, if the input is a valid address
# If not, the loop will continue until a valid string is entered
# Or the exit string is entered
def input_addr(prompt):
    while(True):
        time.sleep(0.2)
        add = input(prompt)
        if(exit_menu(add)):
            return False
        elif not(check_address(add)):
            print("Input is not a valid MiC address! Try again:")
        else:
            return str(add)
        
# Creates an input with prompt
# which is checked, if the volume is in a valid format
# If not, the loop will continue until a valid string is entered
# Or the exit string is entered
# Cannot be negative and needs to be an int or float
def input_volume(prompt):
    while(True):
        time.sleep(0.2)
        nr = input(prompt)
        if(exit_menu(nr)):
            return False
        elif not(check_nr(nr)):
            print("Input is not a number! Try again:")
        else:
            if(float(nr) <= 0):
                print("Volume cannot be negative! Try again:")
            else:
                # Check if volume has more than three digits after dot
                if(get_dec(str(nr)) > 3):
                    print("MiC can only have maximum three decimals! Try again:")
                else:
                    return float(nr)    

####################################        
# Functions to check variable type #
####################################

# Check variable for number (int or float)
# Returns True if conversion was successful
# or False when the variable cannot be converted to a number
def check_nr(var):
    try:
        # Convert it into integer
        val = int(var)
        return True
    except ValueError:
        try:
            # Convert it into float
            val = float(var)
            return True
        except ValueError:
            return False

# Check variable for int
# Returns True if conversion was successful
# or False when the variable cannot be converted to an integer number
def check_int(var):
    try:
        val = int(var)
        return True
    except ValueError:
        return False
    
# Check variable for float
# Returns the variable as int if conversion was successful
# or False when the variable cannot be converted to an integer number
def check_float(var):
    try:
        # Convert it into integer
        val = int(var)
        return False
    except ValueError:
        try:
            # Convert it into float
            val = float(var)
            return True
        except ValueError:
            return False
        
# Checks a variable if it is a valid SHA256 hash
# Checks for SHA256 hash in hex form = 64 characters
# Works also for the private key as it is a 256 bit integer in hex format
def check_prk_hash(var):
    # Check if string contains 64 characters
    if(len(var) != 64):
        return False
    else:
        # Check if string is in hexadecimal format
        # source: https://stackoverflow.com/questions/58437353/how-can-we-efficiently-check-if-a-string-is-hexadecimal-in-python
        try:
            int(var, 16)
            return True
        except ValueError:
            return False
  
# Checks if a string is base58 encoded
def check_base58(var):
    try:
        base58.b58decode(var)
        return True
    except ValueError:
        return False
        
# Check if a variable is in a public key or signature format
# the uncompressed public key (used here) and the signature are both 64 bytes long 
# and base58 encoded
def check_puk_sig(var):
    # Check if key is a base58 encoded string
    if not(check_base58(var)):
        return False
    else:
        # decode key to binary data and check, if it has 64 bytes
        binary = base58.b58decode(var)
        if(len(binary) != 64):
            return False
        else:
            return True
            # Eventually it needs to be checked here if the point is on the curve
            
# Check if a variable is in a address format
# The adress is derived from the public key
# public key -> SHA256(32bytes) -> SHA256(32bytes) -> SHA1(20bytes) -> base58 encoding -> address
def check_address(var):
    # Check if key is a base58 encoded string
    if not(check_base58(var)):
        return False
    else:    
        # decode key to binary data and check, if it has 20 bytes
        binary = base58.b58decode(var)
        if(len(binary) != 20):
            return False
        else:
            return True
               
############################################
# Functions for elyptic curve cryptography #
############################################

# Function returns a private / public ecdsa key pair
# private key: string in hex format (64 letters)
# public key: string base58 encoded (88 letters) to make it shorter
def generate_ECDSA_keys():
    # Generate signing key = private key for generating signatures
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    # convert private key to hex
    private_key = sk.to_string().hex() 
    # Generate verifying key = public key for validating signatures
    vk = sk.get_verifying_key()
    # public_key = vk.to_string().hex()
    # encode with base58 public key to make it shorter      
    # public_key = base58.b58encode(bytes.fromhex(public_key)).decode()
    public_key = base58.b58encode(vk.to_string()).decode()
    return private_key, public_key

# Function signs a string with a given private key
# private key as string in hex format 
# returns the signature: string base58 encoded (88 letters) 
def sign_ECDSA_str(private_key, string):
    # encode string to binary
    bstring = string.encode()
    # Recover signing key from private key string
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    # Generate signature
    signature = base58.b58encode(sk.sign(bstring)).decode()
    return signature

# Function verifyes a string with a given public key and a signature
# public key and signature base58 encoded
# Returns True or False
def verify_ECDSA_str(publik_key, signature, string):
    # encode string to binary
    bstring = string.encode()
    # decode signature back form base58 encoding
    sig = base58.b58decode(signature) 
    # decode public key back form base58 encoding
    pk = base58.b58decode(publik_key)
    # recover verifying key from string
    vk = ecdsa.VerifyingKey.from_string(pk, curve=ecdsa.SECP256k1)
    try:
        # Verify string
        vk.verify(sig, bstring)
        # print("Validation successful!")
        return True
    except:
        # print("Validation failed!")
        return False

# Function recovers the public key from the string and the signature
# takes the string as a string
# takes the signature as a base58 encoded string
# returns a tuple with two base58 encoded public keys as strings
# ONLY ONE of them is the right one
def recover_ECDSA_pubkey(signature, string):
    # set parameters for VerifyingKey.from_public_key_recovery method
    bsig = base58.b58decode(signature)
    bstr = string.encode()
    # curve = ecdsa.curves.SECP256k1
    keys = ecdsa.VerifyingKey.from_public_key_recovery(bsig, bstr, curve=ecdsa.SECP256k1)
    key1 = base58.b58encode(keys[0].to_string()).decode()
    key2 = base58.b58encode(keys[1].to_string()).decode()
    return key1, key2

# Function creates a wallet address fron a public key
# Public key as base58 encoded string
# public key -> SHA256(32bytes) -> SHA1(20bytes) -> base58 encoding -> address
def get_wallet_address(public_key):
    # 1. decode base58 encoded public key
    x1 = base58.b58decode(public_key)
    # print(x1)
    # 2. create a SHA256 hash of the public key
    x2 = hashlib.sha256(x1).digest()
    # print(x2)
    # 3. create a ripemd160 hash of the sha256 hash
    # -> AttributeError: module 'hashlib' has no attribute 'ripemd160'
    # Instead SHA1 is used
    x3 = hashlib.sha1(x2).digest()
    # print(x3)
    # 4. Base58 encode the hash
    x4 = base58.b58encode(x3).decode()
    # print(x4)
    return x4

##################
# Misc functions #
##################

# Function to exit any menue
def exit_menu(var, stop = "<exit>"):
    if(var == stop):
        print("Input canceled!")
        return True
    else:
        return False
    
# Prints a message to exit a menue with <exit>
def exit_menu_msg(stop = "<exit>"):
    print(f"> Enter {stop} to return to menue")
    
# Function returns number of decimal places after decimal point
# source: https://stackoverflow.com/questions/28749177/how-to-get-number-of-decimal-places
def get_dec(no_str):
    if "." in no_str:
        return len(no_str.split(".")[1].rstrip("0"))
    else:
        return 0

















        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        