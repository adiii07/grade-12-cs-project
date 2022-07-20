import os

import mysql.connector

mydb = mysql.connector.connect(
    # host="sql6.freemysqlhosting.net",
    # user="sql6504581",
    # password=os.environ.get('DB_PASSWORD'),
    # database="sql6504581"
    host = "sql.freedb.tech",
    user = "freedb_aditya",
    password = os.environ.get('DB_PASSWORD'),
    database = "freedb_brs_bank"
)
mycursor = mydb.cursor(buffered=True)


# getting user pk from the user's email
def get_user_pk(email):
    sql = "SELECT pk FROM user WHERE email=%s"
    mycursor.execute(sql, (email, ))
    result = mycursor.fetchone()
    try:
        return result[0]
    except:
        return False

# getting user details from the user's pk
def get_user_details(pk):
    sql = "SELECT * FROM user WHERE pk=%s"
    mycursor.execute(sql, (pk,))
    result = mycursor.fetchone()
    return result


def authenticate_user(form_email, form_pwd):
    sql = "SELECT MD5(%s)"
    mycursor.execute(sql, (form_pwd, ))
    for x in mycursor:
        form_pwd_hash = x[0]
    
    try:
        user_id = get_user_pk(form_email)
        db_pwd = get_user_details(user_id)[4] #geting hashed pwd stored in db
        if form_pwd_hash == db_pwd:
            print("Authenticated")
            return True
        else:
            return False
    except TypeError:
        return False
    

# inserting into user table
def create_user(name, email, phone, password):
    sql = "INSERT INTO user (name, email, phone, password) VALUES (%s, %s, %s, MD5(%s))"
    val = (name, email, phone, password)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")


def get_balance(id):
    sql = "SELECT balance from user WHERE pk=%s"
    mycursor.execute(sql, (id,))
    current_balance = mycursor.fetchone()[0]
    return current_balance

def deposit_withdraw_amt(amount, id):
    current_balance = get_balance(id)
    new_balance = current_balance + amount
    sql = "UPDATE user SET balance=%s WHERE pk=%s"
    val = (new_balance, id)
    mycursor.execute(sql, val)
    mydb.commit()
    

def insert_transaction(amount, id):
    sql = "INSERT INTO transactions (user_id, amount, type) VALUES (%s, %s, %s)"
    if amount > 0:
        val = (id, amount, "dep")
    elif amount < 0:
        val = (id, abs(amount), "wtd")
    mycursor.execute(sql, val)
    mydb.commit()
    print(amount, "added.")

# inserting into transfer table
def transfer_amt(sender_id, receiver_id, amount):
    deposit_withdraw_amt(amount, receiver_id)
    deposit_withdraw_amt(-amount, sender_id)
    
    sql = "INSERT INTO transfers (sender_id, receiver_id, amount) VALUES (%s, %s, %s)"
    val = (sender_id, receiver_id, amount)
    mycursor.execute(sql, val)
    mydb.commit()
    print(amount, "transfered from", sender_id, "to", receiver_id)


def transfer_history(user_id, type):
    history = []
    if type == 'send':
        sql = "SELECT * FROM transfers where sender_id=%s"
        mycursor.execute(sql, (user_id,))
        try:
            for x in mycursor:
                history.append([x[4], x[2], x[3]]) # date, receiver, amount
        except:
            return None
            
    elif type == 'receive':
        sql = "SELECT * FROM transfers where receiver_id=%s"
        mycursor.execute(sql, (user_id,))
        try:
            for x in mycursor:
                history.append([x[4], x[1], x[3]]) # date, receiver, amount
        except:
            return None

    return history

# history of deposits and withdrawals
def transaction_history(user_id):
    sql = "SELECT * FROM transactions WHERE user_id=%s"
    mycursor.execute(sql, (user_id,))
    history = []
    for x in mycursor:
        if x[3] == 'dep':
            history.append((x[4], "Deposit", x[2])) # date, type, amount
        else:
            history.append((x[4], "Withdraw", x[2])) # date, type, amount
    return history