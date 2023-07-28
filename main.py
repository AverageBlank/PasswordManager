# %%
###################! Imports ###################
# ? For Generating Password
import string

# ? For Running Commands
from os import name as OSName, system

# ? For Generating Password
from random import choice as randchoice

# ? For Pausing the Script
from time import sleep

# ? For Connecting to MySQL
from sqlite3 import connect

# ? For Copying to Clipboard
import pyperclip

# ? For Hiding Password
from pwinput import pwinput

# ? For encrpytion
from cryptography.fernet import Fernet


###################! Functions ###################
######? Generating Passwords ######
def GenPass(p):
    genop = ""
    while True:
        gen = input("Do you want to generate a password? ").lower()
        if gen == "yes":
            while True:
                try:
                    genlen = int(input("How long should the password be? "))
                    if genlen <= 0:
                        raise ValueError
                    break
                except:
                    print("Please enter a valid positive number.")
            for _ in range(genlen):
                genop += randchoice(
                    string.ascii_letters + string.digits + string.punctuation
                )

            print(f"The generated password is {genop}")
            sleep(5)
            return genop
        elif gen == "no":
            return pwinput(p)
        else:
            print("Please only enter either yes or no.")


######? Adding Entry ######
def AddEntry(t):
    #####* Variables #####
    result = []
    NameResult = []

    #####* Clearing the Screen #####
    system(clear)
    print("-" * 100)
    print("-" * 10, "This is a Password Manager")
    print("-" * 100)
    print()

    #####* Going Through Table #####
    cur.execute(f"select * from {t}")
    res = cur.fetchall()
    for _ in res:
        result.append(_)
    cur.execute(f"select Name from {t}")
    res = cur.fetchall()
    if len(res) != 0:
        for _ in res:
            _ = _[0].lower()
            NameResult.append(_)

    #####* Getting Values #####
    while True:
        name = input("What do you want the entry to be called? ")
        if name == "":
            print("Name cannot be left empty.")
            continue
        if name.lower() in NameResult:
            print("That name already exists.")
            continue
        break
    email = input("What is the Email ID(can be left empty)? ")
    usrname = input("What is the Username(can be left empty)? ")
    passwd = GenPass("What is the Password? ")
    passwd = fernet.encrypt(passwd.encode())

    #####* Adding Values to Table #####
    cur.execute(
        rf'insert into {t} values({len(result) + 1}, "{name}", "{email}", "{usrname}", "{passwd}")'
    )
    conn.commit()
    print(f"The entry for {name} has been successfully added!")
    sleep(1)


######? Editting Entry ######
def EditEntry(t):
    #####* Variables #####
    result = []
    Name = "-"
    Email = "-"
    Username = "-"
    Passwd = "-"

    #####* Going Through Table #####
    cur.execute(f"select * from {t}")
    res = cur.fetchall()
    for _ in res:
        result.append(_)

    #####* Printing Options #####
    while True:
        ###? Clearing the Screen ###
        sleep(1)
        system(clear)
        print("-" * 100)
        print("-" * 10, "This is a Password Manager")
        print("-" * 100)
        print()
        ###? Options ###
        for index, value in enumerate(result):
            print(f"Press {index + 1} for {value[1]}")
        print("Press 0 to quit")
        choice = input("Which entry do you want to edit? ")
        # ? Checking if choice is valid integer
        if choice.isdigit():
            choice = int(choice)
            if choice == "0":
                quit()
            else:
                try:
                    if 0 > choice or choice > index + 1:
                        sleep(1)
                        system(clear)
                        print("-" * 100)
                        print("-" * 10, "This is a Password Manager")
                        print("-" * 100)
                        print()
                        print("Please enter a valid choice.")
                        continue
                except:
                    sleep(1)
                    system(clear)
                    print("-" * 100)
                    print("-" * 10, "This is a Password Manager")
                    print("-" * 100)
                    print()
                    print("Please enter a valid choice.")
                    continue
            break

    #####* Getting Values #####
    ###? Name ###
    while True:
        name = input("Do you want to change the name? ").lower()
        if name not in ["yes", "no"]:
            print('Please enter only "yes" and "no"')
            continue
        elif name == "yes":
            while True:
                Name = input("What should the name be? ")
                cur.execute(f"update {t} set Name='{Name}' where IndexNo={choice}")
                break
        break
    ###? Email ###
    while True:
        email = input("Do you want to change the email? ").lower()
        if email not in ["yes", "no"]:
            print('Please enter only "yes" and "no"')
            continue
        elif email == "yes":
            while True:
                Email = input("What should the email be? ")
                cur.execute(f"update {t} set Email='{Email}' where IndexNo={choice}")
                break
        break
    ###? Username ###
    while True:
        username = input("Do you want to change the Username? ").lower()
        if username not in ["yes", "no"]:
            print('Please enter only "yes" and "no"')
            continue
        elif username == "yes":
            while True:
                Username = input("What should the username be? ")
                cur.execute(
                    f"update {t} set Username='{Username}' where IndexNo={choice}"
                )
                break
        break
    ###? Password ###
    while True:
        passwd = input("Do you want to change the password? ").lower()
        if passwd not in ["yes", "no"]:
            print('Please enter only "yes" and "no"')
            continue
        elif passwd == "yes":
            while True:
                Passwd = GenPass("What should the password be? ")
                Passwd = fernet.encrypt(Passwd.encode())
                cur.execute(
                    f"update {t} set Password='{Passwd}' where IndexNo={choice}"
                )
                break
        break
    if Name == "-" and Email == "-" and Username == "-" and Passwd == "-":
        print("The entry has not been modified.")
    else:
        conn.commit()
        print("The entry has been successfully modified!")
    sleep(1)


######? Deleting Entry ######
def DelEntry(t):
    #####* Variables #####
    result = []
    Names = []

    #####* Going Through Table #####
    cur.execute(f"select * from {t}")
    res = cur.fetchall()
    for _ in res:
        result.append(_)

    #####* Printing Options #####
    while True:
        ###? Clearing the Screen ###
        sleep(1)
        system(clear)
        print("-" * 100)
        print("-" * 10, "This is a Password Manager")
        print("-" * 100)
        print()
        ###? Options ###
        for index, value in enumerate(result):
            print(f"Press {index + 1} for {value[1]}")
        print("Press 0 to quit")
        choice = input("Which entry do you want to delete? ")
        # ? Checking if choice is valid integer
        if choice.isdigit():
            choice = int(choice)
            if choice == "0":
                quit()
            else:
                try:
                    if 0 > choice or choice > index + 1:
                        sleep(1)
                        system(clear)
                        print("-" * 100)
                        print("-" * 10, "This is a Password Manager")
                        print("-" * 100)
                        print()
                        print("Please enter a valid choice.")
                        continue
                except:
                    sleep(1)
                    system(clear)
                    print("-" * 100)
                    print("-" * 10, "This is a Password Manager")
                    print("-" * 100)
                    print()
                    print("Please enter a valid choice.")
                    continue
            break

    #####* Confirmation #####
    while True:
        cur.execute(f"select Name from {t} where IndexNo={choice}")
        name = cur.fetchall()[0][0]
        conf = input(f"Are you sure you want to delete the entry for {name}? ").lower()
        if conf not in ["yes", "no"]:
            continue
        elif conf == "yes":
            cur.execute(f"delete from {t} where IndexNo={choice}")
            conn.commit()
            ###? Setting Proper Index Numbers ###
            cur.execute(f"select Name from {t}")
            names = cur.fetchall()
            for _ in names:
                Names.append(_[0])
            for index, val in enumerate(Names):
                cur.execute(f"update {t} set IndexNo={index + 1} where Name='{val}'")
            conn.commit()
            ###? Confirmation ###
            print(f"The entry for {name} has been successfully deleted!")
            sleep(1)
            break
        elif conf == "no":
            break


######? Copying Entry ######
def CopyEntry(t):
    try:
        #####* Variables #####
        result = []

        #####* Going Through Table #####
        cur.execute(f"select * from {t}")
        res = cur.fetchall()
        for _ in res:
            result.append(_)

        #####* Printing Options #####
        while True:
            ###? Clearing the Screen ###
            sleep(1)
            system(clear)
            print("-" * 100)
            print("-" * 10, "This is a Password Manager")
            print("-" * 100)
            print()
            ###? Options ###
            for index, value in enumerate(result):
                print(f"Press {index + 1} for {value[1]}")
            print("Press 0 to quit")
            choice = input("Which entry do you want to copy? ")
            # ? Checking if choice is valid integer
            if choice.isdigit():
                choice = int(choice)
                if choice == "0":
                    quit()
                else:
                    try:
                        if 0 > choice or choice > index + 1:
                            sleep(1)
                            system(clear)
                            print("-" * 100)
                            print("-" * 10, "This is a Password Manager")
                            print("-" * 100)
                            print()
                            print("Please enter a valid choice.")
                            continue
                    except:
                        sleep(1)
                        system(clear)
                        print("-" * 100)
                        print("-" * 10, "This is a Password Manager")
                        print("-" * 100)
                        print()
                        print("Please enter a valid choice.")
                        continue
                break
        #####* Copying to Clipboard #####
        ###? Getting Name ###
        cur.execute(f"select Name from {t} where IndexNo={choice}")
        name = cur.fetchall()[0][0]
        while True:
            ###? Getting What User Wants to Copy to Clipboard ###
            conf = input(
                "What do you want to copy(email, username, password)? "
            ).lower()
            if conf not in [
                "email",
                "username",
                "password",
                "e",
                "u",
                "p",
                "mail",
                "user",
                "pass",
            ]:
                continue

            ###? Email ###
            elif conf == ["e", "email", "mail"]:
                cur.execute(f"select Email from {t} where IndexNo={choice}")
                result = cur.fetchall()[0][0]
                if result == "":
                    print(f"The email in {name} does not exist.")
                    continue
                pyperclip.copy(result)
                sleep(1)
                print("The email has been successfully copied to your clipboard!")
                sleep(0.5)
                input("Please enter to continue.... ")
                break

            ###? Username ###
            elif conf in ["u", "user", "username"]:
                cur.execute(f"select Username from {t} where IndexNo={choice}")
                result = cur.fetchall()[0][0]
                if result == "":
                    print(f"The Username in {name} does not exist.")
                    continue
                pyperclip.copy(result)
                sleep(1)
                print("The username has been successfully copied to your clipboard!")
                sleep(0.5)
                input("Please enter to continue.... ")
                break

            ###? Password ###
            elif conf in ["pass", "p", "password"]:
                cur.execute(f"select Password from {t} where IndexNo={choice}")
                result = cur.fetchall()[0][0][2:-1]
                decPass = fernet.decrypt(result).decode("utf-8")
                if result == "":
                    print(f"The Password in {name} does not exist.")
                    continue
                print(decPass)
                pyperclip.copy(decPass)
                sleep(1)
                print("The password has been successfully copied to your clipboard")
                sleep(0.5)
                input("Please enter to continue.... ")
                break
    except:
        sleep(1)
        print("Please enter the correct encryption key: ")
        sleep(0.5)
        input("Please enter to continue.... ")


###################! Encryption ###################
#####* Setting Clear Screen Variable #####
clear = "clear" if OSName == "posix" else "cls"
#####* Clearing The Screen #####
sleep(1)
system(clear)
print("-" * 100)
print("-" * 10, "This is a Password Manager")
print("-" * 100)
print()
while True:
    inp = input("Do you have an encryption key? ")
    if inp.lower() == "yes":
        key = pwinput("Enter the key: ")
    elif inp.lower() == "no":
        while True:
            a = input(
                "Do you want to generate a key(you will lose access to previous data)? "
            )
            if a.lower() == "no":
                exit()
            elif a.lower() == "yes":
                key = Fernet.generate_key()
                key = key.decode("utf-8")
                print(
                    f"Given below is the key, you will not get access to it again.\n{key}"
                )
                while True:
                    b = input("Do you want to copy the key? ")
                    if b.lower() == "yes":
                        pyperclip.copy(key)
                        break
                    if b.lower() == "no":
                        break
                break
            else:
                continue
    else:
        try:
            fernet = Fernet(inp)
            break
        except:
            continue
    fernet = Fernet(key)
    break


###################! Connecting To SQL ###################
#####* Connecting to SQLite3 #####
conn = connect("Manager.db")
cur = conn.cursor()
#####* Checking if table exists
table = "passwords"
cur.execute(
    f"Create table if not exists {table}(IndexNo int, Name varchar(244), Email varchar(244), Username varchar(244), Password varchar(244))"
)

###################! Printing Options ###################
while True:
    ####* Printing what the script does ####
    system(clear)
    print("-" * 100)
    print("-" * 10, "This is a Password Manager")
    print("-" * 100)
    print()
    ####* Printing Options ####
    print("Press 1 to Add Entry")
    print("Press 2 to Edit Entry")
    print("Press 3 to Delete an Entry")
    print("Press 4 to Copy an Entry")
    print("Press 0 to quit")
    choice = input("What is your choice? ")
    # ? Checking if choice is valid integer
    if choice.isdigit():
        choice = int(choice)
        if 0 > choice or choice >= 5:
            continue

    #######? Calling Functions #######
    if choice == 0:
        quit()
    elif choice == 1:
        AddEntry(table)
    elif choice == 2:
        EditEntry(table)
    elif choice == 3:
        DelEntry(table)
    elif choice == 4:
        CopyEntry(table)

# %%
