import threading

from maps.BreakInfo import BreakInfo
from maps.StaticMap import StaticMap
from session1.session1sbj1 import Session1Sbj1
from session2.session2sbj2_backUp import Session2Sbj2


def Session1_Subject1(sendId, state, originalFile, staticMap, msgQueue, text):
    if sendId > 5:
        text.delete("1.0", "end")
        text.insert("end", chars="场次序号有误,序号为：" + str(sendId))
        return

    text.delete("1.0", "end")
    text.insert("end", chars="session1_subject1 第" + str(sendId) + "次考试 is running...")
    print("session1_subject1 is running...")
    if staticMap is None:
        print("please prepare staticMap")
        text.delete("1.0", "end")
        text.insert("end", chars="please prepare staticMap")
        return
    execSession1_Subject1(sendId, staticMap, originalFile)
    msg = "1,1," + str(sendId) + ",3"
    msgQueue.put(msg)


def execSession1_Subject1(sendId, staticMap, originalFile):
    REPORT = False
    # 建立breakEvent信息表
    breakInfo = BreakInfo()

    # test = Test()
    # badLine = [[]]
    # badSegment = [[]]
    # # print("··············并查集测试结果··············")
    # badPoint = [[]] + connectState(staticMap)
    # test.testOfMap(badLine, badSegment, badPoint, map=staticMap)

    # 调用50次session1
    if REPORT:
        report_list = []

    print("\n===================================== 科目一/情景一 开始运行client_path_" + str(
        sendId) + " =====================================")
    rootAddress = str(originalFile)
    session1 = Session1Sbj1(rootAddress, staticMap, breakInfo, sendId)
    routine = session1.returnRes()
    # routine = [routine[0], routine[9]]
    # if i < 6:
    #     test = Test()
    #     badLine = [[]]
    #     badSegment = [[]]
    #     badPoint = [[]]
    #     test.testOfMap(badLine, badSegment, badPoint, session1, routine=routine)
    report_list = []
    if REPORT:
        report_list.append(len(routine))
    if REPORT:
        print("session1:\t paths_num:{} \n\t average_num:{}".format(report_list, sum(report_list) / len(report_list)))


def Session1_Subject2(sendId, originalFile, staticMap, msgQueue, text, semaphore):
    if sendId > 5:
        text.delete("1.0", "end")
        text.insert("end", chars="场次序号有误,序号为：" + str(sendId))
        return
    text.delete("1.0", "end")
    text.insert("end", chars="session1_subject2 第" + str(sendId) + "次考试 is running...")
    print("session1_subject2 is running...")
    if staticMap is None:
        print("please prepare staticMap")
        text.delete("1.0", "end")
        text.insert("end", chars="please prepare staticMap")
        return
    execSession1_Subject2(sendId, staticMap, originalFile, semaphore, text)
    msg = "1,2," + str(sendId) + ",3"
    msgQueue.put(msg)


def execSession1_Subject2(sendId, staticMap, originalFile, semaphore, text):
    firstStep(sendId, staticMap, originalFile, text)
    semaphore.acquire()
    secondStep(sendId, staticMap, originalFile, text)


def firstStep(sendId, staticMap, originalFile, text):
    text.delete("1.0", "end")
    text.insert("end", chars="step 1 is running...")
    print("step 1 is running...")


def secondStep(sendId, staticMap, originalFile, text):
    text.delete("1.0", "end")
    text.insert("end", chars="step 2 is running...")
    print("step 2 is running...")


def Session2_Subject1(sendId, state, originalFile, staticMap, msgQueue, text):
    if sendId > 5:
        text.delete("1.0", "end")
        text.insert("end", chars="场次序号有误,序号为：" + str(sendId))
        return
    text.delete("1.0", "end")
    text.insert("end", chars="session2_subject1 第" + str(sendId) + "次考试 is running...")
    print("session2_subject1 is running...")
    if staticMap is None:
        print("please prepare staticMap")
        text.delete("1.0", "end")
        text.insert("end", chars="please prepare staticMap")
        return
    execSession2_Subject1(sendId, staticMap, originalFile, text)
    msg = "2,1," + str(sendId) + ",3"
    msgQueue.put(msg)


def execSession2_Subject1(sendId, staticMap, originalFile, text):
    print("execSession2_Subject1")


def Session2_Subject2(sendId, state, originalFile, staticMap, msgQueue, text):
    if sendId > 5:
        text.delete("1.0", "end")
        text.insert("end", chars="场次序号有误,序号为：" + str(sendId))
        return
    text.delete("1.0", "end")
    text.insert("end", chars="session2_subject2 第" + str(sendId) + "次考试 is running...")
    print("session2_subject2 is running...")
    if staticMap is None:
        print("please prepare staticMap")
        text.delete("1.0", "end")
        text.insert("end", chars="please prepare staticMap")
        return
    execSession2_Subject2(sendId, staticMap, )
    msg = "2,2," + str(sendId) + ",3"
    msgQueue.put(msg)


def execSession2_Subject2(sendId, staticMap, originalFile, text):
    print("execSession2_Subject2")


def Session3_Subject1(sendId, state, originalFile, staticMap, msgQueue, text):
    if sendId > 5:
        text.delete("1.0", "end")
        text.insert("end", chars="场次序号有误,序号为：" + str(sendId))
        return
    text.delete("1.0", "end")
    text.insert("end", chars="session3_subject1 第" + str(sendId) + "次考试 is running...")
    print("session3_subject1 is running...")
    if staticMap is None:
        print("please prepare staticMap")
        text.delete("1.0", "end")
        text.insert("end", chars="please prepare staticMap")
        return
    execSession3_Subject1(sendId, staticMap, )
    msg = "3,1," + str(sendId) + ",3"
    msgQueue.put(msg)


def execSession3_Subject1(sendId, staticMap, originalFile, text):
    print("execSession3_Subject1")


def Session3_Subject2(sendId, state, originalFile, staticMap, msgQueue, text):
    if sendId > 5:
        text.delete("1.0", "end")
        text.insert("end", chars="场次序号有误,序号为：" + str(sendId))
        return
    text.delete("1.0", "end")
    text.insert("end", chars="session3_subject2 第" + str(sendId) + "次考试 is running...")
    print("session3_subject2 is running...")
    if staticMap is None:
        print("please prepare staticMap")
        text.delete("1.0", "end")
        text.insert("end", chars="please prepare staticMap")
        return
    execSession3_Subject2(sendId, staticMap, )
    msg = "2,1," + str(sendId) + ",3"
    msgQueue.put(msg)


def execSession3_Subject2(sendId, staticMap, originalFile, text):
    print("execSession3_Subject2")
