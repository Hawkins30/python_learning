age = int(input("Enter your age: "))

if age >= 18 and age < 65:
    print("You're an adult.")
elif age >= 65:
    print("You're a senior.")
else:
    print("You're underage.")
