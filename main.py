import subprocess
from tt import BooleanExpression


# Function to print information
def info():
    print("\t\t\tCMOS Circuit Generator")
    print("-" * 70)
    print("Available operators: & => AND, | => OR, ! => NOT")
    print("(You can use parentheses for indicating precedence)\n")
    print("Example: A&B|!C")
    print("-" * 70, end="\n")


# Function to print layout of NOT gate
def NOT(input, count):
    p1 = f"p {input} vdd out_{count} 2 4\n"
    n1 = f"n {input} gnd out_{count} 2 4\n"

    return p1 + n1


# Function to print layout of AND gate
def AND(a, b, count):
    inter = f"{a}_nand_{b}_int"
    p1 = f"p {a} vdd nand_{count} 2 4\n"
    p2 = f"p {b} vdd nand_{count} 2 4\n"
    n1 = f"n {a} nand_{count} {inter} 2 4\n"
    n2 = f"n {b} {inter} gnd 2 4\n\n"
    inv = NOT(f"nand_{count}", count)

    return p1 + p2 + n1 + n2 + inv


# Function to print layout of OR gate
def OR(a, b, count):
    inter = f"{a}_nor_{b}_int"
    p1 = f"p {a} vdd {inter} 2 4\n"
    p2 = f"p {b} {inter} nor_{count} 2 4\n"
    n1 = f"n {a} nor_{count} gnd 2 4\n"
    n2 = f"n {b} nor_{count} gnd 2 4\n\n"
    inv = NOT(f"nor_{count}", count)

    return p1 + p2 + n1 + n2 + inv


# Function to write the content to either stdout or a file
def create(expr, op=False, fileName=None):
    # Initialization
    count = 0
    tempExpr = []

    # Write to the file information about the circuit
    if op:
        fp = open(fileName, "w")
        fp.write("|units: 100 tech: scmos\n"
                 "|\n"
                 "|type gate source drain length width\n"
                 "|---- ---- ------ ----- ------ -----\n\n")
    else:
        print("\n\nSim file content\n")

    '''
	Convert the given boolean expression to a postix representation
	and parse that to create the sim file content
	'''
    expr = expr.postfix_tokens
    for i in range(len(expr)):
        if(expr[i] == "&"):
            if op:
                fp.write(AND(tempExpr.pop(-1), tempExpr.pop(-1), count))
            else:
                print(AND(tempExpr.pop(-1), tempExpr.pop(-1), count))
            tempExpr.append("out_"+str(count))
            count += 1
        elif(expr[i] == '!'):
            if op:
                fp.write(NOT(tempExpr.pop(-1), count))
            else:
                print(NOT(tempExpr.pop(-1), count))
            tempExpr.append("out_"+str(count))
            count += 1
        elif(expr[i] == '|'):
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


if __name__ == "__main__":
    # Print information
    info()

    # Get boolean expression string
    be = str(input("Enter a boolean expression: "))

    # Check if it's a valid one
    try:
        expr = BooleanExpression(be)
    except:
        print("Error: Not a valid boolean expression")
        exit(0)

    # Ask the user if they want to create .sim file
    fileName = None
    if str(input("Do you want to export it to a file? (Y/N) ")).lower() == "y":
        fileName = str(input("Enter the filename: "))
        if ".sim" not in fileName:
            fileName += ".sim"
        create(expr, True, fileName)
    else:
        create(expr)

    print("-" * 70, end="\n")

    # Ask if the user wants to simulate directly in program or in irsim
    if fileName != None:
        if str(input("Do you want to simulate in Irsim? (Y/N) ")).lower() == "y":
            # Irsim simulation through subprocess
            print("Opening Irsim...")
            subprocess.call([f"irsim scmos100.prm {fileName}"], shell=True)
