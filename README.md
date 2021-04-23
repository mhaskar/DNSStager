# What is DNSStager?

DNSStager is an open-source project based on Python used to hide and transfer your payload using DNS protocol.

DNSStager will create a malicious DNS server that handles DNS requests to your domain and return your payload as a response to specific records such as `AAAA` or `TXT` records after splitting it into chunks and encode the payload using different algorithms.

DNSStager can generate a custom agent written in `C` or `GoLang` that will resolve a sequence of domains, retrieve the payload, decode it and finally inject it into the memory based on any technique you want.

Based on your DNS resolving option, DNSStager will save a chunk of the payload into that record, so for example, if you choose `IPV6` as an option to retrieve the payload, the DNS response will be like the following:


`cloud-srv-1.test.mydnsserver.live. 300 IN AAAA	5648:31d2:6548:8b52:6048:8b52:1848:8b52`

Where `5648:31d2:6548:8b52:6048:8b52:1848:8b52` is a part of your payload.

So, the agent will resolve some domains to retrieve the payload and then decode it and finally inject it into memory.
