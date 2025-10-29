# password_strength.py

def check_password(password):
    if len(password) < 8:
        return "Too short"
    elif password.isalpha():
        return "Only letters - weak"
    elif password.isdigit():
        return "Only numbers - weak"
    else:
        return "Looks okay!"

user_input = input("Enter a password to check: ")
result = check_password(user_input)
print("Password strength:", result)
