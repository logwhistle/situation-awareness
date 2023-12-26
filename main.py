import threading
import time
import tkinter
from functools import partial
from communication.udp_function_0626 import *
from multiprocessing.managers import BaseManager
from queue import Queue

import maps
from communication.udp_function_0626 import udp_interpretation, udp_grasp, info42000, info42002


from maps.BreakInfo import BreakInfo
from session1.session1sbj1 import Session1Sbj1
from maps.StaticMap import StaticMap

import socket  # 导入 socket 模块
import yaml
import os
import sys
import handler
semaphore12 = threading.Semaphore(0)

def startClient(ip, serverID, serverReceive, clientID, clientReceive, originalFile, staticMap):
    filter_grasp = "dst host " + str(ip) + " && dst port " + str(clientReceive)
    print(filter_grasp)
    # command = [1, 2, 1, 0]
    while True:

        command = udp_interpretation(udp_grasp(filter_grasp))
        print(command)

        if not msgQueue.empty():
            m = msgQueue.get()
            print(m)
            strList = m.split(",")
            if len(strList) != 4:
                print("消息错误")
                text.delete("1.0", "end")
                text.insert("end", chars="消息错误")
                break
            text.delete("1.0", "end")
            text.insert("end", chars=m)

            # 发送已完成
            info42002(serverID, clientID, ip, serverReceive, strList[0], strList[1], strList[2], strList[3])
        if len(command) == 1:
            # 心跳响应
            info42000(serverID, clientID, ip, serverReceive)
        else:
            # time.sleep(5)
            # command[3] += 1
            # print("command[3]:" + str(command[3]))
            if command[0] == 1 and command[1] == 1:
                t = threading.Thread(target=handler.Session1_Subject1,
                                     args=(command[2], command[3], originalFile, staticMap, msgQueue, text,))
                t.start()
            elif command[0] == 1 and command[1] == 2:
                if command[3] == 1:
                    t = threading.Thread(target=handler.Session1_Subject2,
                                         args=(command[2], originalFile, staticMap, msgQueue, text, semaphore12,))
                    t.start()
                if command[3] == 2:
                    semaphore12.release()
            elif command[0] == 2 and command[1] == 1:
                t = threading.Thread(target=handler.Session2_Subject1,
                                     args=(command[2], command[3], originalFile, staticMap, msgQueue, text,))
                t.start()
            elif command[0] == 2 and command[1] == 2:
                t = threading.Thread(target=handler.Session2_Subject2,
                                     args=(command[2], command[3], originalFile, staticMap, msgQueue, text,))
                t.start()
            else:
                pass


def get_yaml_data(yaml_file):
    # 打开yaml文件
    print("***获取yaml文件数据***")
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data


def Prepare(originalFile):
    # D.delete("1.0", "end")
    # D.insert("end", chars="preparing...")
    rootAddress = originalFile
    # 建立静态地图
    global staticMap
    staticMap = StaticMap(rootAddress)
    text.delete("1.0", "end")
    text.insert("end", chars="staticMap OK")


if __name__ == '__main__':
    # os.chdir(sys.path[0])
    msgQueue = Queue()
    staticMap = None
    REPORT = False
    conf = get_yaml_data("conf\\dev.yaml")
    ip = conf['ip']
    serverID = conf["server"]["id"]
    clientID = conf["client"]["id"]
    serverReceive = conf["server"]["receive"]
    clientReceive = conf["client"]["receive"]
    originalFile = conf["originalFile"]
    windows = tkinter.Tk()
    windows.title('RHZT_TJU')
    windows.geometry('500x1000')
    A = tkinter.Label(windows, text='TJU_RHZT', bg='yellow', font=('times new roman', 20), width=20, height=3)
    prepare11 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="prepare11",
                               command=lambda: info42002_prepare_11(serverID, clientID, ip, serverReceive),
                               width=10, height=3)
    prepare12 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="prepare12",
                               command=lambda: info42002_prepare_12(serverID, clientID, ip, serverReceive),
                               width=10, height=3)
    prepare21 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="prepare21",
                               command=lambda: info42002_prepare_21(serverID, clientID, ip, serverReceive),
                               width=10, height=3)
    prepare22 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="prepare22",
                               command=lambda: info42002_prepare_22(serverID, clientID, ip, serverReceive),
                               width=10, height=3)
    prepare31 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="prepare31",
                               command=lambda: info42002_prepare_31(serverID, clientID, ip, serverReceive),
                               width=10, height=3)
    prepare32 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="prepare32",
                               command=lambda: info42002_prepare_32(serverID, clientID, ip, serverReceive),
                               width=10, height=3)
    # session1sbj1 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="session1sbj1",
    #                              command=Session1_Subject1,
    #                              width=10, height=3)
    # session2sbj2 = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="session2sbj2",
    #                              command=Session2_Subject2,
    #                              width=10, height=3)

    text = tkinter.Text(windows)
    A.pack()
    prepare11.pack()
    prepare12.pack()
    prepare21.pack()
    prepare22.pack()
    prepare31.pack()
    prepare32.pack()
    # prepare.pack()
    # session1sbj1.pack()
    # session2sbj2.pack()
    text.pack()
    Prepare(originalFile)
    # 开启线程
    getThread = threading.Thread(target=startClient, args=(ip, serverID, serverReceive, clientID, clientReceive, originalFile, staticMap))
    getThread.start()

    windows.mainloop()
    print("主程序完成")
