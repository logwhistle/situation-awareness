from communication.udp_function_0626 import timemark_udp


def infocode_udp(a, b):
    a1 = hex(a)
    b1 = hex(b)
    # 这一步强制转换，将udp读取的十进制转换为16进制
    a2 = str(a1)
    a2 = a2[2:]
    b2 = str(b1)
    b2 = b2[2:]
    # 这一步是字符串变化，同时删去无用的0x标识符
    all = b2 + a2
    all_decimal = int(all, 16)
    # print(type(all_decimal))
    return all_decimal


def info24002(packet):
    session = packet[0][3].load[18]
    subject = packet[0][3].load[22]
    state = packet[0][3].load[26]
    # 这里可以print到文本，也可以返回数组
    return [session, subject, state]


def info24000(packet):
    running_state = packet[0][3].load[18]
    return running_state


# 解析udp协议
def udp_interpretation(packet):
    a = packet
    timemark = timemark_udp(a[0][3].load[14], a[0][3].load[15], a[0][3].load[16], a[0][3].load[17])
    infocode = infocode_udp(a[0][3].load[8], a[0][3].load[9])
    if (len(a[0][3].load) == 20):
        state = info24000(a)
        return [False, state, infocode, timemark]
    else:
        detail = info24002(a)
        return detail.insert(0, True)


# 后续还需要写udp发送函数udp_sent

# udp_sent还需要定义信息类别码42000和42002


# 这里的infocode的返回值设置两个函数，分别接受不同的结果。


print(b)
print(c)
