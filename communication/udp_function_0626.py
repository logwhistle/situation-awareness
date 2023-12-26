
import struct
# import scapy

from datetime import datetime
import socket
from scapy.all import *


#主要函数

# 1、def udp_grasp(filter_grasp): 抓包
# 输入--提供抓包时的过滤条件；输出：一条服务端发出的udp报文

# 2、def udp_interpretation(packet): 解析 ，判断报文是24000还是24002
# 输入--udp报文； 24000--输出运行状态， 24002--输出考试信息detail [session,subject,number,state]


# 3、info42000(port_server,port_client,ip_address): 发送udp报文42000
# 如果发送成功，返回42000

# 4、info42002(port_server,port_client,ip_address,session,subject,number,state): 发送udp报文42002
# 如果发送成功，返回42002








#转包代码 一次只抓取一个udp报文，应该需要循环执行
#filter_grasp的例子： 'dst host 192.168.1.107 && dst port 10014'  字符串 IP+端口号
def udp_grasp(filter_grasp):
    packet=sniff(filter=filter_grasp, prn=lambda x:x.summary(),count=1)
    # packet[0][3].load --->  这个里面保存了报文里所有的data
    #每100毫秒抓取一次
    return packet

#为了获得更准确的抓取结果，这里应该还需要指定source的ip  （src+dst && two port）


def timemark_udp(a,b,c,d):
    a1=hex(a);
    b1=hex(b);
    c1=hex(c);
    d1=hex(d);
    #这一步强制转换，将udp读取的十进制转换为16进制
    a2 = str(a1);
    a2 = a2[2:];
    b2 = str(b1)
    b2 = b2[2:]
    c2 = str(c1)
    c2 = c2[2:]
    d2 = str(d1)
    d2 = d2[2:]
    #这一步是字符串变化，同时删去无用的0x标识符

    all=d2+c2+b2+a2;
    all_decimal=int(all,16)
    # 将字符串逆序相加，形成16进制字符串，再将16进制字符串返回成10进制int类型的时间戳
    #print(type(all_decimal))
    return all_decimal

def infocode_udp(a,b):
    a1 = hex(a);
    b1 = hex(b);
    # 这一步强制转换，将udp读取的十进制转换为16进制
    a2 = str(a1);
    a2 = a2[2:];
    b2 = str(b1)
    b2 = b2[2:]
    # 这一步是字符串变化，同时删去无用的0x标识符
    all =  b2 + a2;
    all_decimal = int(all, 16)
    # print(type(all_decimal))
    return all_decimal


def info24002(packet):
    session= packet[0][3].load[18]
    subject=packet[0][3].load[22]
    number=packet[0][3].load[26]
    state= packet[0][3].load[30]
    #这里可以print到文本，也可以返回数组

    return [session,subject,number,state]


def info24000(packet):
    running_state= packet[0][3].load[18]
    return running_state



#解析udp协议
def udp_interpretation(packet):
    a=packet
    timemark = timemark_udp(a[0][3].load[14], a[0][3].load[15], a[0][3].load[16], a[0][3].load[17])
    infocode = infocode_udp(a[0][3].load[8], a[0][3].load[9])
    if(len(a[0][3].load)==20):
        state=info24000(a)
        ret = list()
        ret.append(state)
        return ret
    else:
        detail=info24002(a)
        return detail





def info42000(id_server,id_client,ip_address,port_server):
    id_server=int(id_server)
    id_client=int(id_client)
    id_serve_b =struct.pack('<H', id_server)
    id_client_b =struct.pack('<H', id_client)
    len_info=1
    len_info_b =struct.pack('<I', len_info)
    bool_value=1
    bool_value_b =struct.pack('?', bool_value)
    #print(bool_value_b)
    infocode=42000
    infocode_b =struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9=time_now[:9]
    print(time_now_9)
    time_int=int(time_now_9)
    timemark_b=struct.pack('<I', time_int)
    message=b'\x52\x48\x5a\x54'+id_serve_b+id_client_b+infocode_b+len_info_b+timemark_b+b'\x01'+bool_value_b

    # 创建socket对象
    # SOCK_DGRAM  udp模式
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 字节
    port_server=int(port_server)
    ip_address=str(ip_address)
    address_port=(ip_address,port_server)
    s.sendto(message, address_port)
    s.close()
    return 42000

def info42002_prepare_11(id_server,id_client,ip_address,port_server):
    id_server = int(id_server)
    id_client = int(id_client)

    id_serve_b = struct.pack('<H', id_server)
    id_client_b = struct.pack('<H', id_client)
    len_info = 16
    len_info_b = struct.pack('<I', len_info)

    session_b = struct.pack('<I', 1)
    subject_b = struct.pack('<I', 1)
    number_b = struct.pack('<I', 0)
    state_b = struct.pack('<I', 1)

    bool_value = 1
    bool_value_b = struct.pack('?', bool_value)
    # print(bool_value_b)
    infocode = 42002
    infocode_b = struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9 = time_now[:9]
    print(time_now_9)
    time_int = int(time_now_9)
    timemark_b = struct.pack('<I', time_int)
    message = b'\x52\x48\x5a\x54' + id_serve_b + id_client_b + infocode_b + len_info_b + timemark_b + session_b + subject_b + number_b + state_b + bool_value_b

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 以字节为单位
    port_server = int(port_server)
    ip_address = str(ip_address)
    address_port = (ip_address, port_server)
    s.sendto(message, address_port)
    s.close()
    return 42002


def info42002_prepare_12(id_server,id_client,ip_address,port_server):
    id_server = int(id_server)
    id_client = int(id_client)

    id_serve_b = struct.pack('<H', id_server)
    id_client_b = struct.pack('<H', id_client)
    len_info = 16
    len_info_b = struct.pack('<I', len_info)

    session_b = struct.pack('<I', 1)
    subject_b = struct.pack('<I', 2)
    number_b = struct.pack('<I', 0)
    state_b = struct.pack('<I', 1)

    bool_value = 1
    bool_value_b = struct.pack('?', bool_value)
    # print(bool_value_b)
    infocode = 42002
    infocode_b = struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9 = time_now[:9]
    print(time_now_9)
    time_int = int(time_now_9)
    timemark_b = struct.pack('<I', time_int)
    message = b'\x52\x48\x5a\x54' + id_serve_b + id_client_b + infocode_b + len_info_b + timemark_b + session_b + subject_b + number_b + state_b + bool_value_b

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 以字节为单位
    port_server = int(port_server)
    ip_address = str(ip_address)
    address_port = (ip_address, port_server)
    s.sendto(message, address_port)
    s.close()
    return 42002

def info42002_prepare_21(id_server,id_client,ip_address,port_server):
    id_server = int(id_server)
    id_client = int(id_client)

    id_serve_b = struct.pack('<H', id_server)
    id_client_b = struct.pack('<H', id_client)
    len_info = 16
    len_info_b = struct.pack('<I', len_info)

    session_b = struct.pack('<I', 2)
    subject_b = struct.pack('<I', 1)
    number_b = struct.pack('<I', 0)
    state_b = struct.pack('<I', 1)

    bool_value = 1
    bool_value_b = struct.pack('?', bool_value)
    # print(bool_value_b)
    infocode = 42002
    infocode_b = struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9 = time_now[:9]
    print(time_now_9)
    time_int = int(time_now_9)
    timemark_b = struct.pack('<I', time_int)
    message = b'\x52\x48\x5a\x54' + id_serve_b + id_client_b + infocode_b + len_info_b + timemark_b + session_b + subject_b + number_b + state_b + bool_value_b

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 以字节为单位
    port_server = int(port_server)
    ip_address = str(ip_address)
    address_port = (ip_address, port_server)
    s.sendto(message, address_port)
    s.close()
    return 42002


def info42002_prepare_22(id_server,id_client,ip_address,port_server):
    id_server = int(id_server)
    id_client = int(id_client)

    id_serve_b = struct.pack('<H', id_server)
    id_client_b = struct.pack('<H', id_client)
    len_info = 16
    len_info_b = struct.pack('<I', len_info)

    session_b = struct.pack('<I', 2)
    subject_b = struct.pack('<I', 2)
    number_b = struct.pack('<I', 0)
    state_b = struct.pack('<I', 1)

    bool_value = 1
    bool_value_b = struct.pack('?', bool_value)
    # print(bool_value_b)
    infocode = 42002
    infocode_b = struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9 = time_now[:9]
    print(time_now_9)
    time_int = int(time_now_9)
    timemark_b = struct.pack('<I', time_int)
    message = b'\x52\x48\x5a\x54' + id_serve_b + id_client_b + infocode_b + len_info_b + timemark_b + session_b + subject_b + number_b + state_b + bool_value_b

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 以字节为单位
    port_server = int(port_server)
    ip_address = str(ip_address)
    address_port = (ip_address, port_server)
    s.sendto(message, address_port)
    s.close()
    return 42002

def info42002_prepare_31(id_server,id_client,ip_address,port_server):
    id_server = int(id_server)
    id_client = int(id_client)

    id_serve_b = struct.pack('<H', id_server)
    id_client_b = struct.pack('<H', id_client)
    len_info = 16
    len_info_b = struct.pack('<I', len_info)

    session_b = struct.pack('<I', 3)
    subject_b = struct.pack('<I', 1)
    number_b = struct.pack('<I', 0)
    state_b = struct.pack('<I', 1)

    bool_value = 1
    bool_value_b = struct.pack('?', bool_value)
    # print(bool_value_b)
    infocode = 42002
    infocode_b = struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9 = time_now[:9]
    print(time_now_9)
    time_int = int(time_now_9)
    timemark_b = struct.pack('<I', time_int)
    message = b'\x52\x48\x5a\x54' + id_serve_b + id_client_b + infocode_b + len_info_b + timemark_b + session_b + subject_b + number_b + state_b + bool_value_b

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 以字节为单位
    port_server = int(port_server)
    ip_address = str(ip_address)
    address_port = (ip_address, port_server)
    s.sendto(message, address_port)
    s.close()
    return 42002


def info42002_prepare_32(id_server,id_client,ip_address,port_server):
    id_server = int(id_server)
    id_client = int(id_client)

    id_serve_b = struct.pack('<H', id_server)
    id_client_b = struct.pack('<H', id_client)
    len_info = 16
    len_info_b = struct.pack('<I', len_info)

    session_b = struct.pack('<I', 3)
    subject_b = struct.pack('<I', 2)
    number_b = struct.pack('<I', 0)
    state_b = struct.pack('<I', 1)

    bool_value = 1
    bool_value_b = struct.pack('?', bool_value)
    # print(bool_value_b)
    infocode = 42002
    infocode_b = struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9 = time_now[:9]
    print(time_now_9)
    time_int = int(time_now_9)
    timemark_b = struct.pack('<I', time_int)
    message = b'\x52\x48\x5a\x54' + id_serve_b + id_client_b + infocode_b + len_info_b + timemark_b + session_b + subject_b + number_b + state_b + bool_value_b

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 以字节为单位
    port_server = int(port_server)
    ip_address = str(ip_address)
    address_port = (ip_address, port_server)
    s.sendto(message, address_port)
    s.close()
    return 42002












def info42002(id_server,id_client,ip_address,port_server,session,subject,number,state):
    id_server=int(id_server)
    id_client=int(id_client)
    session=int(session)
    subject=int(subject)
    number=int(number)
    state=int(state)
    id_serve_b =struct.pack('<H', id_server)
    id_client_b =struct.pack('<H', id_client)
    len_info=16
    len_info_b =struct.pack('<I', len_info)

    session_b = struct.pack('<I', session)
    subject_b = struct.pack('<I', subject)
    number_b = struct.pack('<I', number)
    state_b=struct.pack('<I', state)

    bool_value=1
    bool_value_b =struct.pack('?', bool_value)
    #print(bool_value_b)
    infocode=42002
    infocode_b =struct.pack('<H', infocode)
    time_now = datetime.now().strftime('%H%M%S%f')
    time_now_9=time_now[:9]
    print(time_now_9)
    time_int=int(time_now_9)
    timemark_b=struct.pack('<I', time_int)
    message=b'\x52\x48\x5a\x54'+id_serve_b+id_client_b+infocode_b+len_info_b+timemark_b+session_b+subject_b+number_b+state_b+bool_value_b

    # 创建socket对象
    # SOCK_DGRAM  udp模式
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 发送数据 以字节为单位
    port_server=int(port_server)
    ip_address=str(ip_address)
    address_port=(ip_address,port_server)
    s.sendto(message, address_port)
    s.close()
    return 42002





