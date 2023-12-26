from session1.session1sbj1 import Session1Sbj1
from session1.session1sbj2 import Session1Sbj2
from session2.session2sbj1 import Session2Sbj1
from session2.session2sbj2 import Session2Sbj2
from session3.session3sbj1 import Session3Sbj1
from session3.session3sbj2 import Session3Sbj2
from maps.StaticMap import StaticMap
from maps.BreakInfo import BreakInfo
from utils.TestOfRes import *

TEST = True

if __name__ == "__main__":
    # 预处理阶段
    # 根目录
    rootAddress = "originalFile\\"
    # 建立静态地图
    staticMap = StaticMap(rootAddress)
    # 建立breakEvent信息表
    breakInfo = BreakInfo()
    # if TEST:
    #     # 测试静态图
    #     testOfStatic = TestOfRes(sbj=None, res=None, map=staticMap, roadLineListList=None, segmentListList=None,
    #                              pointIdListList=None, isolatedPoint=staticMap.res)

    # # session1project1调用50次
    # time = 6
    # report_list = []
    # for sendId in range(1, time):
    #     print("\n===================================== 科目一/情景一 开始运行client_path_" + str(
    #         sendId) + " =====================================")
    #     rootAddress = "originalFile\\"
    #     session1sbj1 = Session1Sbj1(rootAddress=rootAddress, FileNumber=sendId, staticMap=staticMap, BreakInfo=breakInfo)
    #     if TEST:
    #         if sendId < time:
    #             roadLine = None
    #             Segment = None
    #             roadPoint = None  # [[]]
    #
    #             testOfsession1Sbj1 = TestOfRes(sbj=session1sbj1, map=None, roadLineListList=roadLine,
    #                                            segmentListList=Segment, pointIdListList=roadPoint)
    #     report_list.append(len(session1sbj1.drawMapRes))
    # print("session1:\t paths_num:{} \n\t average_num:{}".format(report_list, sum(report_list) / len(report_list)))

    # # session1project2调用50次
    # time = 6
    # for sendId in range(1, time):
    #     print("\n===================================== 科目一/情景二 开始运行client_path_" + str(
    #         sendId) + " =====================================")
    #     rootAddress = "originalFile\\"
    #     session1sbj2 = Session1Sbj2(rootAddress=rootAddress, FileNumber=sendId, staticMap=staticMap,
    #                                 BreakInfo=breakInfo)
    #     if TEST:
    #         if sendId < time:
    #             roadLine = [[479]]
    #             Segment = [[]]
    #             roadPoint = None  # [[]]
    #
    #             testOfsession1Sbj2 = TestOfRes(sbj=session1sbj2, map=None, roadLineListList=roadLine,
    #                                            segmentListList=Segment, pointIdListList=roadPoint)

    # session2project1调用50次
    time = 2
    for sendId in range(1, time):
        print("\n===================================== 科目二/情景一 开始运行client_path_" + str(sendId) + " =====================================")
        rootAddress = "originalFile\\"
        session2sbj1 = Session2Sbj1(rootAddress=rootAddress, FileNumber=sendId, staticMap=None, BreakInfo=None)

        if TEST:
            testOfsession2sbj1 = TestOfRes(sbj=session2sbj1, map=None, roadLineListList=None,
                                           segmentListList=None, pointIdListList=None)

    # # session2project2调用50次
    # time = 2
    # for sendId in range(1, time):
    #     print("\n===================================== 科目二/情景一 开始运行client_path_" + str(sendId) + " =====================================")
    #     rootAddress = "originalFile\\"
    #     session2sbj2 = Session2Sbj2(rootAddress=rootAddress, FileNumber=sendId, staticMap=staticMap, BreakInfo=breakInfo)
    #
    #     if TEST:
    #         testOfsession2sbj2 = TestOfRes(sbj=session2sbj2, map=None, roadLineListList=None,
    #                                        segmentListList=None, pointIdListList=None)

    # # session3project1调用50次
    # time = 2
    # for sendId in range(1, time):
    #     print("\n===================================== 科目三/情景一 开始运行client_path_" + str(
    #         sendId) + " =====================================")
    #     rootAddress = "originalFile\\"
    #     session3sbj1 = Session3Sbj1(rootAddress=rootAddress, FileNumber=sendId, staticMap=staticMap,
    #                                 BreakInfo=breakInfo)
    #
    #     if TEST:
    #         if sendId < time:
    #             roadLine = None
    #             Segment = None
    #             roadPoint = None  # [[]]
    #             testOfsession3sbj1 = TestOfRes(sbj=session3sbj1, roadLineListList=roadLine, segmentListList=Segment,
    #                                            pointIdListList=roadPoint)

    # # session3project2调用50次
    # time = 3
    # for sendId in range(2, time):
    #     print("\n===================================== 科目三/情景二 开始运行client_path_" + str(
    #         sendId) + " =====================================")
    #     rootAddress = "originalFile\\"
    #     session3sbj2 = Session3Sbj2(rootAddress=rootAddress, FileNumber=sendId, staticMap=staticMap,
    #                                 BreakInfo=breakInfo)
    #     res = session3sbj2.finalRes
    #
    #     if TEST:
    #         testOfsession3sbj2 = TestOfRes(sbj=session3sbj2, map=None, roadLineListList=None,
    #                                        segmentListList=None, pointIdListList=None, isolatedPoint=None)

        # 打印每个点坐标
        # staticMap.printAllPointCoordinate()

        # 打印邻接表
        # staticMap.printAnswer()

        # # 打印每个roadLine的segmentList
        # staticMap.printSegmentListOfRoadLines(False)

        # # 打印每个RoadLine的PointList
        # staticMap.printPointListOfRoadLines(False)

        # # 打印每个Point的RoadLineList
        # staticMap.printRoadLineListOfPoints(False)

    input("\n\n按下 enter 键后退出。")
