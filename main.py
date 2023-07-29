##
###################! Imports ###################
# ? String -> For Generating Password
import string

# ? OS -> For Running Commands
from os import name as OSName, system

# ? Random -> For Generating Password
from random import choice as randchoice

# ? Time -> For Pausing the Script
from time import sleep

# ? SQLite3 -> For Connecting to MySQL
from sqlite3 import connect

# ? Pyperclip -> For Copying to Clipboard
import pyperclip

# ? Cryptography -> For encrpytion
from cryptography.fernet import Fernet

# ? Questionary -> For better command line interface
from questionary import Style, password, select, text, confirm, checkbox

# ? Rich --> For a box and loading bar
from rich import print
from rich.console import Console

from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
)


###################! Functions ###################
######? Connecting to SQLite3 #####
def conSQL():
    global conn, cur, table
    conn = connect("Manager.db")
    cur = conn.cursor()
    #####* Checking if table exists
    table = "passwords"
    cur.execute(
        rf"Create table if not exists {table}(IndexNo int, Name varchar(244), Email varchar(244), Username varchar(244), Password varchar(244))"
    )


######? Encryption #####
def encryption():
    global fernet

    #####* Clearing The Screen #####
    ClearScreen()

    while True:
        inp = confirm("Do you have an encryption key?").ask()
        if inp:
            key = password("Enter the key:").ask()
        elif inp == False:
            while True:
                GenKey = confirm(
                    "Do you want to generate a key?\n[You will lose access to previous data]"
                ).ask()
                if GenKey == False:
                    exit()
                elif GenKey:
                    key = Fernet.generate_key()
                    key = key.decode("utf-8")
                    print(
                        f"Given below is the key, you will not get access to it again.\n{key}"
                    )
                    while True:
                        copyKey = confirm("Do you want to copy the key?").ask()
                        if copyKey:
                            pyperclip.copy(key)
                            break
                        if copyKey == False:
                            break
                    break
                else:
                    continue
        fernet = Fernet(key)
        break


######? Clear Screen #####
def ClearScreen():
    console = Console()
    system("clear" if OSName == "posix" else "cls")
    console.print(Panel.fit("[bold italic #77DDD4]Password Manager", padding=(0, 22)))


######? Loading bar ######
def StatBar(time: float, desc: str):
    progress_bar = Progress(
        TextColumn(f"{desc} "),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    )
    with progress_bar as p:
        for i in p.track(range(100), description=desc):
            sleep(time / 100)
    sleep(0.5)


######? Generating Passwords ######
def GenPass(p):
    genop = ""
    while True:
        gen = confirm("Do you want to generate a password?").ask()
        if gen:
            while True:
                try:
                    genlen = int(text("How long should the password be?").ask())
                    if genlen <= 0:
                        raise ValueError
                    break
                except:
                    print("Please enter a valid positive number.")
            for _ in range(genlen):
                genop += randchoice(
                    string.ascii_letters + string.digits + string.punctuation
                )

            ClearScreen()
            print(f"Generated Password: {genop}")
            return genop
        elif gen == False:
            return password(p).ask()
        else:
            print("Please only enter either yes or no.")


######? Adding Entry ######
def AddEntry(t):
    #####* Variables #####
    result = []
    NameResult = []

    #####* Clearing the Screen #####
    ClearScreen()

    #####* Going Through Table #####
    cur.execute(rf"select * from {t}")
    res = cur.fetchall()
    for _ in res:
        result.append(_)
    cur.execute(rf"select Name from {t}")
    res = cur.fetchall()
    if len(res) != 0:
        for _ in res:
            _ = _[0].lower()
            NameResult.append(_)

    #####* Getting Values #####
    while True:
        name = text("What do you want the entry to be called?").ask()
        if name == "":
            print("Name cannot be left empty.")
            continue
        if name.lower() in NameResult:
            print("That name already exists.")
            continue
        break
    email = text("Enter Email ID [Optional]:").ask()
    usrname = text("Enter Username [Optional]:")
    passwd = GenPass("Enter Password:")
    passwd = fernet.encrypt(passwd.encode())

    #####* Adding Values to Table #####
    cur.execute(
        rf'insert into {t} values({len(result) + 1}, "{name}", "{email}", "{usrname}", "{passwd}")'
    )
    conn.commit()
    print(f"Entry for {name} has been successfully added!")
    input("Please enter to continue...")


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
        ClearScreen()

        ###? Options ###
        for i in result:
            options.append(f"{i[0]}. {i[1]}".title())
        options.append("0. Back")
        choice = select("Which entry do you want to edit?", options).ask()
        choice = int(choice[0])
        if choice == 0:
            raise AttributeError

        #####* Getting Values #####
        opt = checkbox("What all do you want to edit?", ["Name", "Email", "Username", "Password"]).ask()
        ###? Name ###
        if "Name" in opt:
            while True:
                Name = text("What should the name be?").ask()
                if Name == "":
                    print("Name cannot be left empty.")
                    continue
                cur.execute(rf"update {t} set Name='{Name}' where IndexNo={choice}")
                break
        ###? Email ###
        if "Email" in opt:
            Email = text("What should the email be?").ask()
            cur.execute(
                rf"update {t} set Email='{Email}' where IndexNo={choice}"
            )
        ###? Username ###
        if "Username" in opt:
            Username = text("What should the username be?").ask()
            cur.execute(
                rf"update {t} set Username='{Username}' where IndexNo={choice}"
            )
        ###? Password ###
        if "Password" in opt:
            Passwd = GenPass("What should the password be?")
            Passwd = fernet.encrypt(Passwd.encode())
            cur.execute(
                rf'update {t} set Password="{Passwd}" where IndexNo={choice}'
            )
        if Name == "-" and Email == "-" and Username == "-" and Passwd == "-":
            print("The entry has not been modified.")
        else:
            conn.commit()
            print("The entry has been successfully modified!")
        input("Please enter to continue...")
    except AttributeError:
        PrintOptions()
    except:
        sleep(1)
        print("There has been some unknown error causing the program to crash.")
        sleep(0.5)
        input("Please enter to continue...")


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
        ClearScreen()

        ###? Options ###
        for i in result:
            options.append(f"{i[0]}. {i[1]}".title())
        options.append("0. Back")
        choice = select("Which entry do you want to edit?", options).ask()
        choice = int(choice[0])
        if choice == 0:
            raise AttributeError

        #####* Confirmation #####
        while True:
            cur.execute(rf"select Name from {t} where IndexNo={choice}")
            name = cur.fetchall()[0][0]
            conf = confirm(
                f"Are you sure you want to delete the entry for {name}?"
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
                sleep(1)
                break
            elif conf == False:
                break
    except AttributeError:
        PrintOptions()
    except:
        sleep(1)
        print("There has been some unknown error causing the program to crash.")
        sleep(0.5)
        input("Please enter to continue...")


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
        ClearScreen()

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
            conf = (
                select(
                    "What do you want to copy?",
                    ["Email", "Username", "Password"],
                )
                .ask()
            )
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
                input("Please enter to continue...")
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
                input("Please enter to continue...")
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
                input("Please enter to continue...")
                break
    except AttributeError:
        PrintOptions()
    except:
        sleep(1)
        print("Please enter the correct encryption key.")
        sleep(0.5)
        input("Please enter to continue...")


######? Printing Options ######
def PrintOptions():
    while True:
        global minimalStyle

        #####* For Questionary Style #####
        minimalStyle = Style(
            [
                ("answer", "fg:#FFFFFF italic"),  # ? White
                ("question", "fg:#FFFFFF bold"),  # ? White
                ("pointer", "fg:#00FFFF bold"),  # ? Cyan
                ("highlighted", "fg:#FFFFFF"),  # ? White
                ("selected", "fg:#A9A9A9"),  # ? Grey
                ("qmark", "fg:#77DD77"),  # ? Green
            ]
        )

        ####* Clearing the Screen ####
        ClearScreen()
        ####* Printing Options ####
        choice = select(
            "What is your choice?",
            ["Add Entry", "Edit Entry", "Delete Entry", "Copy Entry", "Quit"],
        ).ask()

        #######? Calling Functions #######
        if choice == "Quit":
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
    #####* Clearing the Screen #####
    ClearScreen()

    #####* Loading bar #####
    StatBar(2, desc="[cyan]Loading Password Manager")

    #####* Encryption #####
    encryption()

    #####* Connecting To SQLite3 #####
    conSQL()

    #####* Printing Options #####
    PrintOptions()
