from dnslib.dns import DNSRecord,DNSQuestion, QTYPE
import socket
from binascii import unhexlify

q = DNSRecord(q=DNSQuestion('check.infinite.thecatch.cz',getattr(QTYPE,'SOA')))
soa = DNSRecord.parse(q.send('8.8.8.8', 53))
print soa.auth[0]
dnsserver = str(soa.auth[0].rdata.mname)

q = DNSRecord(q=DNSQuestion(dnsserver,getattr(QTYPE,'A')))
a = DNSRecord.parse(q.send('8.8.8.8', 53))
print a.rr[0]
dnsserver_ip = str(a.rr[0].rdata)

done = []
code = ''
nsl = 'dustoff.infinite.thecatch.cz'
while True:
    q = DNSRecord(q=DNSQuestion(nsl,getattr(QTYPE,'NS')))
    try:
        a = DNSRecord.parse(q.send(dnsserver_ip, 53, timeout=0.5, tcp=False))
    except socket.timeout:
        continue

    nsl = str(a.auth[0].rdata)
    if nsl in done:
       break
    done.append(nsl)

    if nsl.endswith('.'): nsl = nsl[:-1]
    print nsl

    if nsl.startswith('ns.0x'):
       try:
         s = unhexlify(nsl[5:].split('.',1)[0])
         code += s
         if '\0' in s: 
            print code
            break
       except:
         pass


