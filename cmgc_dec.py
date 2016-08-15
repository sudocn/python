# -*- coding: cp936 -*-

BASE64_TABLE_Ut = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
STAR_KEY_Uv = 'emag+/HF'
#STAR_LEN_Uy = len(STAR_KEY_Uv)
#STAR_MAP_Ux = []#transform_bJ(EMAG_Uv)

def pos_a(c):
    pos = BASE64_TABLE_Ut.find(c)
    return len(BASE64_TABLE_Ut) if (pos == -1 ) else pos

def encMap_bJ(key):
    temp = [ 0 ] * len(BASE64_TABLE_Ut)
    for i,v in enumerate(key):
        temp[pos_a(v)] = i

    emap = [ 0 ] * len(key)
    m = 1
    for i,v in enumerate(temp):
        if v != 0:
            emap[v] = m
            m += 1
            
    return emap

def decMap(key):
    emap = encMap_bJ(key)
    dmap = [ 0 ] * len(emap)
    for i,v in enumerate(emap):
        dmap[v] = i

    return dmap
    
def notAlphaNum_b(c):
    return (c < '0' or c > '9') and (c < 'A' or c > 'Z') \
           and (c < 'a' or c > 'z')

def reverse_bK(msg):
    msg = msg[::-1]
    out = ''
    for c in msg:
        if not notAlphaNum_b(c):
            c = chr(ord(c) ^ 0x8)
            if notAlphaNum_b(c):
                c = chr(ord(c) ^ 0x8)
        out += c
    return out

def bubTransform(msg, table):
    sz = len(table)
    rem = len(msg) % sz
    if rem != 0:
        msg = msg + ' ' * (sz - rem)

    j = 0
    out = [ 0 ] * len(msg)
    for i,v in enumerate(msg):
        out[i] = msg[table[i % sz] + j *sz]
        if i != 0 and (i + 1) % sz == 0:
            j += 1
            
    return  ''.join(out)

def bubEncode_bG(raw):
    return reverse_bK(bubTransform(raw, encMap_bJ(STAR_KEY_Uv)))

def bubDecode(msg):
    return bubTransform(reverse_bK(msg), decMap(STAR_KEY_Uv))    

def test_bub():
    '''
    bub_raw = \
    '460001298365603@6093@866528057836289@15@40166001@600116002110@intex@intex@NONE@20121@fFxOYKNeDzbR@'
    bub_enc = \
    '@      ZQCjrmFLG92pN@9n8@F2@FGMpmpmta@ft29fa89@86886989@8998668420@5@196203058758166@30636@3658068128894'
    '''
    bub_raw = '460021010350002@5335@200609111108180@15@41231000@626516024809@intex@intex@NONE@20121@BReomg8bsVe5@'
    bub_enc = '@      5eomVj0sg92mZ@9J8@F2@FGMpmpmta@ft40fa18@26286569@9288938490@5@890818999963388@52535@2888868982894'
    e = bubEncode_bG(bub_raw)
    print e
    print "encode", "OK" if e == bub_enc else "fail"

    d = bubDecode(e)
    print d
    print "decode", "OK" if d[:len(bub_raw)] == bub_raw else "fail"

    loginSMS = "BUB@|" + e
    print loginSMS

test_bub()

#############################################

MAP_Vv = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def longConv_a(num, size):
    st = ""
    j = long(num)
    while j != 0:
        #print j
        i = j - (j / 62) * 62
        st += (MAP_Vv[i])
        j = j / 62

    st += '0' * (size - len(st))
    #print st[::-1]
    return st[::-1]

def longRevConv(code):
    j = long(0)
    for c in code:
        j *= 62
        j += MAP_Vv.find(c)
        #print j

    return j
         
def billEncode_by(raw):
    #print raw
    result = ''
    for i in [18, 18, 18, 10]:
        head,raw = raw[:i],raw[i:]
        result += longConv_a(head, 6 if i == 10 else 11)
            
    return result

def billDecode(msg):
    result = ''
    for i in [11, 11, 11, 6]:
        head,msg = msg[:i],msg[i:]
        if i == 11:
            result += "%018ld" % longRevConv(head)
        else:
            result += "%010ld" % longRevConv(head)

    return result

def test_bill():
    #bill_raw = "2812012160011600211040166001000000000000006005793002001298365603"
    #bill_enc = "0Klu56DMabl07gOcZfmi8m0000AZYfXOS1ProCh"
    bill_raw = '2812012162651602480941231000000000000000006057424003021010350002'
    bill_enc = '0Klu56VEJ7w06x5FxOfRAG0000AfC5NaY16NKBm'
    e = billEncode_by(bill_raw)
    print e
    print "encode", "OK" if e == bill_enc else "fail"
    d = billDecode(bill_enc)
    print d
    print "decode", "OK" if d == bill_raw else "fail"

test_bill()
