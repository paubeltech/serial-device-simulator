from debugsim import check_and_return_line_in_file, replace_rsp_in_file

def replacer(s, newstring, index, nofail=False):
    # raise an error if index is outside of the string
    if not nofail and index not in range(len(s)):
        raise ValueError("index outside given string")

    # if not erroring, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return newstring + s
    if index > len(s):  # add it to the end
        return s + newstring

    # insert the new string between "slices" of the original
    return s[:index] + newstring + s[index + 1:]

def setbit(data, byte_pos, bit_pos, val):
    # Get the byte from the specified byte position
    byte = data[byte_pos:byte_pos+1]
    # Convert byte to 8bit binary
    bin_txt = format(ord(byte), '08b')
    # Replace bit position with new value - val
    bin_txt = replacer(bin_txt,str(val),bit_pos)
    # Convert binary text to ascii
    bin_to_ascii_txt = chr(int(bin_txt,2))
    # Replace original byte with the changed byte
    data = replacer(data,str(bin_to_ascii_txt), byte_pos)
    return data

def setbits(data, byte_pos, start_bit, end_bit, val):
    # Get the byte from the specified byte position
    byte = data[byte_pos:byte_pos+1]
    # Convert byte to 8bit binary
    bin_txt = format(ord(byte), '08b')
    print(f'bin_txt: {bin_txt}')

    # Replace bit positions with new value - val
    while(start_bit <= end_bit):
        # Subtract start_bit by 7 to start from end
        bin_txt = replacer(bin_txt,str(val),7-start_bit)
        start_bit+=1
    print(f'bin_txt: {bin_txt}')
    # Convert binary text to ascii
    bin_to_ascii_txt = chr(int(bin_txt,2))
    print(f'bin_to_ascii_txt: {bin_to_ascii_txt}')
    # Replace original byte with the changed byte
    data = replacer(data,str(bin_to_ascii_txt), byte_pos)
    return data

def extract_data_or_cmd(packet, stx, addr, etx, cmd=None, command=False):
    if(stx != None):
        data_start = packet.find(stx)
        # print(f'data_start {data_start}')
        if(data_start < 0):
            return -10
    else:
        data_start = 0

    if(addr != None):
        data_addr = packet.find(addr)
        # print(f'data_addr {data_addr}')
        if(data_addr < 0):
            return -11
        else:
            data_addr = len(addr)
    else:
        data_addr = 0


    if(cmd != None and command == False):
        data_cmd = packet.find(cmd)
        # print(f'data_cmd {data_cmd}')
        if(data_cmd < 0):
            return -12
        else:
            data_cmd = len(cmd)
    else:
        data_cmd = 0

    if(etx != None):
        data_end = packet.find(etx)
        # print(f'data_end {data_end}')
        if(data_end < 0):
            return -13
    else:
        data_end = 1

    # data_addr = (self.addr != None and len(self.addr) or 0)
    # data_cmd = (self.cmd != None and len(self.cmd) or 0)
    data_start_index = 1 + data_addr + data_cmd
    # print(f'data_start_index {data_start_index}')
    data = packet[data_start+data_start_index:data_end]
    # print(f'data {data}')

    return data

def build_packet(data, stx, addr, cmd, etx):
    packet = stx + addr + cmd + data + etx + 'n'

    return packet

def xstr(s):
    if s is None:
        return ''
    return str(s)


def main():
    packet = '{AXQ#P@@@@@T@B[@@@@}n'
    stx = '{'
    etx = '}'
    addr = 'A'
    cmd = 'X'

    data = extract_data_or_cmd(packet, stx, addr, cmd, etx)
    print(data)
    data = setbit(data, 4, 2, 1)
    print(data)
    data = setbits(data, 4, 2, 4, 1)
    print(data)

    packet = build_packet(data, stx, addr, cmd, etx)
    print(packet)

    packet = '{AS}n'

    rsp_text = check_and_return_line_in_file(packet)
    print(rsp_text)

    replace_rsp_in_file('This_is_something_we_need_to_take_care_of', rsp_text)

if __name__ == '__main__':
    main()
