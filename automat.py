import os
import lexer as lex
from sim import *
import sys
import re
import platform
from codegen_VM import *
import time

def run_test_cases(dir_path):
    while True:
        sys.stdout = sys.__stdout__
        command = input("Enter command : ")
        startTime = time.time()
        passCount = 0
        failCount = 0
        match command:
            case "all": # 41 cases, without bytecode->220s, with bytecode-> 160s
                dir = giveFilesWithFolders(dir_path)
                print("Total test cases: ", len(dir))
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
                        try:
                            if stack_VM_On:
                                # compile code
                                # c = Compiler(p)
                                # v = VM()
                                # c = codegen(c)
                                # # print_bytecode(c)
                                # v.load(c)
                                # # then execute
                                # v.execute()
                                # sys.stdout = sys.__stdout__
                                ############################################# uncomment either above or below
                                # execute code
                                e = Executor(p)
                                codegen(e)
                            else:    

                                i = Interpreter(p)
                                # print(eval(i))
                                eval(i)
                        except:
                            pass
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
                                    
                            print(" [92mTest passed:"  + file+"[0m")
                            passCount += 1
                        else:
                            print(" [91mTest failed:"  + file+"[0m")
                            failCount += 1
                        # output = os.popen('').read()
                        # for line in lines[1:]:
                        #     print(line)
                # continue
                print("Passed Count:", passCount, "Failed Count:", failCount)
                print("Time taken: ", time.time()-startTime)


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
                                try:
                                    if stack_VM_On:
                                        # compile code
                                        # c = Compiler(p)
                                        # v = VM()
                                        # c = codegen(c)
                                        # # print_bytecode(c)
                                        # v.load(c)
                                        # # then execute
                                        # v.execute()
                                        # sys.stdout = sys.__stdout__
                                        ############################################# uncomment either above or below
                                        # execute code
                                        e = Executor(p)
                                        codegen(e)
                                    else:    

                                        i = Interpreter(p)
                                        # print(eval(i))
                                        eval(i)
                                except:
                                    pass
                                sys.stdout = sys.__stdout__

                                # if platform.platform().startswith('Windows'):
                                #     output = os.popen('fc eval.txt solution.txt').read()
                                # else:
                                #     output = os.popen('diff eval.txt solution.txt').read()

                               
                                # print(output)
                                # if output == "":
                                if open('eval.txt').read() == open('solution.txt').read():
                                    
                                    print(" [92mTest passed:"  + file+"[0m")
                                    passCount += 1
                                else:
                                    print(" [91mTest failed:"  + file+"[0m")
                                    failCount += 1
                                
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
                                try:
                                    if stack_VM_On:
                                        # compile code
                                        # c = Compiler(p)
                                        # v = VM()
                                        # c = codegen(c)
                                        # # print_bytecode(c)
                                        # v.load(c)
                                        # # then execute
                                        # v.execute()
                                        # sys.stdout = sys.__stdout__
                                        ############################################# uncomment either above or below
                                        # execute code
                                        e = Executor(p)
                                        codegen(e)
                                    else:    

                                        i = Interpreter(p)
                                        # print(eval(i))
                                        eval(i)
                                except:
                                    pass
                                sys.stdout = sys.__stdout__
                                # if platform.platform().startswith('Windows'):
                                #     output = os.popen('fc eval.txt solution.txt').read()
                                # else:
                                #     output = os.popen('diff eval.txt solution.txt').read()


                                # print(output)
                                # if output == "":
                                if open('eval.txt').read() == open('solution.txt').read():
                                    
                                    print(" [92mTest passed:"  + file+"[0m")
                                    passCount += 1
                                else:
                                    print(" [91mTest failed:"  + file+"[0m")
                                    failCount += 1
                        if flag == 1:
                            print("File or Folder not found")
                    print("Passed Count:", passCount, "Failed Count:", failCount)
                    print("Time taken: ", time.time()-startTime)

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
