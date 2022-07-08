from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render

from bank_manager.forms import DepositWithdrawForm, LoginForm, RegisterForm, TransformForm
from bank_manager.connector import *     #logic to retrive/insert data to and from the table

LOGGED_IN = False    
CURRENT_USER = None

def index(request):
    return render(request, "index.html", {'CURRENT_USER': CURRENT_USER})


def register(request):
    global LOGGED_IN
    global CURRENT_USER
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['confirm_password']
            
            if not get_user_pk(email) and password==password2:
                create_user(name, email, phone, password)
                LOGGED_IN = True
                user_pk = get_user_pk(email)
                CURRENT_USER = user_pk
                return HttpResponseRedirect(f"/dashboard/{user_pk}/")
            else:
                messages.error(request, 'Registration Failed. Try again')
                return HttpResponseRedirect("/register/")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form,
                                             'CURRENT_USER': CURRENT_USER})


def login(request):
    global LOGGED_IN
    global CURRENT_USER
    
    if not LOGGED_IN:
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                
                if authenticate_user(email, password):
                    LOGGED_IN = True
                    user_pk = get_user_pk(email)
                    CURRENT_USER = user_pk
                    return HttpResponseRedirect(f"/dashboard/{user_pk}/")
                else:
                    messages.error(request, 'Log In Failed')
                    return HttpResponseRedirect("/login/")
        else:
            form = LoginForm()
    else:
        LOGGED_IN = False
        return HttpResponseRedirect("/login/")
    return render(request, 'login.html', {'form': form,
                                          'CURRENT_USER': CURRENT_USER})


def dashboard(request, user_id):
    if LOGGED_IN and CURRENT_USER == user_id:
        details = get_user_details(user_id)
        
        # getting transaction history
        transactions = transaction_history(user_id)
        for transaction in transactions:
            transaction = list(transaction)
            transaction[2] = abs(transaction[2])
            if transaction[1] == 'wtd':
                transaction[1] = 'Withdrawal'
            elif transaction[1] == 'dep':
                transaction[1] == 'Deposit'
        deposits = []
        withdrawals = []
        for transaction in transactions:
            if transaction[1] == 'Deposit': # deposits are stored as 'dep' in the table
                transaction = (transaction[0], transaction[2])
                deposits.append(transaction)
            elif transaction[1] == 'Withdraw': # withdrawals are stored as 'wth' in the table
                transaction = (transaction[0], transaction[2])
                withdrawals.append(transaction)
        
        # getting transfer history
        sent = transfer_history(user_id, 'send')
        received = transfer_history(user_id, 'receive')
        if sent:
            for transfer in sent:
                transfer[1] = get_user_details(transfer[1])[2] # changing receiver value from id to email
            sent = sent[::-1]
        if received:
            for transfer in received:
                transfer[1] = get_user_details(transfer[1])[2] # changing receiver value from id to email
            received = received[::-1]
        
        return render(request, "dashboard.html", {
            'CURRENT_USER': CURRENT_USER,
            'balance': details[6],
            'user_name': details[1],
            'email': details[2],
            'reg_date': details[3],
            'details': details,
            'transactions': transactions[::-1],
            'sent': sent,
            'received': received,
            'deposits': deposits[::-1],
            'withdrawals': withdrawals[::-1]
            
        })
    else:
        return HttpResponseRedirect("/login/")


def deposit(request, user_id):
    if LOGGED_IN and CURRENT_USER == user_id:
        if request.method == 'POST':
            form = DepositWithdrawForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                deposit_withdraw_amt(amount, user_id)
                insert_transaction(amount, user_id)
                messages.success(request, f"Successfully deposited {amount}")
                return HttpResponseRedirect(f"/dashboard/{user_id}/")
        else:
            form = DepositWithdrawForm()
        return render(request, "deposit.html", {'form': form,
                                                'CURRENT_USER': CURRENT_USER})
    else:
        return HttpResponseRedirect("/login/")
    

def withdraw(request, user_id):
    if LOGGED_IN and CURRENT_USER == user_id:
        if request.method == 'POST':
            form = DepositWithdrawForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                if amount < get_balance(user_id):
                    deposit_withdraw_amt(-amount, user_id) # amount will be subtracted from balance
                    insert_transaction(-amount, user_id)
                    messages.success(request, f"Successfully withdrew {amount}")
                    return HttpResponseRedirect(f"/dashboard/{user_id}/")
                else:
                    messages.error(request, 'Not enough balance')
                    return HttpResponseRedirect(f"/dashboard/{user_id}/withdraw")
        else:
            form = DepositWithdrawForm()
        return render(request, "withdraw.html", {'form': form,
                                                 'CURRENT_USER': CURRENT_USER})
    else:
        return HttpResponseRedirect("/login/")
    
 
def transfer(request, user_id):
    if LOGGED_IN and CURRENT_USER == user_id:
        if request.method == 'POST':
            form = TransformForm(request.POST)
            if form.is_valid():
                receiver_email = form.cleaned_data['send_to']
                amount = form.cleaned_data['amount']
                
                if get_user_pk(receiver_email):
                    receiver_id = get_user_pk(receiver_email)
                    if amount < get_balance(user_id):
                        sender_details = get_user_details(user_id)
                        transfer_amt(user_id, receiver_id, amount)
                        messages.success(request, f'Amount transfered to {receiver_email}')
                        return HttpResponseRedirect(f"/dashboard/{user_id}/")
                    else:
                        messages.error(request, 'Not enough balance')
                else:
                    messages.error(request, 'email not found')
        else:
            form = TransformForm()
        return render(request, "transfer.html", {'form': form,
                                                 'CURRENT_USER': CURRENT_USER})
    else:
        return HttpResponseRedirect("/login/")


def logout(request):
    global LOGGED_IN
    global CURRENT_USER
    
    if CURRENT_USER and LOGGED_IN:
        LOGGED_IN = False
        CURRENT_USER = None
        messages.success(request, "Logged Out Successfully")
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/login/")