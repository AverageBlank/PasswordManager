# ? Flask --> For the backend of HTML
from flask import (
    Flask,
    render_template,
    make_response,
    request,
    redirect,
    url_for,
)

# ? String -> For Generating Password
import string

# ? OS -> For Running Commands
from os import name as OSName, system, environ

# ? Random -> For Generating Password
from random import choice as randChoice, shuffle as randShuffle

# ? Time -> For Pausing the Script
from time import sleep

# ? Datetime
from datetime import datetime

# ? SQLite3 -> For Connecting to MySQL
from sqlite3 import connect
from pymongo import MongoClient
from dotenv import load_dotenv

# ? Pyperclip -> For Copying to Clipboard
import pyperclip

# ? Re --> For checking if characters exist in string
from re import compile

# ? Cryptography -> For encrpytion
from cryptography.fernet import Fernet, InvalidToken

###################! Functions ###################
######? Connecting to SQLite3 #####
conn = connect("Manager.db")
cur = conn.cursor()
#####* Checking if table exists
table = "passwords"


# ? Required.
app = Flask(__name__)
app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
app.config["MONGO_URI"] = environ.get("link")
domain = "https://pass.aaloke.com/"
hasUsedApp = False

# ? Connecting to the Mongo DB Database
load_dotenv()
mongoLink = environ.get("link")
client = MongoClient(mongoLink)
db = client["PassManager"]

# ? Connecting to Collections
passColl = db["urls"]
usersColl = db["users"]

# ? Create indexes (if needed)
passColl.create_index("ID", unique=True)
passColl.create_index("Timestamp")
passColl.create_index("Name")
passColl.create_index("Email/Username")
passColl.create_index("Password")
passColl.create_index("UserID")

usersColl.create_index("ID", unique=True)
usersColl.create_index("UserID", unique=True)
usersColl.create_index("Key", unique=True)
print("Successfully connected to MongoDB.")


######? Encryption #####
def encryption():  # TODO
    global fernet

    while True:
        #####* Clearing The Screen #####

        inp = confirm("Do you have an encryption key?", style=minimalStyle).ask()
        if inp:
            key = password("Enter the key:", style=minimalStyle).ask()
        else:
            while True:
                GenKey = confirm(
                    "Do you want to generate a key?\n[You will lose access to previous data]",
                    style=minimalStyle,
                ).ask()
                if GenKey is False:
                    exit()
                elif GenKey:
                    key = Fernet.generate_key()
                    key = key.decode("utf-8")
                    print(
                        f"Given below is the key, you will not get access to it again.\n{key}"
                    )
                    while True:
                        copyKey = confirm(
                            "Do you want to copy the key?", style=minimalStyle
                        ).ask()
                        if copyKey:
                            pyperclip.copy(key)
                        break
                    break
                else:
                    continue
        try:
            fernet = Fernet(key)
            break
        except ValueError:
            print("The key you entered is invalid.")


######? Generating Passwords ######
def GenPass(p):  # TODO
    genop = []
    while True:
        gen = confirm("Do you want to generate a password?", style=minimalStyle).ask()
        if gen:
            while True:
                try:
                    genlen = int(
                        text(
                            "How long should the password be?", style=minimalStyle
                        ).ask()
                    )
                    if genlen <= 0:
                        raise ValueError
                    break
                except ValueError or TypeError:
                    print("Please enter a valid positive number.")
            while True:
                for _ in range(genlen):
                    genop.append(
                        randChoice(
                            string.ascii_letters + string.digits + "@!_#$%^&*()<>?/}{~:"
                        )
                    )

                regex = compile("[@!_#$%^&*()<>?/}{~:]")
                if regex.search("".join(str(v) for v in genop)) is None:
                    genop = []
                    continue
                if any(i.isdigit() for i in genop) is False:
                    genop = []
                    continue
                if any(i.isalpha() for i in genop) is False:
                    genop = []
                    continue
                break

            randShuffle(genop)
            genop = "".join(str(v) for v in genop)

            print(f"Generated Password: {genop}")
            return genop
        elif gen is False:
            return password(p).ask()


######? Adding Entry ######
def AddEntry(t):
    #####* Variables #####
    result = passColl.count_documents({})

    temp = passColl.find({}, {"Name": 1, "_id": 0})
    names = [doc["Name"] for doc in temp if "Name" in doc]

    #####* Getting Values #####
    while True:
        # name = text(
        #     "What do you want the entry to be called?", style=minimalStyle
        # ).ask()
        # Aaloke implement this.
        name = ""
        if name == "":
            print("Name cannot be left empty.")
            # Aaloke return error..
            continue
        if name.lower() in names:
            print("That name already exists.")
            # Aaloke return error..
            continue
        break
    # email = text("Enter Email ID [Optional]:", style=minimalStyle).ask() # Aaloke
    emailUsername = ""
    passwd = GenPass()
    passwd = fernet.encrypt(passwd.encode())  # TODO TO BE FIXED
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")
    userID = ""  # Aaloke set this up.

    #####* Adding Values to Table #####
    values = {
        "ID": len(result) + 1,
        "Timestamp": time,
        "Name": name,
        "Email/Username": emailUsername,
        "Password": passwd,
        "UserID": userID,
    }
    passColl.insert_one(values)


######? Editting Entry ######
def EditEntry(t):
    try:
        #####* Variables #####
        result = []
        options = []
        Name = "-"
        Email = "-"
        Username = "-"
        Passwd = "-"

        #####* Going Through Table #####
        cur.execute(rf"select * from {t}")
        res = cur.fetchall()
        for _ in res:
            result.append(_)

        #####* Printing Options #####
        ###? Clearing the Screen ###

        ###? Options ###
        for i in result:
            options.append(f"{i[0]}. {i[1]}".title())
        options.append("0. Back")
        choice = select(
            "Which entry do you want to edit?", options, style=minimalStyle
        ).ask()
        choice = int(choice[0])
        if choice == 0:
            raise AttributeError

        #####* Getting Values #####
        opt = checkbox(
            "What all do you want to edit?",
            ["Name", "Email", "Username", "Password"],
            style=minimalStyle,
        ).ask()
        ###? Name ###
        if "Name" in opt:
            while True:
                Name = text("What should the name be?", style=minimalStyle).ask()
                if Name == "":
                    print("Name cannot be left empty.")
                    continue
                cur.execute(rf"update {t} set Name='{Name}' where IndexNo={choice}")
                break
        ###? Email ###
        if "Email" in opt:
            Email = text("What should the email be?", style=minimalStyle).ask()
            cur.execute(rf"update {t} set Email='{Email}' where IndexNo={choice}")
        ###? Username ###
        if "Username" in opt:
            Username = text("What should the username be?", style=minimalStyle).ask()
            cur.execute(rf"update {t} set Username='{Username}' where IndexNo={choice}")
        ###? Password ###
        if "Password" in opt:
            Passwd = GenPass("What should the password be?")
            Passwd = fernet.encrypt(Passwd.encode())
            cur.execute(rf'update {t} set Password="{Passwd}" where IndexNo={choice}')
        if Name == "-" and Email == "-" and Username == "-" and Passwd == "-":
            print("The entry has not been modified.")
        else:
            conn.commit()
            print("The entry has been successfully modified!")
        cont().ask()
    except AttributeError:
        PrintOptions()


######? Deleting Entry ######
def DelEntry(t):
    try:
        #####* Variables #####
        result = []
        options = []
        Names = []

        #####* Going Through Table #####
        cur.execute(rf"select * from {t}")
        res = cur.fetchall()
        for _ in res:
            result.append(_)

        #####* Printing Options #####
        ###? Clearing the Screen ###

        ###? Options ###
        for i in result:
            options.append(f"{i[0]}. {i[1]}".title())
        options.append("0. Back")
        choice = select(
            "Which entry do you want to edit?", options, style=minimalStyle
        ).ask()
        choice = int(choice[0])
        if choice == 0:
            raise AttributeError

        #####* Confirmation #####
        while True:
            cur.execute(rf"select Name from {t} where IndexNo={choice}")
            name = cur.fetchall()[0][0]
            conf = confirm(
                f"Are you sure you want to delete the entry for {name}?",
                style=minimalStyle,
            ).ask()
            if conf:
                cur.execute(rf"delete from {t} where IndexNo={choice}")
                conn.commit()
                ###? Setting Proper Index Numbers ###
                cur.execute(rf"select Name from {t}")
                names = cur.fetchall()
                for _ in names:
                    Names.append(_[0])
                for index, val in enumerate(Names):
                    cur.execute(
                        rf"update {t} set IndexNo={index + 1} where Name='{val}'"
                    )
                conn.commit()
                ###? Confirmation ###
                print(f"The entry for {name} has been successfully deleted!")
                cont().ask()
                break
            elif conf is False:
                break
    except AttributeError:
        PrintOptions()


######? Copying Entry ######
def CopyEntry(t):
    try:
        #####* Variables #####
        result = []
        options = []

        #####* Going Through Table #####
        cur.execute(rf"select * from {t}")
        res = cur.fetchall()
        for _ in res:
            result.append(_)

        #####* Printing Options #####
        ###? Clearing the Screen ###

        ###? Options ###
        for i in result:
            options.append(f"{i[0]}. {i[1]}".title())
        options.append("0. Back")
        choice = select(
            "Which entry do you want to copy?", options, style=minimalStyle
        ).ask()
        choice = int(choice[0])
        if choice == 0:
            raise AttributeError

        #####* Copying to Clipboard #####
        ###? Getting Name ###
        cur.execute(rf"select Name from {t} where IndexNo={choice}")
        name = cur.fetchall()[0][0]
        while True:
            ###? Getting What User Wants to Copy to Clipboard ###
            conf = select(
                "What do you want to copy?",
                ["Email", "Username", "Password"],
                style=minimalStyle,
            ).ask()
            ###? Email ###
            if conf == "Email":
                cur.execute(rf"select Email from {t} where IndexNo={choice}")
                result = cur.fetchall()[0][0]
                if result == "":
                    print(f"The email in {name} does not exist.")
                    continue
                pyperclip.copy(result)
                sleep(1)
                print("The email has been successfully copied to your clipboard!")
                sleep(0.5)
                cont().ask()
                break

            ###? Username ###
            elif conf == "Username":
                cur.execute(rf"select Username from {t} where IndexNo={choice}")
                result = cur.fetchall()[0][0]
                if result == "":
                    print(f"The Username in {name} does not exist.")
                    continue
                pyperclip.copy(result)
                sleep(1)
                print("The username has been successfully copied to your clipboard!")
                sleep(0.5)
                cont().ask()
                break

            ###? Password ###
            elif conf == "Password":
                cur.execute(rf"select Password from {t} where IndexNo={choice}")
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
                cont().ask()
                break
    except AttributeError:
        PrintOptions()
    except InvalidToken:
        sleep(1)
        print("Please enter the correct encryption key.")
        cont().ask()


######? Printing Options ######
def PrintOptions():
    while True:
        global minimalStyle

        ####* Clearing the Screen ####
        ####* Printing Options ####
        choice = select(
            "What is your choice?",
            ["Add Entry", "Edit Entry", "Delete Entry", "Copy Entry", "Quit"],
            style=minimalStyle,
        ).ask()

        #######? Calling Functions #######
        if choice == "Quit":
            system("clear" if OSName == "posix" else "cls")
            quit()
        elif choice == "Add Entry":
            AddEntry(table)
        elif choice == "Edit Entry":
            EditEntry(table)
        elif choice == "Delete Entry":
            DelEntry(table)
        elif choice == "Copy Entry":
            CopyEntry(table)


###################! Connecting To SQL ###################
if __name__ == "__main__":
    #####* Encryption #####
    encryption()

    #####* Printing Options #####
    PrintOptions()
