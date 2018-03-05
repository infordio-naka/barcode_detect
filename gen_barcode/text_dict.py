import random

az  = [chr(i) for i in range(97, 123)]
AZ  = [c.upper() for c in az]
num = [str(i) for i in range(0, 10)]

code39 = num+AZ+['-', '.', ' ', '$', '/', '+', '%']
ean    = num
ean13  = num
ean8   = num
gs1    = num
gtin   = num
isbn   = num
isbn10 = num
isbn13 = num
issn   = num
jan    = num
pzn    = num
upc    = num
upca   = num

text_dict = {
    "code39":lambda x:"".join([random.choice(code39) for i in range(x)]),
    "ean":lambda x:"".join([random.choice(ean) for i in range(x)]),
    "ean13":lambda x:"".join([random.choice(ean13) for i in range(x)]),
    "ean8":lambda x:"".join([random.choice(ean8) for i in range(x)]),
    "gs1":lambda x:random.choice(["978", "979"])+"".join([random.choice(gs1) for i in range(x-3)]),
    "gtin":lambda x:"".join([random.choice(gtin) for i in range(x)]),
    "isbn":lambda x:random.choice(["978", "979"])+"".join([random.choice(isbn) for i in range(x-3)]),
    "isbn10":lambda x:"".join([random.choice(isbn10) for i in range(x)]),
    "isbn13":lambda x:random.choice(["978", "979"])+"".join([random.choice(isbn13) for i in range(x-3)]),
    "issn":lambda x:"".join([random.choice(issn) for i in range(x)]),
    "jan":lambda x:random.choice(["45", "49"])+"".join([random.choice(jan) for i in range(x-2)]),
    "pzn":lambda x:"".join([random.choice(pzn) for i in range(x)]),
    "upc":lambda x:"".join([random.choice(upc) for i in range(x)]),
    "upca":lambda x:"".join([random.choice(upca) for i in range(x)]),
}
