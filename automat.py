import os
import lexer as lex
from sim import *
import sys
import re
import platform

def run_test_cases(dir_path):
    while True:
        sys.stdout = sys.__stdout__
        command = input("Enter command : ")
        match command:
            case "all":
                dir = giveFilesWithFolders(dir_path)
                # for file in os.listdir(dir_path):
                for file in dir:
                    if file.endswith(".txt"):

                        # print("Running test case: " + file)
                        # with open(os.path.join(dir_path, file)) as f:
                        with open(file) as f:
                            text = f.read()
                        text = "BEGIN "+text+" END"
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
                        # if platform.platform().startswith('Windows'):
                        #     output = os.popen('fc eval.txt solution.txt').read()
                        # else:
                        #     output = os.popen('diff eval.txt solution.txt').read()
                        # print(output, len(output))

                        # print(output)
                        # if output == "":
                        # compare two text files

                        if open('eval.txt').read() == open('solution.txt').read():
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
                    dir = giveFilesWithFolders(dir_path)
                    # with open(os.path.join(dir_path, default)) as f:
                    flag = 1
                    # if re.search(".", default) != None:
                    if default.find(".")>=0:
                        # print("e111")
                        
                        for file in dir:
                            if file.endswith(default):
                                flag = 0
                                with open(file) as f:
                                    text = f.read()
                                text = "BEGIN "+text+" END"
                                l = lex.Lexer(text)
                                p = prs.Parser(l)
                                i = Interpreter(p)
                                eval(i)
                                sys.stdout = sys.__stdout__

                                # if platform.platform().startswith('Windows'):
                                #     output = os.popen('fc eval.txt solution.txt').read()
                                # else:
                                #     output = os.popen('diff eval.txt solution.txt').read()

                               
                                # print(output)
                                # if output == "":
                                if open('eval.txt').read() == open('solution.txt').read():
                                    print("Test passed: " + file)
                                else:
                                    print("Test failed: " + file)
                        if flag == 1:
                            print("File or Folder not found")

                    else:
                        # print("f222")
                        # run all files in folder
                        for file in dir:
                            # print(default)

                            if file.startswith(default) or (file.find(default+"\\")>=0):
                                # print("entering")
                                flag = 0
                                with open(file) as f:
                                    text = f.read()

                                text = "BEGIN "+text+" END"
                                l = lex.Lexer(text)   
                                p = prs.Parser(l)
                                i = Interpreter(p)
                                eval(i)
                                sys.stdout = sys.__stdout__
                                # if platform.platform().startswith('Windows'):
                                #     output = os.popen('fc eval.txt solution.txt').read()
                                # else:
                                #     output = os.popen('diff eval.txt solution.txt').read()


                                # print(output)
                                # if output == "":
                                if open('eval.txt').read() == open('solution.txt').read():
                                    print("Test passed: " + file)
                                else:
                                    print("Test failed: " + file)
                        if flag == 1:
                            print("File or Folder not found")

                except:
                    print("File or Folder not found")
                    # if f == None:
                    #     print("File not found")
                    #     continue

def giveFilesWithFolders(dir_path):
    files = []
    for file in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, file)):
            
            # files.append(file)
            files.extend(giveFilesWithFolders(os.path.join(dir_path, file)))
        else:
            files.append(dir_path+"\\"+file)
    return files
 

if __name__ == "__main__":
    # start = time.time()
    # run_test_cases("test_cases")
    dir = os.listdir("test_cases")
    dir.append("")
    print(dir)
    dir = giveFilesWithFolders("test_cases")
    print(dir)
    # default = input("Enter folder")
    # for i in dir:
    #     x = re.search(".", i)
        
    #     print(i.startswith(default) or (i.find(default+"\\")>=0))

    run_test_cases("test_cases")
        # print("hi")
        # print(x)
        # if not x:
            # print("hi")
            # run_test_cases("test_cases/" + i)
    # print("Time taken", time.time()-start)


# import platform

# print(platform.platform())


# code to write in file
