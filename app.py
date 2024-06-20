# Starting of the program
#! --------------------------------------------------
#! ---------- Credits
#! --------------------------------------------------
# region credits
# * ---- Made by:
# * ------- Aaloke Eppalapalli
# * ------- Husain Khorakiwala

# * ---- Source Code:
# * ------- https://github.com/AverageBlank/URLShortener
# endregion


#! --------------------------------------------------
#! ---------- Imports
#! --------------------------------------------------
# region import
# ? Flask --> For the backend of HTML
from flask import (
    abort,
    flash,
    Flask,
    render_template,
    make_response,
    request,
    redirect,
    url_for,
)

# ? Flask Login --> For the Login Management
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
    current_user,
)


# ? String -> For Generating Password
import string

# ? OS -> For Running Commands
from os import name as OSName, system, environ

# ? Random -> For Generating Password
from random import choice as randChoice, shuffle as randShuffle

# ? Datetime
from datetime import datetime

# ? PymMongo -> For Connecting to MongoDB
from pymongo import MongoClient
from dotenv import load_dotenv

# ? Re --> For checking if characters exist in string
from re import compile

# ? Cryptography -> For encrpytion
from cryptography.fernet import Fernet

# ? Bcrypt --> Hashing passwords
from bcrypt import hashpw, gensalt, checkpw

from time import sleep

# endregion
#! --------------------------------------------------
#! --------------------------------------------------


#! --------------------------------------------------
#! ---------- Running the Program
#! --------------------------------------------------
# region Running the Program
# ? Required
app = Flask(__name__)
app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
domain = ""
hasUsedApp = False

# ? Connecting to the Mongo DB Database
load_dotenv()
mongoLink = environ.get("link")
client = MongoClient(mongoLink)
db = client["PassManager"]

# ? Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

# ? Connecting to Collections
passColl = db["pass"]
usersColl = db["users"]

# ? Create indexes (if needed)
passColl.create_index("Timestamp")
passColl.create_index("Name")
passColl.create_index("Email/Username")
passColl.create_index("Password")
passColl.create_index("UserID")

usersColl.create_index("Username", unique=True)
usersColl.create_index("Password")
usersColl.create_index("UserID", unique=True)
usersColl.create_index("EncryptionKey")
print("Successfully connected to MongoDB.")
# endregion
#! --------------------------------------------------
#! --------------------------------------------------


#! --------------------------------------------------
#! ---------- Functions
#! --------------------------------------------------
# region Functions


# Flask Login Management
class User(UserMixin):
    def __init__(
        self,
        username,
        password,
        _id=None,
    ):
        self.id = _id
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    user_data = usersColl.find_one({"_id": user_id})
    if user_data:
        return User(
            user_data["_id"],
            user_data["Username"],
            user_data["Password"],
        )
    return None


@app.route("/signup", methods=["GET", "POST"])
def register():
    global userID
    if current_user.is_authenticated:
        return redirect("/dashboard")
    else:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            existingUser = usersColl.find_one({"Username": username})
            users = usersColl.distinct("UserID")
            if existingUser:
                return render_template(
                    "signup.html",
                    errorTrue="errorTrue",
                    errorValue="User already exists",
                )
            if len(username) < 1 or username.isdigit() or " " in username:
                return render_template(
                    "signup.html",
                    errorTrue="errorTrue",
                    errorValue="Please enter a valid username",
                )
            for i in username:
                if i in string.punctuation:
                    return render_template(
                        "signup.html",
                        errorTrue="errorTrue",
                        errorValue="Please enter a valid username",
                    )
            if len(password) < 1 or password.isdigit() or " " in password:
                return render_template(
                    "signup.html",
                    errorTrue="errorTrue",
                    errorValue="Please enter a valid password",
                )
            while True:
                userID = []
                for _ in range(10):
                    userID.append(randChoice(string.ascii_letters + string.digits))
                randShuffle(userID)
                userID = "".join(str(v) for v in userID)
                if userID in users:
                    continue
                break
            while True:
                key = Fernet.generate_key()
                key = key.decode("utf-8")
                existingKey = usersColl.find_one({"Key": key})
                if existingKey:
                    continue
                break
            hashed_password = hashpw(password.encode("utf-8"), gensalt())
            usersColl.insert_one(
                {
                    "Username": username,
                    "Password": hashed_password,
                    "UserID": userID,
                    "EncryptionKey": key,
                }
            )
            uid = usersColl.find_one({"Username": username}, {"_id": 1})
            user = User(uid, username, hashed_password)
            login_user(user, remember=True)
            return redirect("/dashboard")
        return render_template(
            "signup.html",
        )


@app.route("/login", methods=["GET", "POST"])
def login():
    print(current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect("/dashboard")
    else:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user_data = usersColl.find_one({"Username": username})

            if user_data:
                passwd = user_data["Password"]
                if checkpw(password.encode("utf-8"), passwd):
                    user = User(
                        user_data["_id"],
                        user_data["Username"],
                        user_data["Password"],
                    )
                    login_user(user, remember=True)
                    sleep(2)
                    return redirect("/dashboard")
                else:
                    return render_template(
                        "login.html",
                        errorTrue="errorTrue",
                        errorValue="Invalid password",
                    )
            else:
                return render_template(
                    "login.html",
                    errorTrue="errorTrue",
                    errorValue="User not found",
                )
        else:
            return render_template("/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/generatePassword", methods=["GET", "POST"])
def genPass():
    if request.method == "POST":
        useGeneratedPassword = request.form.get("useGeneratedPassword")
        if useGeneratedPassword is True:
            generatedPassword = []
            while True:
                val = []
                digit = request.form.get("digitsRequired")
                letters = request.form.get("lettersRequired")
                punc = request.form.get("puncRequired")
                if digit:
                    val += string.digits
                if letters:
                    val += string.ascii_letters
                if punc:
                    val += "[@!_#$%^&*()<>?/}{~:]"
                while True:
                    try:
                        generateLength = request.form.get("generateLength")
                        if 0 <= generateLength <= 50:
                            raise ValueError
                        break
                    except ValueError or TypeError:
                        return render_template(
                            "generatepassword.html",
                            errorTrue="errorTrue",
                            errorValue="Please enter a number between 0 & 50.",
                        )
                while True:
                    for _ in range(generateLength):
                        generatedPassword.append(randChoice(val))

                    if generateLength > 5:
                        regex = compile("[@!_#$%^&*()<>?/}{~:]")
                        if (
                            regex.search("".join(str(v) for v in generatedPassword))
                            is None
                        ):
                            generatedPassword = []
                            continue
                        if any(i.isdigit() for i in generatedPassword) is False:
                            generatedPassword = []
                            continue
                        if any(i.isalpha() for i in generatedPassword) is False:
                            generatedPassword = []
                            continue
                    break

                randShuffle(generatedPassword)
                generatedPassword = "".join(str(v) for v in generatedPassword)

                return render_template(
                    "generatepassword.html",
                    generatedPassword,
                )
    elif useGeneratedPassword is False:
        customPass = request.form.get("CustomPassword")
        if customPass == "None":
            return render_template(
                "generatePassword.html",
                errorTrue="errorTrue",
                errorValue="No Custom Password given",
            )
        else:
            return render_template(
                "generatepassword.html",
                customPass,
            )


def addEntry():
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
    # passwd = genPass()
    # passwd = fernet.encrypt(passwd.encode())  # TODO TO BE FIXED
    passwd = ""  # Aaloke implement.
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")

    #####* Adding Values to Table #####
    values = {
        "Timestamp": time,
        "Name": name,
        "Email/Username": emailUsername,
        "Password": passwd,
        "UserID": userID,
    }
    passColl.insert_one(values)


# def EditEntry(): # TODO FIX
#     try:
#         #####* Variables #####
#         result = []
#         options = []
#         names = []
#         Name = "-"
#         Email = "-"
#         Username = "-"
#         Passwd = "-"

#         #####* Going Through Table #####
#         query = {"UserID": userID}
#         projection = {"_id": 0, "Name": 1}
#         cursor = passColl.find(query, projection)

#         for doc in cursor:
#             names.append(doc["Name"])

#         ###? Options ###
#         for i, j in enumerate(names):
#             options.append(f"{i + 1}. {j[i]}".title())
#         options.append("0. Back")
#         # Aaloke implement option to be edited using "options" list.
#         # by that I mean the list has the statement that is to be printed, so print out the options for the list and ask the user to select one.
#         choice = "1"  # TODO FIX
#         choice = int(choice[0])
#         if choice == 0:
#             raise AttributeError

#     #####* Getting Values ##### # TODO FIX
#     opt = checkbox(
#         "What all do you want to edit?",
#         ["Name", "Email", "Username", "Password"],
#         style=minimalStyle,
#     ).ask()
#     ###? Name ###
#     if "Name" in opt:
#         while True:
#             Name = text("What should the name be?", style=minimalStyle).ask()
#             if Name == "":
#                 print("Name cannot be left empty.")
#                 continue
#             cur.execute(rf"update {t} set Name='{Name}' where IndexNo={choice}")
#             break
#     ###? Email ###
#     if "Email" in opt:
#         Email = text("What should the email be?", style=minimalStyle).ask()
#         cur.execute(rf"update {t} set Email='{Email}' where IndexNo={choice}")
#     ###? Username ###
#     if "Username" in opt:
#         Username = text("What should the username be?", style=minimalStyle).ask()
#         cur.execute(rf"update {t} set Username='{Username}' where IndexNo={choice}")
#     ###? Password ###
#     if "Password" in opt:
#         Passwd = GenPass("What should the password be?")
#         Passwd = fernet.encrypt(Passwd.encode())
#         cur.execute(rf'update {t} set Password="{Passwd}" where IndexNo={choice}')
#     if Name == "-" and Email == "-" and Username == "-" and Passwd == "-":
#         print("The entry has not been modified.")
#     else:
#         conn.commit()
#         print("The entry has been successfully modified!")
#     cont().ask()
# except AttributeError:
#     print("Home")  # Aaloke return homepage


# def DelEntry(t): # TODO FIX
#     try:
#         #####* Variables #####
#         result = []
#         options = []
#         Names = []

#         #####* Going Through Table #####
#         cur.execute(rf"select * from {t}")
#         res = cur.fetchall()
#         for _ in res:
#             result.append(_)

#         #####* Printing Options #####
#         ###? Clearing the Screen ###

#         ###? Options ###
#         for i in result:
#             options.append(f"{i[0]}. {i[1]}".title())
#         options.append("0. Back")
#         choice = select(
#             "Which entry do you want to edit?", options, style=minimalStyle
#         ).ask()
#         choice = int(choice[0])
#         if choice == 0:
#             raise AttributeError

#         #####* Confirmation #####
#         while True:
#             cur.execute(rf"select Name from {t} where IndexNo={choice}")
#             name = cur.fetchall()[0][0]
#             conf = confirm(
#                 f"Are you sure you want to delete the entry for {name}?",
#                 style=minimalStyle,
#             ).ask()
#             if conf:
#                 cur.execute(rf"delete from {t} where IndexNo={choice}")
#                 conn.commit()
#                 ###? Setting Proper Index Numbers ###
#                 cur.execute(rf"select Name from {t}")
#                 names = cur.fetchall()
#                 for _ in names:
#                     Names.append(_[0])
#                 for index, val in enumerate(Names):
#                     cur.execute(
#                         rf"update {t} set IndexNo={index + 1} where Name='{val}'"
#                     )
#                 conn.commit()
#                 ###? Confirmation ###
#                 print(f"The entry for {name} has been successfully deleted!")
#                 cont().ask()
#                 break
#             elif conf is False:
#                 break
#     except AttributeError:
#         PrintOptions()
