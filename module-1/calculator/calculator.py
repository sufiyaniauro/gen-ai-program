class Calculator:
    def __init__(self):
        self.history = []
        
    def add(self, a, b):
        """Addition operation"""
        return a + b
        
    def subtract(self, a, b):
        """Subtraction operation"""
        return a - b
        
    def multiply(self, a, b):
        """Multiplication operation"""
        return a * b
        
    def divide(self, a, b):
        """Division operation"""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
        
    def power(self, a, b):
        """Exponential operation"""
        return a ** b
        
    def modulo(self, a, b):
        """Modulo operation"""
        if b == 0:
            raise ZeroDivisionError("Cannot find modulo with zero")
        return a % b
    
    def floor_divide(self, a, b):
        """Floor division operation"""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a // b
        
    def logical_and(self, a, b):
        """Logical AND operation"""
        return a and b
        
    def logical_or(self, a, b):
        """Logical OR operation"""
        return a or b
        
    def logical_not(self, a):
        """Logical NOT operation"""
        return not a
        
    def logical_xor(self, a, b):
        """Logical XOR operation"""
        return bool(a) != bool(b)
    
    def bitwise_and(self, a, b):
        """Bitwise AND operation"""
        if not all(isinstance(x, int) for x in [a, b]):
            raise TypeError("Bitwise operations require integer operands")
        return a & b
        
    def bitwise_or(self, a, b):
        """Bitwise OR operation"""
        if not all(isinstance(x, int) for x in [a, b]):
            raise TypeError("Bitwise operations require integer operands")
        return a | b
        
    def bitwise_xor(self, a, b):
        """Bitwise XOR operation"""
        if not all(isinstance(x, int) for x in [a, b]):
            raise TypeError("Bitwise operations require integer operands")
        return a ^ b
        
    def bitwise_not(self, a):
        """Bitwise NOT operation"""
        if not isinstance(a, int):
            raise TypeError("Bitwise operations require integer operands")
        return ~a
        
    def left_shift(self, a, b):
        """Left shift operation"""
        if not all(isinstance(x, int) for x in [a, b]):
            raise TypeError("Shift operations require integer operands")
        return a << b
        
    def right_shift(self, a, b):
        """Right shift operation"""
        if not all(isinstance(x, int) for x in [a, b]):
            raise TypeError("Shift operations require integer operands")
        return a >> b
    
    def save_operation(self, operation, inputs, result):
        """Save the operation in history"""
        self.history.append({
            'operation': operation,
            'inputs': inputs,
            'result': result
        })
    
    def get_history(self):
        """Return calculation history"""
        return self.history


def display_menu():
    """Display the calculator menu"""
    print("\n===== CALCULATOR MENU =====")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Exponentiation")
    print("6. Modulo")
    print("7. Floor Division")
    print("8. Logical AND")
    print("9. Logical OR")
    print("10. Logical NOT")
    print("11. Logical XOR")
    print("12. Bitwise AND")
    print("13. Bitwise OR")
    print("14. Bitwise XOR")
    print("15. Bitwise NOT")
    print("16. Left Shift")
    print("17. Right Shift")
    print("18. View History")
    print("0. Exit")
    print("==========================")


def get_numeric_input(prompt_msg):
    """Get numeric input with validation"""
    while True:
        try:
            value = input(prompt_msg)
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            return float(value)
        except ValueError:
            print("Invalid input! Please enter a number.")


def get_int_input(prompt_msg):
    """Get integer input with validation"""
    while True:
        try:
            return int(input(prompt_msg))
        except ValueError:
            print("Invalid input! Please enter an integer.")


def main():
    calc = Calculator()
    result = None
    
    print("Welcome to the Advanced Calculator!")
    
    while True:
        display_menu()
        
        if result is not None:
            print(f"\nPrevious result: {result}")
            print("You can use 'result' as an input for your next calculation.")
        
        try:
            choice = input("\nEnter your choice (0-18): ")
            
            if choice == '0':
                print("Thank you for using the calculator. Goodbye!")
                break
                
            elif choice == '18':
                history = calc.get_history()
                if not history:
                    print("No calculation history available.")
                else:
                    print("\n===== CALCULATION HISTORY =====")
                    for i, entry in enumerate(history, 1):
                        print(f"{i}. {entry['operation']}: {entry['inputs']} = {entry['result']}")
                continue
                
                a = result if result is not None and input(f"Use previous result {result}? (y/n): ").lower() == 'y' else (
                    get_numeric_input("Enter a value: ") if choice == '10' else get_int_input("Enter an integer: ")
                )
                
                if choice == '10':
                    result = calc.logical_not(a)
                    calc.save_operation("Logical NOT", [a], result)
                else:
                    result = calc.bitwise_not(a)
                    calc.save_operation("Bitwise NOT", [a], result)
                    
                print(f"Result: {result}")
                
            elif choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '12', '13', '14', '16', '17']:
                needs_int = choice in ['12', '13', '14', '16', '17']
                
                if result is not None and input(f"Use previous result {result} as first operand? (y/n): ").lower() == 'y':
                    a = result
                else:
                    a = get_int_input("Enter first integer: ") if needs_int else get_numeric_input("Enter first value: ")
                
                b = get_int_input("Enter second integer: ") if needs_int else get_numeric_input("Enter second value: ")
                
                if choice == '1':
                    result = calc.add(a, b)
                    calc.save_operation("Addition", [a, b], result)
                elif choice == '2':
                    result = calc.subtract(a, b)
                    calc.save_operation("Subtraction", [a, b], result)
                elif choice == '3':
                    result = calc.multiply(a, b)
                    calc.save_operation("Multiplication", [a, b], result)
                elif choice == '4':
                    result = calc.divide(a, b)
                    calc.save_operation("Division", [a, b], result)
                elif choice == '5':
                    result = calc.power(a, b)
                    calc.save_operation("Exponentiation", [a, b], result)
                elif choice == '6':
                    result = calc.modulo(a, b)
                    calc.save_operation("Modulo", [a, b], result)
                elif choice == '7':
                    result = calc.floor_divide(a, b)
                    calc.save_operation("Floor Division", [a, b], result)
                elif choice == '8':
                    result = calc.logical_and(a, b)
                    calc.save_operation("Logical AND", [a, b], result)
                elif choice == '9':
                    result = calc.logical_or(a, b)
                    calc.save_operation("Logical OR", [a, b], result)
                elif choice == '11':
                    result = calc.logical_xor(a, b)
                    calc.save_operation("Logical XOR", [a, b], result)
                elif choice == '12':
                    result = calc.bitwise_and(a, b)
                    calc.save_operation("Bitwise AND", [a, b], result)
                elif choice == '13':
                    result = calc.bitwise_or(a, b)
                    calc.save_operation("Bitwise OR", [a, b], result)
                elif choice == '14':
                    result = calc.bitwise_xor(a, b)
                    calc.save_operation("Bitwise XOR", [a, b], result)
                elif choice == '16':
                    result = calc.left_shift(a, b)
                    calc.save_operation("Left Shift", [a, b], result)
                elif choice == '17':
                    result = calc.right_shift(a, b)
                    calc.save_operation("Right Shift", [a, b], result)
                    
                print(f"Result: {result}")
                
            else:
                print("Invalid choice! Please enter a number between 0 and 18.")
                
        except ZeroDivisionError as e:
            print(f"Error: {e}")
            
        except ValueError as e:
            print(f"Error: {e}")
            
        except TypeError as e:
            print(f"Error: {e}")
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

