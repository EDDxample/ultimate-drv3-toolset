# string = 'ABCDEFGHIJOLKMÑOPQRSTUVWKYZÁÉÍÓÚÜabcdefghijklmnñopqrstuvwxyzáéíóúü¡!¿?1234567890,.;:_Çç$#%&\'"<>+-=*'
# string = ''.join(sorted(set(string)))

# print(''.join(sorted(set(string))))

# print(ord('ñ'))



# v3_font08

# fontA = ' !,_.?TWabcdeghilmnortuw'
# fontA = ''.join(sorted(set(fontA)))

# for c in fontA:
#     print(ord(c), c)

# print()

# v3_font07

# fontB = ' !,_.?ATabcdefghijlmnoprstuwy'
# fontB = ''.join(sorted(set(fontB)))





# for c in fontB:
#     print(ord(c), c)

# ordinal = ord('!')
# print(ordinal, ordinal >> 3, ordinal & 7)

# print(ord('w') >> 3)

import struct
def read_u8(data): return struct.unpack('<B', data.read(1))[0]

# font8 = ' !,_.?TWabcdeghilmnortuw'
with open('files/srd/0_font/fr.srd', 'rb') as ff:
    ff.seek(0x70) # SpFt
    ff.seek(0x2C, 1) # list of character flags

    list_offset = ff.tell()
    print(ff.read(5))
    ff.seek(list_offset)
    for byte in range(255 // 8):
        current_byte = read_u8(ff)

        has_chars = False
        chars = ''
        
        for bit in range(8):
            if (current_byte >> bit) & 1 == 1:
                has_chars = True
                ordinal = byte * 8 + bit
                chars += chr(ordinal)

        if has_chars:
            print(f'{byte * 8} - {current_byte:08b} [ {chars} ]')
    