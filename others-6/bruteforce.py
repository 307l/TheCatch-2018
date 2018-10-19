def trans(a):
    ta = ''
    for i in range(0,8):
        for j in range(0,8):
            ta += a[j*8+i]
    return ta

# template: CT18-XXXX-XXXX-XXXX-XXXX
a = "HBSR-CCR2DC16-6X1FBU-NLWFIPTDHBH-FRLVA7G5SC3T18-V-EA2-CHT-YBY0VZ 7TZE-NAUPOL8LG-P6VO6IDMFU6ZNWFX-LIBTOMHFLAZGSYCXDT-18NF-EWAMCHJ- S-O-SJMTBY8YKTE-H-INTFUNLL-3SMG6MVDOI-DCTG18OT-MREALKAC0ZH-B5YPI LTLE-INUFLASXILFI--XV4AXOLIZD4RLTK9O6P6U4FNABHKI7-2AJ6D-F3-UB296"

for rot in range(0,16):
 fst = a.split()[0]
 if rot & 1: fst = trans(fst)
 print 'rot %02X' % rot
 indexes = xrange(len(fst))
 for c in [i for i in indexes if fst[i] == 'C']:
    for t in [i for i in indexes if fst[i] == 'T']:
        for n1 in [i for i in indexes if fst[i] == '1']:
            for n2 in [i for i in indexes if fst[i] == '8']:
                for dsh in [i for i in indexes if fst[i] == '-']:
                  for lst0 in indexes:
                       if fst[lst0] == '-': continue

                       ss = ''
                       rotf = rot
                       for seq in a.split():
                             if rotf & 1: seq = trans(seq)
                             rotf = rotf >> 1                       
#                            seq = trans(seq)
                             ss += ''.join([seq[i] for i  in [c,t,n1,n2,dsh,lst0]])
 
                       assert ss[0:5] == 'CT18-'
#                       print ss[9],
#                       if ss[9]!='-': continue
#                       if ss[14]!='-': continue
                       if ss[19]!='-': continue

                       print ss

