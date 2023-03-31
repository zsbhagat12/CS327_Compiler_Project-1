import os
import lexer as lex
from sim import *
import sys
import re

def run_test_cases(dir_path):
    while True:
        sys.stdout = sys.__stdout__
        command = input("Enter command : ")
        match command:
            case "all":
                for file in os.listdir(dir_path):
                    if file.endswith(".txt"):

                        # print("Running test case: " + file)
                        with open(os.path.join(dir_path, file)) as f:
                            text = f.read()
                            l = lex.Lexer(text)   
                            p = prs.Parser(l)
                            i = Interpreter(p)
                            eval(i)
                        sys.stdout = sys.__stdout__


                        # with open('tempt2.txt', 'r') as f:
                        #     print(f.read())

                        # print('------------------------')

                        # with open(os.path.join(dir_path, 'tempt.txt')) as f:
                        #     print(f.read())
        
                        output = os.popen('diff tempt.txt tempt2.txt').read()

                        # print(output)
                        if output == "":
                            print("Test passed: " + file)
                        else:
                            print("Test failed: " + file)
                        # output = os.popen('').read()
                        # for line in lines[1:]:
                        #     print(line)
                # continue

            case "exit":
                break
            case default:
                try:
                    with open(os.path.join(dir_path, default)) as f:
                        text = f.read()
                    l = lex.Lexer(text)   
                    p = prs.Parser(l)
                    i = Interpreter(p)
                    eval(i)
                    sys.stdout = sys.__stdout__
                    output = os.popen('diff tempt.txt tempt2.txt').read()

                    # print(output)
                    if output == "":
                        print("Test passed: " + file)
                    else:
                        print("Test failed: " + file)

                except:
                    print("File not found")
                    # if f == None:
                    #     print("File not found")
                    #     continue



if __name__ == "__main__":
    # start = time.time()
    run_test_cases("test_cases")
    dir = os.listdir("test_cases")
    print(dir)
    for i in dir:
        x = re.search(".", i)
        print("hi")
        if not x:
            print("hi")
            run_test_cases("test_cases/" + i)
    # print("Time taken", time.time()-start)


# import platform

# print(platform.platform())


# code to write in file
