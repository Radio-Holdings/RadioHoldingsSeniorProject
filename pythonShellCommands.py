import os
import subprocess

def main():

    """
    OS library examples
    """
    # print(os.system("ls"))
    # print(os.popen("ls").read())
    # print(os.spawnl(os.P_NOWAIT,"/usr/sh","ls")) # gives the process id
    
    """
    subprocess library examples
    """

    """
    Basic examples with ls command
    """
    result = subprocess.run("ls", stdout= subprocess.PIPE, stderr=subprocess.STDOUT)
    print("result 1:")
    print(result.stdout.decode())
    print("\n")

    """
    if we have to run commands with more than 1 args, we should pass them as an array as shown below
    """
    result2 = subprocess.run(["rm", "xyz"], stdout= subprocess.PIPE, stderr=subprocess.STDOUT)
    print("result 2:")
    print("error is:",result2.stdout.decode())
    print("\n")


    """
    We can pass the commands with more than 1 ards together by shell=True option
    """
    result3 = subprocess.run("rm xyz", shell=True, stdout= subprocess.PIPE, stderr=subprocess.STDOUT)
    print("result 3:")
    print("error is:",result3.stdout.decode())
    print("\n")

    """
    Sets the stdout to pipe and stderror to pipe.
    """
    result4 = subprocess.run("ls", capture_output=True)
    print("result 4:")
    print(result4.stdout.decode())
    print("\n")

if __name__ == "__main__":
    main()
