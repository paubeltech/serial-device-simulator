from debugsim import check_and_return_line_in_file, replace_rsp_in_file
from util import extract_data_or_cmd, replacer, setbits

STX = '{'
ETX = '}' 
DEVICE_ADDRESS = 'A'
CHECKSUM_USED = 'Yes'

def ascii_checksum(s):
    """
    Calculates and returns the ascii checksum for the data passed as
    parameter
    """
    sum = 0
    for c in s:
        sum += (ord(c)-32)
    sum = (sum % 95) + 32
    return '%c' % (sum & 0xFF)


def build_cmd_packet(cmd):
    """
    This command buildsand returns the resulting packet 
    as per the device protocol. \n
    parameters - \n
    cmd : main message or data that needs to be framed into a packet
    """    
    rsp = STX + DEVICE_ADDRESS + cmd + ETX
    # if(CHECKSUM_USED=='Yes'):
    #     rsp = rsp + ascii_checksum(rsp)
    return (rsp)

def build_return_packet(msg):
    """
    Returns the final packet by appending checksum to the data sent as
    parameter.
    """
    if(len(msg) > 0):
        if(CHECKSUM_USED == 'Yes'):
            msg = msg + ascii_checksum(msg)
    # Uncomment the code below, if testing with the client application...
    # as the client application disconnects on receiving 0 bytes
    # else: 
    #     msg = '*'
    return msg

def strip_msg_as_per_dbg_file(msg):
    """
    Removes the last checksum byte to match with the debug file.    
    """
    if(ascii_checksum(msg[:-1]) == msg[-1:]):
        msg = msg[:-1]

    return msg

def get_rsp_for_cmd(cmd):
    """
    This function checks wether the received message is part of the
    command. If yes then it proceeds to process it and return the
    appropriate response. Else it returns None
    """
    cmd_qry = {
                "@OA" : "@", "@OP" : "@", "@OU" : "@", "@OV" : "@", 
                "@LA" : "@", "@LP" : "@", "@LU" : "@", "@LV" : "@",
                "@N" : "@",
                "A" : "", "C" : "", "H" : "", "L" : "",
                "R" : "", "M" : "", "P" : "", "]" : "", 
                "1" : "", "2" : "",
                "G" : ""
                # , "K" : ""
                }

    rsp = ''
    ext_cmd = extract_data_or_cmd(cmd, STX, DEVICE_ADDRESS, ETX)
    status = 1
    if(isinstance(ext_cmd, str)):
        for key in cmd_qry:
            if(ext_cmd.startswith(key)):
                rsp = cmd_qry.get(key)
                if(rsp != ''):
                    rsp = build_cmd_packet(cmd_qry.get(key))
                
                status = update_rsp_for_cmd(cmd, ext_cmd)
                if status < 1:
                    rsp = ''

    return rsp

def update_rsp_for_cmd(cmd, ext_cmd):
    """
    This function checks the received extracted command(ext_cmd) with the 
    Dictionary of commands and when matched, the corresponding key's value
    is returned. The value returned is the query which would fetch the 
    data affected by the command sent.
    """
    cmd_qry = { # HPA Attenuator
                "@OA1" : "@OA1?", "@OA2" : "@OA2?", "@OA3" : "@OA3?", 
                "@OA4" : "@OA4?", "@OA5" : "@OA5?", "@OA6" : "@OA6?", 
                "@OA7" : "@OA7?", "@OA8" : "@OA8?", 
                # HPA Power
                "@OP1" : "@OP1?", "@OP2" : "@OP2?", "@OP3" : "@OP3?", 
                "@OP4" : "@OP4?", "@OP5" : "@OP5?", "@OP6" : "@OP6?", 
                "@OP7" : "@OP7?", "@OP8" : "@OP8?", 
                # Upconverter Attenuator 1
                "@OU1" : "@OU1?", "@OU2" : "@OU2?", "@OU3" : "@OU3?", 
                "@OU4" : "@OU4?", "@OU5" : "@OU5?", "@OU6" : "@OU6?", 
                "@OU7" : "@OU7?", "@OU8" : "@OU8?", 
                # Upconverter Attenuator 2
                "@OV1" : "@OV1?", "@OV2" : "@OV2?", "@OV3" : "@OV3?", 
                "@OV4" : "@OV4?", "@OV5" : "@OV5?", "@OV6" : "@OV6?", 
                "@OV7" : "@OV7?", "@OV8" : "@OV8?", 
                # Auto Mode # 
                # The Value is of the format ->
                # "Command,byte position(-1),start bit position,end bit position, value"
                "A" : "X1,3,0,5,1",
                "A1" : "X1,3,0,0,1", "A2" : "X1,3,1,1,1", "A3" : "X1,3,2,2,1", 
                "A4" : "X1,3,3,3,1", "A5" : "X1,3,4,4,1", "A6" : "X1,3,5,5,1",
                # Manual Mode
                # The Value is of the format ->
                # "Command,byte position(-1),start bit position,end bit position, value"
                "M" : "X1,3,0,5,0",
                "M1" : "X1,3,0,0,0", "M2" : "X1,3,1,1,0", "M3" : "X1,3,2,2,0", 
                "M4" : "X1,3,3,3,0", "M5" : "X1,3,4,4,0", "M6" : "X1,3,5,5,0",                 
                # RF Adjustment Limits
                "@LA" : "@LA?", "@LP" : "@LP?", "@LU" : "@LU?", "@LV" : "@LV?",
                # Set Maintenance Mode
                # The Value is of the format ->
                # "Command,byte position(-1),start bit position,end bit position, value"
                "H0" : "D,1,2,2,1", "H1" : "D,3,2,2,1", "H2" : "D,5,2,2,1", 
                "H3" : "D,7,2,2,1", "H4" : "D,9,2,2,1", "H5" : "D,11,2,2,1", 
                "H6" : "D,13,2,2,1", "H7" : "D,15,2,2,1", "H8" : "D,17,2,2,1", 
                # Clear Maintenance Mode
                # The Value is of the format ->
                # "Command,byte position(-1),start bit position,end bit position, value"
                "C0" : "D,1,2,2,0", "C1" : "D,3,2,2,0", "C2" : "D,5,2,2,0", 
                "C3" : "D,7,2,2,0", "C4" : "D,9,2,2,0", "C5" : "D,11,2,2,0", 
                "C6" : "D,13,2,2,0", "C7" : "D,15,2,2,0", "C8" : "D,17,2,2,0", 
                # Priority Chain Control
                # The Value is of the format ->
                # "Command,byte position(-1),start bit position,end bit position, value"
                "P0" : "D,1,3,3,1", "P1" : "D,3,3,3,1", "P2" : "D,5,3,3,1", 
                "P3" : "D,7,3,3,1", "P4" : "D,9,3,3,1", "P5" : "D,11,3,3,1", 
                "P6" : "D,13,3,3,1", "P7" : "D,15,3,3,1", "P8" : "D,17,3,3,1", 
                # Set KPA Channel
                "]" : "<", 
                # Local Remote
                # The Value is of the format ->
                # "Command,byte position(-1),start bit position,end bit position, value"
                "L" : "X1,0,0,0,1", "R" : "X1,0,0,0,0",
                # Fitted Flag
                "G" : "F",
                # Waveguide Switch Control
                "1" : "S", "2" : "S",
                # Network Address
                "@N" : "@N?"
                # ,"K" : "X2" 
                }

    search_cmd = ''
    # Command for KPA Channel settings starts with ']'
    if(ext_cmd.startswith(']')):
        return handle_set_kpa_channel(ext_cmd)
    # Command for Fitted flags starts with 'G'        
    elif(ext_cmd.startswith('G')):
        return handle_fitted_flag(ext_cmd)
    # Commands for Attenuation, Power etc starts with '@'   
    if(ext_cmd.startswith('@')):
        for key in cmd_qry:
            if(ext_cmd.startswith(key)):                
                search_cmd = build_cmd_packet(cmd_qry.get(key))
        if(search_cmd == ''):
            return -10

        act_rsp = check_and_return_line_in_file(search_cmd, command=True)
        return update_file_with_new_rsp(cmd, act_rsp)
    # Commands whose response is reflected in bulk status queries 
    # usually have command length of 1 or 2
    elif(len(ext_cmd) <= 2 and len(ext_cmd) >= 1):
        # Commands for Waveguide Switch postions starts with '1' or '2'
        if(ext_cmd.startswith('1') or ext_cmd.startswith('2')):
            return handle_waveguide_switches(ext_cmd)
        else:
            for key in cmd_qry:
                if(ext_cmd.startswith(key)):
                    cmd_rsp_str = cmd_qry.get(key).split(',')
                    search_cmd = build_cmd_packet(cmd_rsp_str[0])

            act_rsp = check_and_return_line_in_file(search_cmd, command=True)
            status = handle_bulk_cmd_rsp(cmd_rsp_str,act_rsp)

            if(len(ext_cmd) == 1 and (ext_cmd == 'A' or ext_cmd == 'M')):
                cmd_rsp_str[1] = '0'
                cmd_rsp_str[2] = '1'
                cmd_rsp_str[3] = '1'
                search_cmd = build_cmd_packet(cmd_rsp_str[0])
                act_rsp = check_and_return_line_in_file(search_cmd, command=True)
                status = handle_bulk_cmd_rsp_A_M(cmd_rsp_str,act_rsp)
            
            return status
            


def update_file_with_new_rsp(new_rsp, act_rsp):
    """
    This function replaces the actual response in the debug file
    with the new response.
    """
    if(len(act_rsp) < 1):
        return -12

    # Check if the checksum is present in the response
    # and replace in file accordingly
    if(new_rsp.find(ETX)+2 == len(new_rsp)):
        replace_rsp_in_file(act_rsp, new_rsp[:-1])
    else:
        replace_rsp_in_file(act_rsp, new_rsp)
    
    return 10


def handle_fitted_flag(ext_cmd):
    """
    This function handles Fitted flag commands
    """
    # c - chain number 0...8
    c = ext_cmd[1:2]
    # f - flag number 0...7
    f = ext_cmd[2:3]
    # v - value 0 or 1
    v = ext_cmd[3:4]

    # get the response for 'F' command from the debug file.
    act_rsp = check_and_return_line_in_file(build_cmd_packet('F'), command=True)
    # strip the response to retrieved only data
    strp_rsp = extract_data_or_cmd(act_rsp, STX, DEVICE_ADDRESS, ETX, cmd='F')
    # Manipulate the byte as per the c f v
    strp_rsp = setbits(strp_rsp, int(c), int(f), int(f), v)
    # update_packet = STX + DEVICE_ADDRESS + '<' + strp_rsp + ETX
    # Rebuild packet to be replaced in the debug file
    update_packet = build_cmd_packet('F' + strp_rsp)

    return update_file_with_new_rsp(update_packet, act_rsp)

def handle_waveguide_switches(ext_cmd):
    """
    This function handles Waveguid switch commands
    """    
    # Switch position
    postion = ext_cmd[0:1]
    # Switch Number
    switch_no = ord(ext_cmd[1:2]) - 65

    # get the response for 'S' command from the debug file.
    act_rsp = check_and_return_line_in_file(build_cmd_packet('S'), command=True)
    # strip the response to retrieved only data
    strp_rsp = extract_data_or_cmd(act_rsp, STX, DEVICE_ADDRESS, ETX, cmd='S')
    # Manipulate byte as per Switch position
    if postion == '1':
        strp_rsp = setbits(strp_rsp, int(switch_no), 0, 0, 1)
        # strp_rsp = setbits(strp_rsp, int(switch_no), 1, 1, 0)
    else:
        strp_rsp = setbits(strp_rsp, int(switch_no), 1, 1, 1)
        # strp_rsp = setbits(strp_rsp, int(switch_no), 0, 0, 0)

    # update_packet = STX + DEVICE_ADDRESS + 'S' + strp_rsp + ETX
    # Rebuild packet to be replaced in the debug file
    update_packet = build_cmd_packet('S' + strp_rsp)

    return update_file_with_new_rsp(update_packet, act_rsp)

def handle_set_kpa_channel(ext_cmd):
    """
    This function handles KPA Channel setting commands
    """    
    # Channel number to be set
    channel_no = ext_cmd[1:-1]
    # KPA number for which it needs to be set.
    kpa_no = ext_cmd[3:]
    # Convert ascii and subtract it with 65 to get 
    # KPA number between 0 - 8
    if(not kpa_no.isdigit()):
        print(f'This is not a digit')
        kpa_no_dec = ord(kpa_no) - 64
    else:        
        kpa_no_dec = int(kpa_no)
        print(f'This is a digit {int(kpa_no)}')

    # get the response for '<' command from the debug file.
    act_rsp = check_and_return_line_in_file(build_cmd_packet('<'), command=True)
    # strip the response to retrieved only data
    strp_rsp = extract_data_or_cmd(act_rsp, STX, DEVICE_ADDRESS, ETX, cmd='<')
    # Split response to get a list of values
    split_msg = strp_rsp.split(',')
    # Replace channel number with the new channel for the KPA
    split_msg[kpa_no_dec-1] = channel_no
    # Join the list
    strp_rsp = ",".join(split_msg)

    # update_packet = STX + DEVICE_ADDRESS + '<' + strp_rsp + ETX
    # Rebuild packet to be replaced in the debug file
    update_packet = build_cmd_packet('<' + strp_rsp)

    status = handle_set_kpa_channel_individual(channel_no, kpa_no_dec)
    if(status):
        return update_file_with_new_rsp(update_packet, act_rsp)

    return status   


def handle_set_kpa_channel_individual(channel_no, kpa_no_dec):
    print(f'kpa_no_dec: {kpa_no_dec}')
    # get the response for '<' command from the debug file.
    act_rsp = check_and_return_line_in_file(build_cmd_packet('<'+str(kpa_no_dec)), command=True)
    # strip the response to retrieved only data
    strp_rsp = extract_data_or_cmd(act_rsp, STX, DEVICE_ADDRESS, ETX, cmd='<')
    print(f'strp_rsp: {strp_rsp}')
    strp_rsp = channel_no

    # Rebuild packet to be replaced in the debug file
    update_packet = build_cmd_packet('<' + strp_rsp)   
    return update_file_with_new_rsp(update_packet, act_rsp)

def handle_bulk_cmd_rsp(cmd, act_rsp):
    """
    This function handles commands where changes are reflected 
    in the build status commands/queries
    """    
    cmd_t = (cmd[0])[:-1]
    print(f'cmd_t: {cmd_t}')
    act_rsp = extract_data_or_cmd(act_rsp, STX, DEVICE_ADDRESS, ETX, cmd=cmd_t)
    new_rsp = setbits(act_rsp, int(cmd[1]), int(cmd[2]), int(cmd[3]), cmd[4])

    return update_file_with_new_rsp(new_rsp,act_rsp)    

def handle_bulk_cmd_rsp_A_M(cmd, act_rsp):
    """
    This function handles commands where changes are reflected 
    in the build status commands/queries
    """    
    cmd_t = (cmd[0])[:-1]
    print(f'cmd_t: {cmd_t}')
    act_rsp = extract_data_or_cmd(act_rsp, STX, DEVICE_ADDRESS, ETX, cmd=cmd_t)
    new_rsp = setbits(act_rsp, int(cmd[1]), int(cmd[2]), int(cmd[3]), cmd[4])

    return update_file_with_new_rsp(new_rsp,act_rsp)    
        
def handle_at_the_rate_rsp(cmd, act_rsp):
    """
    This function handles commands that start with '@'
    """    
    if(cmd.find(ETX)+2 == len(cmd)):
        replace_rsp_in_file(act_rsp, cmd[:-1])
    else:
        replace_rsp_in_file(act_rsp, cmd)


def set_protocol_packet_vars(stx, etx, addr, checksum):
    """
    This function sets the global parameters.
    """    
    global STX
    STX = stx

    global ETX
    ETX = etx

    global DEVICE_ADDRESS
    DEVICE_ADDRESS = addr

    global CHECKSUM_USED
    CHECKSUM_USED = checksum

def main():
    cmd = '{A@OA1,25.0}O'
    ext_cmd = extract_data_or_cmd(cmd, '{', 'A', '}')
    print(cmd)
    qry = get_rsp_for_cmd(cmd)
    print(qry)


if __name__ == '__main__':
    main()

 
