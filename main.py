import subprocess
from tt import BooleanExpression, to_primitives


# Function to print information
def printInfo():
    print("\t\t\tCMOS Circuit Generator")

    print("-" * 70)

    print("Available operators: and, iff, impl, nand, nor, not, nxor, or, xnor, xor")
    print("(You can use parentheses for indicating precedence)\n")
    print("Example: A and B or not C xor D")

    print("-" * 70, end="\n")


def getInput():
    # Get boolean expression string
    be = str(input("Enter a boolean expression: "))

    # Check if the string contains something other than alphabets
    tempBoolExpr = be.split()
    for item in tempBoolExpr:
        if not item.isalpha():
            print("Error: Expression has an unknown operator")
            exit(0)

    # Check if the string is a valid Boolean Expression
    try:
        expr = to_primitives(BooleanExpression(be))
    except:
        print("Error: Not a valid boolean expression")
        exit(0)

    return expr


# Function to print layout of NOT gate
def NOT(a, count):
    p1 = f"p {a} vdd out_{count} 2 4\n"
    n1 = f"n {a} gnd out_{count} 2 4\n"

    return p1 + n1


# Function to print layout of AND gate
def AND(a, b, count):
    inter = f"{a}_nand_{b}"
    p1 = f"p {a} vdd nand_{count} 2 4\n"
    p2 = f"p {b} vdd nand_{count} 2 4\n"
    n1 = f"n {a} nand_{count} {inter} 2 4\n"
    n2 = f"n {b} {inter} gnd 2 4\n\n"
    inv = NOT(f"nand_{count}", count)

    return p1 + p2 + n1 + n2 + inv


# Function to print layout of OR gate
def OR(a, b, count):
    inter = f"{a}_nor_{b}"
    p1 = f"p {a} vdd {inter} 2 4\n"
    p2 = f"p {b} {inter} nor_{count} 2 4\n"
    n1 = f"n {a} nor_{count} gnd 2 4\n"
    n2 = f"n {b} nor_{count} gnd 2 4\n\n"
    inv = NOT(f"nor_{count}", count)

    return p1 + p2 + n1 + n2 + inv


# Function to write the content to either stdout or a file
def createCMOS(expr, op=False, fileName=None):
    # Initialization
    count = 0
    tempExpr = []

    # Write information about the circuit to the file
    if op:
        fp = open(fileName, "w")
        fp.write("|units: 100 tech: scmos\n"
                 "|\n"
                 "|type gate source drain length width\n"
                 "|---- ---- ------ ----- ------ -----\n\n")
    else:
        print("\n\nSim file content\n")

    # Convert the given boolean expression to a postix representation
    # and parse that to create the sim file content
    expr = expr.postfix_tokens
    for i in range(len(expr)):
        if(expr[i] == 'and'):
            if op:
                fp.write(AND(tempExpr.pop(-1), tempExpr.pop(-1), count))
            else:
                print(AND(tempExpr.pop(-1), tempExpr.pop(-1), count))
            tempExpr.append("out_"+str(count))
            count += 1
        elif(expr[i] == 'not'):
            if op:
                fp.write(NOT(tempExpr.pop(-1), count))
            else:
                print(NOT(tempExpr.pop(-1), count))
            tempExpr.append("out_"+str(count))
            count += 1
        elif(expr[i] == 'or'):
            if op:
                fp.write(OR(tempExpr.pop(-1), tempExpr.pop(-1), count))
            else:
                print(OR(tempExpr.pop(-1), tempExpr.pop(-1), count))
            tempExpr.append("out_"+str(count))
            count += 1
        else:
            tempExpr.append(expr[i])
    if op:
        fp.close()
        print("Export finished")

    return count


if __name__ == "__main__":
    # Print initial information
    printInfo()

    # Get the boolean expression from the user
    expr = getInput()

    # Ask the user if they want to create .sim file
    count = 0
    fileName = None
    if str(input("Do you want to export it to a file? (Y/N) ")).lower() == "y":
        fileName = str(input("Enter the filename: "))
        if ".sim" not in fileName:
            fileName += ".sim"
        count = createCMOS(expr, True, fileName)
    else:
        count = createCMOS(expr)

    print("-" * 70, end="\n")

    # Print the data used in generating the cmos circuit
    print("Input terminals:", *expr.symbols)
    print(f"Output terminal: out_{count - 1}")

    print("-" * 70, end="\n")

    # Ask if the user wants to simulate the circuit in irsim
    if fileName != None:
        if str(input("Do you want to simulate in Irsim? (Y/N) ")).lower() == "y":
            # Irsim simulation through subprocess
            print("Opening Irsim...")
            subprocess.call([f"irsim scmos100.prm {fileName}"], shell=True)
