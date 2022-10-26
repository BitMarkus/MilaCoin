###########
# Modules #
###########

# hashlib: encryption/decryption module
# source: https://datagy.io/python-sha256/
import hashlib
# datetime: for timestamp and datetime
# source: https://pynative.com/python-timestamp/
# from datetime import datetime
# time: For inserting breaks
# If I don't insert a small break (0.2s) before an input, 
# the promt of the input is randomly insertet in the printed text
# source: https://realpython.com/python-sleep/
import time
# exists: check, if file in a directory exists
# source: https://www.pythontutorial.net/python-basics/python-check-if-file-exists/
# from os.path import exists
# itemgetter: required to sort a list in a list
# source: https://www.delftstack.com/de/howto/python/sort-list-of-lists-in-python/
# from operator import itemgetter
# fnc (Module for own functions): Own set of functions
import fnc
# wlm (wallet module). Own module for wallet handling
from wlm import Wallet

#########
# Class #
#########
# Based on: https://stackoverflow.com/questions/59121573/python-login-and-register-system-using-text-files

class User():   
    
    ###########
    # Dunders #
    ###########
    
    # Constructor: Instance Variables
    def __init__(self, cred_path, user_path):
        self.cred_path = cred_path
        self.user_path = user_path
        self.name = None
        self.password = None 
        self.user_id = None
        
    # Print Object as formatted string
    def __str__(self):
        string = f"Logged in user: {self.name}"
        return string  

    ##################
    # Static methods #
    ##################
    
    # Retuns the user ID which is the SHA256 hash of the name as hex string
    @staticmethod
    def get_user_id(name):
        return hashlib.sha256(name.encode()).hexdigest()    
 
    ###################################       
    # Instance Methods for user login # 
    ###################################
               
    # Method iterates through all registered users
    # Storage of user credentials in a text database (credentials.txt)
    def get_users(self):
        with open(self.cred_path, "r") as fp:
             for line in fp.readlines():
                 # Delimiter = |, remove \n at the end of line with strip()
                 username, password = line.strip().split("|")
                 # Generator object
                 yield username, password
                 
    # Method checks, if a username is already registered
    def user_exists(self, username):
        for user, _ in self.get_users():
            if user == username:
                return True
        return False 
    
    # Method resets the user object
    def clear_user(self):
        self.name = None
        self.password = None 
        self.user_id = None
                 
    # Method for signup
    def signup(self): 
        # Message for exit menues
        fnc.exit_menu_msg()
        # Name
        name = str(fnc.input_str("Enter name: "))
        if fnc.exit_menu(name): return True # Exit input
        if(self.user_exists(name)):
            print("Name already taken!")  
            return False
        # Password    
        pwd = str(fnc.input_str("Enter password: "))  
        if fnc.exit_menu(pwd): return True # Exit input
        # Confirm password
        conf_pwd = str(fnc.input_str("Confirm password: "))   
        if fnc.exit_menu(conf_pwd): return True # Exit input         
        # Check if pw and confirmed pw are the same         
        if(conf_pwd == pwd):
            hash256 = hashlib.sha256(conf_pwd.encode()).hexdigest()        
            # Delimiter = |
            with open(self.cred_path, "a") as f:
                 f.write(name + "|" + hash256 + "\n")
            print("You have registered successfully!")                        
            # Create a wallet for the user
            user_id = self.get_user_id(name)
            Wallet.new_wallet(self.user_path, user_id)            
        else:
            print("Password and confirmed password are not matching! \n") 
            return False

    # Method checks username and password             
    def user_authorized(self, username, password):
        for user, pw in self.get_users():
            if(user == username and pw == hashlib.sha256(password.encode()).hexdigest()):
                return True
        return False 

    # Method for login
    def login(self):
        # Message for exit menues
        fnc.exit_menu_msg()
        time.sleep(0.2)        
        self.name = str(fnc.input_str("Name: "))  
        if fnc.exit_menu(self.name): return False # Exit input   
        if not(self.user_exists(self.name)):
            print("Name not found! Please sign up")
            self.clear_user()
            return False  
        else:
            self.password = str(fnc.input_str("Password: ")) 
            # if fnc.exit_menu(self.password): return False # Exit input  
            if self.user_authorized(self.name, self.password):
               # Set user id = SHA256 hash of user name
               self.user_id = self.get_user_id(self.name)
               print(f"Login successful! Welcome back, {self.name}")
               return True
            else:
                print("Login not successful! Wrong password")
                self.clear_user()
                return False 
            
    # Method for logout
    # Sets self.name and self.password to None
    def logout(self):
        print(f"Successfully logged out! Good bye, {self.name}")
        self.clear_user()
        
    # Method checks, if a user is logged in
    # i.e. self.name and self.password are NOT None
    def is_loggedin(self):
        if(self.name == None and self.password == None):
            return False
        else:
            return True
            
    # Retuns the user name and ID as tuple
    def get_user_data(self):
        return(self.name, self.user_id)















    






































































































