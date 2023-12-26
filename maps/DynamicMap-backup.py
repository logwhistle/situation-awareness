import json
from maps.MapScale import MapScale
from maps.RoadLine import RoadLine
from maps.RoadPoint import RoadPoint
from maps.Segment import Segment
from utils.MapsUtil import *
from utils.Clustering import *
from copy import deepcopy


# DynamicMap: 静态地图
class DynamicMap:

    # 初始化StaticMap类
    def __init__(self, staticMap, breakInfo) -> None:
        print("\n========================== 开始创建dynamicMap ==========================")
        # 存储地图画幅大小，以便画图使用
        self.mapScale = deepcopy(staticMap.mapScale)
        # 存储 RoadLineId--RoadLine
        self.roadLineHashMap = deepcopy(staticMap.roadLineHashMap)
        # 存储 RoadPoint的StringId--intId
        self.roadPointIndexHashMap = deepcopy(staticMap.roadPointIndexHashMap)
        # 存储KeyPoint的StringId--intId
        self.keyPointIndexHashMap = deepcopy(staticMap.keyPointIndexHashMap)
        # 存储People的StringId--intId
        self.PeopleIndexHashMap = dict()
        # 存储 Point的intId--Point
        self.roadPointHashMap = deepcopy(staticMap.roadPointHashMap)
        # 存储 str((stratPointId, endPointId))--SegmentId
        self.segmentIndexHashMap = dict()
        # 存储 SegmentId--Segment
        self.segmentHashMap = dict()
        # 存储omsId--breakEventIdList
        self.breakEventIndexHashMap = dict()
        # 存储breakEventId--breakEvent
        self.breakEventHashMap = dict()
        # breakEvent速度查询表
        self.breakInfo = breakInfo

        # 对point进行的分区
        self.piece = deepcopy(staticMap.piece)
        # TODO 生成segment的时候计算每个散点的分区，并加入到每个分区的segmentSet中
        # 存储 DistrictCode--District
        self.districtHashMap = deepcopy(staticMap.districtHashMap)

        # 存储结果（非联通point）
        self.res = staticMap.res

        print("-------------------------- 清理数据 --------------------------")
        # 清空roadLine需要重新赋值的变量
        for _, roadLine in self.roadLineHashMap.items():
            roadLine.segmentList = []
            self.roadLineHashMap[roadLine.roadLineId] = roadLine
        # 清空point需要重新赋值的变量
        for _, point in self.roadPointHashMap.items():
            point.isKeyPoint = False
            point.isPeople = False
            point.roadLineSet = set()
            point.pointSet = set()
            point.segmentSet = set()
            self.roadPointHashMap[point.intId] = point
        self.printRoadLineAll(False)
        self.printKeyPointAll(False)
        self.printRoadPointAll(False)
        self.printSegmentAll(False)

        print("========================== dynamicMap已创建 ==========================")

    # 生成segment
    def generateSegment(self):
        segmentWithBreak = []
        if len(self.roadPointHashMap) == 0 or len(self.roadLineHashMap) == 0:
            raise Exception("无法建立segmentMap")

        # 遍历所有的roadLine
        for roadLineId, roadLine in self.roadLineHashMap.items():

            # 用于生成Segment的数据
            # roadLine的原始osmId
            osmId = roadLine.osmId
            # roadLine的限速
            speed = roadLine.speed
            if speed > 30:
                speed = 30
            # roadLine的宽度
            wide = roadLine.wide

            # 获取roadLine中的所有points与keyPoints，生成segment
            keyPointsList = self.getKeyPointsOfRoadLineOrSegment(roadLineId)
            pointsList = self.getPointsOfRoadLineOrSegment(roadLineId)
            # 设置循环索引
            keyPointsListIndex = 1
            # 设置需要存入segment的内容
            pointListOfSegment = [keyPointsList[0].intId]
            length = 0
            # 开始循环
            for pointsListIndex in range(1, len(pointsList)):
                # 将当前point添加到pointsList
                pointListOfSegment.append(pointsList[pointsListIndex].intId)
                dist = getDistanceMeter(pointsList[pointsListIndex - 1].coordinate,
                                        pointsList[pointsListIndex].coordinate)
                length += dist
                # 发现当前point为keyPoint,生成Segment
                if pointsList[pointsListIndex].intId == keyPointsList[keyPointsListIndex].intId:
                    # 生成segment
                    segment = Segment(roadLineId, osmId, speed, length, wide, pointListOfSegment[0],
                                      pointListOfSegment[-1],
                                      pointListOfSegment)
                    # 更新segment中的点信息
                    for i in range(0, len(segment.roadPointList)):
                        # 获取point的intId
                        pointId = segment.roadPointList[i]
                        # 获取point
                        point = self.roadPointHashMap[pointId]
                        # 设置KeyPoint属性
                        if i == 0 or i == len(segment.roadPointList) - 1:
                            point.isKeyPoint = True
                        # 添加相邻roadLine
                        point.roadLineSet.add(segment.roadLineId)
                        # 添加相邻segment
                        point.segmentSet.add(segment.segmentId)
                        # 添加相邻point
                        if i != 0:
                            point.pointSet.add(segment.roadPointList[i - 1])
                        if i != len(segment.roadPointList) - 1:
                            point.pointSet.add(segment.roadPointList[i + 1])
                        # 存入信息更新后的point
                        self.roadPointHashMap[pointId] = point
                    # 将segment信息添加到roadLine中
                    roadLine.segmentList.append(segment.segmentId)
                    # 存入segment
                    indexOfSegment = [segment.endPoint1Id, segment.endPoint2Id]
                    self.segmentIndexHashMap[str(indexOfSegment)] = segment.segmentId
                    self.segmentHashMap[segment.segmentId] = segment
                    # 更新循环信息，遍历segment中的下一个point
                    pointListOfSegment = [keyPointsList[keyPointsListIndex].intId]
                    keyPointsListIndex += 1
            # 存储信息更新后的roadLine
            self.roadLineHashMap[roadLineId] = roadLine

            # 如果道路涉及breakEvent
            if roadLine.osmId in self.breakEventIndexHashMap:
                breakEventIdList = self.breakEventIndexHashMap[roadLine.osmId]
                keyPointsOfRoadLine = self.getKeyPointsOfRoadLineOrSegment(roadLineId, onlyId=True)
                for breakEventId in breakEventIdList:
                    breakEvent = self.breakEventHashMap[breakEventId]
                    index1 = keyPointsOfRoadLine.index(breakEvent.roadPointList[0])
                    index2 = keyPointsOfRoadLine.index(breakEvent.roadPointList[1])
                    if index2 < index1:
                        temp = index2
                        index2 = index1
                        index1 = temp
                    for i in range(index1, index2):
                        segment = self.segmentHashMap[roadLine.segmentList[i]]
                        segment.breakEventList.append(breakEventId)
                        self.segmentHashMap[segment.segmentId] = segment
                        segmentWithBreak.append(segment.segmentId)
        print("··············带有break事件的segment有：" + str(segmentWithBreak) + "··············")
        for segmentId in segmentWithBreak:
            segment = self.segmentHashMap[segmentId]
            print(segment)

    # 计算Segment的通行时间
    def transTimeOfSegment(self, segmentId, currnetTime):
        segment = self.segmentHashMap[segmentId]
        length = segment.length
        speed = segment.speed
        transTime = length / speed
        breakEventIdList = segment.breakEventList
        # 如果没有breakEvent发生，则直接计算时间
        if len(breakEventIdList) == 0:
            return transTime
        # 如果有breakEvent发生，计算其通行时间（目前只能计算同时发生一个break事件的情况）
        for breakEventId in breakEventIdList:
            breakEvent = self.breakEventHashMap[breakEventId]
            if breakEvent.happendTime <= currnetTime <= breakEvent.happendTime + breakEvent.continueTime:
                breakSpeed = self.getSpeedInBreakEvent(breakEvent.breakType, breakEvent.breakLevel)
                if breakSpeed < speed:
                    speed = breakSpeed
                    if speed == 0:
                        return -1
                    transTime = length / speed
                    if currnetTime + transTime > breakEvent.happendTime + breakEvent.continueTime:
                        fastTime = currnetTime + transTime - breakEvent.happendTime + breakEvent.continueTime
                        transTime = transTime - fastTime
                        fastTime = fastTime * segment.speed
                        transTime += fastTime
        return transTime

    # 通过break信息查询通行速度
    def getSpeedInBreakEvent(self, BreakEvent):
        typeOfBreakEvent = BreakEvent.breakType
        level = BreakEvent.breakLevel
        return self.breakInfo.getSpeed(typeOfBreakEvent, level)

    # 获取point
    def getPoint(self, pointId):
        intId = -1
        if isinstance(pointId, str):
            intId = self.roadPointIndexHashMap[pointId]
        elif isinstance(pointId, int):
            intId = pointId
        if intId == -1:
            raise RuntimeError("getPoint()传入参数类型错误")
        return self.roadPointHashMap[intId]

    # 存入point
    def savePoint(self, point):
        self.roadPointIndexHashMap[point.stringId] = point.intId
        if point.isKeyPoint:
            self.keyPointIndexHashMap[point.stringId] = point.intId
        if point.isPeople:
            self.PeopleIndexHashMap[point.stringId] = point.intId
        self.roadPointHashMap[point.intId] = point

    # 存入breakEvent
    def saveBreakEvent(self, breakEvent):
        breakEvent.speed = self.breakInfo.getSpeed(breakEvent.breakType, breakEvent.breakLevel)
        if breakEvent.omsId not in self.breakEventIndexHashMap:
            breakEventIdList = [breakEvent.breakEventId]
        else:
            breakEventIdList = self.breakEventIndexHashMap[breakEvent.omsId]
            breakEventIdList.append(breakEvent.breakEventId)
        self.breakEventIndexHashMap[breakEvent.omsId] = breakEventIdList
        self.breakEventHashMap[breakEvent.breakEventId] = breakEvent

    # 打印所有存储在Map中的breakEventIndex
    def printBreakEventIndexAll(self, detail):
        if len(self.breakEventHashMap) == 0:
            print("··············map没有存储的breakEvent··············")
        else:
            if detail is True:
                print("··············map的breakEventIndex列表··············")
                for key in self.breakEventIndexHashMap:
                    print("omsId:" + str(key) + "\tbreakEventIdList:" + str(self.breakEventIndexHashMap[key]))
            print('··············map中breakEvent所在的omsId总数为：' + str(len(self.breakEventIndexHashMap)) + '··············')

    # 打印所有存储在Map中的breakEvent
    def printBreakEventAll(self, detail):
        if len(self.breakEventHashMap) == 0:
            print("··············map没有存储的breakEvent··············")
        else:
            if detail is True:
                print("··············map的breakEvent列表··············")
                for key in self.breakEventHashMap:
                    print(self.breakEventHashMap[key])
            print('··············map中breakEvent总数为：' + str(len(self.breakEventHashMap)) + '··············')

    # 获取roadLine或者segment
    def getRoadLineOrSegment(self, roadLineOrSegmentId):
        roadLineOrSegment = None
        # id是str类型，认为是roadLineId
        if isinstance(roadLineOrSegmentId, str):
            if roadLineOrSegmentId not in self.roadLineHashMap:
                raise RuntimeError("getRoadLineOrSegment()获取不到相应id的roadLine")
            roadLineOrSegment = self.roadLineHashMap[roadLineOrSegmentId]
        # id是int类型，认为是segment
        elif isinstance(roadLineOrSegmentId, int):
            if roadLineOrSegmentId not in self.segmentHashMap:
                raise RuntimeError("getRoadLineOrSegment()获取不到相应id的segment")
            roadLineOrSegment = self.segmentHashMap[roadLineOrSegmentId]
        return roadLineOrSegment

    # 对地图进行分区
    def getPiece(self, n_clusters=4):
        # 对Point进行K-means分类
        X = []
        for _, pointId in self.keyPointIndexHashMap.items():
            point = self.roadPointHashMap[pointId]
            if len(point.segmentSet) > 2:
                X.append(point.coordinate)
        molde = Cluster(X, n_clusters)
        return molde

    # 获取segment分区权重，用以算法使用
    def getWeightOfSegment(self, pointId1, pointId2):
        # segment = self.segmentHashMap[segmentId]
        point1 = self.roadPointHashMap[pointId1]
        point2 = self.roadPointHashMap[pointId2]
        return self.piece.predict(point1.coordinate, point2.coordinate)

    # 获取RoadLineOrSegment的StartPoint&EndPoint
    def getSEPointOfRoadLineOrSegment(self, roadLineOrSegmentId, onlyId=False, onlyCoordinates=False):
        sePointOfRoadLineOrSegment = []
        roadLineOrSegment = self.getRoadLineOrSegment(roadLineOrSegmentId)
        if onlyId:
            sePointOfRoadLineOrSegment.append(roadLineOrSegment.roadPointList[0])
            sePointOfRoadLineOrSegment.append(roadLineOrSegment.roadPointList[-1])
        elif onlyCoordinates:
            sePointOfRoadLineOrSegment.append(self.roadPointHashMap[roadLineOrSegment.roadPointList[0]].coordinate)
            sePointOfRoadLineOrSegment.append(self.roadPointHashMap[roadLineOrSegment.roadPointList[-1]].coordinate)
        else:
            sePointOfRoadLineOrSegment.append(self.roadPointHashMap[roadLineOrSegment.roadPointList[0]])
            sePointOfRoadLineOrSegment.append(self.roadPointHashMap[roadLineOrSegment.roadPointList[-1]])
        return sePointOfRoadLineOrSegment

    # 获取RoadLineOrSegment的KeyPoints
    def getKeyPointsOfRoadLineOrSegment(self, roadLineOrSegmentId, onlyId=False, onlyCoordinates=False):
        keyPointOfRoadLine = []
        roadLineOrSegment = self.getRoadLineOrSegment(roadLineOrSegmentId)
        for pointId in roadLineOrSegment.roadPointList:
            point = self.roadPointHashMap[pointId]
            if point.stringId in self.keyPointIndexHashMap:
                if onlyId:
                    keyPointOfRoadLine.append(pointId)
                elif onlyCoordinates:
                    keyPointOfRoadLine.append(point.coordinate)
                else:
                    keyPointOfRoadLine.append(point)
        return keyPointOfRoadLine

    # 获取RoadLineOrSegment的Points
    def getPointsOfRoadLineOrSegment(self, roadLineOrSegmentId, onlyCoordinates=False):
        pointOfRoadLine = []
        roadLineOrSegment = self.getRoadLineOrSegment(roadLineOrSegmentId)
        for pointId in roadLineOrSegment.roadPointList:
            if onlyCoordinates:
                pointOfRoadLine.append(self.roadPointHashMap[pointId].coordinate)
            else:
                pointOfRoadLine.append(self.roadPointHashMap[pointId])
        return pointOfRoadLine

    # 寻找地图中的点坐标在什么位置（待修改）
    def searchForPointId(self, coordinate):
        minDistance = float("inf")
        pointId = -1
        for k, v in self.roadPointHashMap.items():
            dis = getDistanceMeter(coordinate, v.coordinate)
            if dis < minDistance:
                minDistance = dis
                pointId = v.intId
        # 返回Point坐标
        return pointId

    # 打印每个RoadLine下所包含的PointList
    def printPointListOfRoadLines(self, detail):
        # 不存在RoadLine的情况
        if len(self.roadLineHashMap) == 0:
            print("··············StaticMap没有存储的RoadLine,无法打印PointList··············")
            return
        # 计数器，记录没有Point的RoadLine数量
        counter = 0
        # 循环遍历RoadLine
        for k, v in self.roadLineHashMap.items():
            # # （测试用）打印特定成员数的表
            # if len(v.roadPointList) > 0:
            #     continue

            # roadPointList的内容为空
            if len(v.roadPointList) == 0:
                print("\n·······RoadLine" + str(v.roadLineId) + "没有Point·······")
                counter += 1
                continue
            # roadPointList的内容不为空
            print("\n·······RoadLine" + str(v.roadLineId) + "的Point列表·······")
            for pointItem in v.roadPointList:
                print("Point[" + str(pointItem[0]) + "]\t交汇点坐标索引:" + str(pointItem[1]) + \
                      "\t坐标为" + str(self.roadPointHashMap[pointItem[0]].coordinate), end="")
                if not detail:
                    print()
                else:
                    roadPoint = self.roadPointHashMap[pointItem][0]
                    print(str(roadPoint))

            print("RoadLine: {0} 共有coordinate {1}个".format(str(v.roadLineId), str(len(v.coordinates))))
        print('没有交汇点的道路共有' + str(counter) + '条')
        return

    # 打印每个RoadLine下所包含的PointList
    def printSegmentListOfRoadLines(self, detail):
        # 不存在RoadLine的情况
        if len(self.roadLineHashMap) == 0:
            print("··············StaticMap没有存储的RoadLine,无法打印segment··············")
            return
        exceptionLineList = []
        # 循环遍历RoadLine
        for k, v in self.roadLineHashMap.items():
            # # （测试用）打印特定成员数的表
            # if len(v.roadSegmentList) > 0:
            #     continue
            # SegmentList的内容为空
            if len(v.segmentList) == 0:
                print("\n·······RoadLine" + str(v.roadLineId) + "没有segment·······")
                continue
            # segmentList的内容不为空
            print("\n·······RoadLine" + str(v.roadLineId) + "的segment列表·······")
            sumLength = 0
            for segmentId in v.segmentList:
                print("segment[" + str(segmentId) + "]", end="")
                if not detail:
                    segment = self.segmentHashMap[segmentId]
                    endPoint1 = self.roadPointHashMap[segment.endPoint1Id]
                    endPoint2 = self.roadPointHashMap[segment.endPoint2Id]
                    # print("起点 " + str(endPoint1.intId) + ":" + str(endPoint1.coordinate), end="")
                    # print("终点 " + str(endPoint2.intId) + ":" + str(endPoint2.coordinate), end="")
                    print("长度:" + str(segment.length), end="")
                    sumLength += segment.length
                    print()
                else:
                    segment = self.segmentHashMap[segmentId]
                    print(str(segment))
            print()

            lineLength = 0
            for i in range(1, len(v.coordinates)):
                dis = getDistanceMeter(v.coordinates[i - 1], v.coordinates[i])
                lineLength += dis

            print("segment总长度为：" + str(sumLength))
            print("roadLine总长度为：" + str(lineLength))
            print("omsId为" + str(v.osmId) + "的道路总长度为：" + str(v.length))
            print("omsId为" + str(v.osmId) + "的端点距离为：" + str(getDistanceMeter(v.coordinates[0], v.coordinates[-1])))

            print("RoadLine: {0} 共有segment {1}个 共有point {2}个".format(str(v.roadLineId), str(
                len(v.segmentList)), str(len(v.roadPointList))))

            if lineLength > (10 + v.length):
                exceptionLineList.append(v.osmId)

            if len(v.roadPointList) - 1 != len(v.segmentList):
                raise RuntimeError("道路分段出现问题")
        print("\nexceptionLineList" + str(exceptionLineList))
        return

    # 打印每个Point下所包含的RoadLineList
    def printRoadLineListOfPoints(self, detail):
        # 不存在Point的情况
        if len(self.roadPointHashMap) == 0:
            print("··············StaticMap没有存储的RoadPoint,无法打印RoadLineList··············")
            return
        # 遍历所有的Point
        for k, v in self.roadPointHashMap.items():
            # # （测试用）打印特定成员数的表
            # if len(v.roadLineList) > 2:
            #     continue

            # Point的roadLineList内容为空
            if len(v.roadLineList) == 0:
                print("\n·······Point[" + str(v.intId) + "]没有连接RoadLine·······")
                continue
            # Point的roadLineList内容不为空
            print("\n·······Point[" + str(v.intId) + "]的RoadLine列表·······")
            for RoadLineId in v.roadLineList:
                print("RoadLine：" + RoadLineId + "\t", end="")
                if not detail:
                    print()
                else:
                    roadLine = self.roadLineHashMap[RoadLineId]
                    print(str(roadLine))
        return

    # 打印所有存储在StaticMap中的RoadLine
    def printRoadLineAll(self, detail):
        if len(self.roadLineHashMap) == 0:
            print("··············StaticMap没有存储的RoadLine··············")
        else:
            if detail is True:
                print("··············StaticMap的RoadLine列表··············")
                for key in self.roadLineHashMap:
                    print(self.roadLineHashMap[key])
            print('··············StaticMap中RoadLine总数为：' + str(len(self.roadLineHashMap)) + '··············')

    # 打印所有存储在StaticMap中的RoadPoint
    def printRoadPointAll(self, detail):
        if len(self.roadLineHashMap) == 0:
            print("··············StaticMap没有存储的RoadPoint··············")
        else:
            if detail is True:
                print("··············StaticMap的RoadPoint列表··············")
                for key in self.roadPointHashMap:
                    point = self.roadPointHashMap[key]
                    if point.isKeyPoint:
                        print(point)
            print('··············StaticMap中RoadPoint总数为：' + str(len(self.roadPointHashMap)) + '··············')

    # 打印所有存储在StaticMap中的KeyPoint
    def printKeyPointAll(self, detail):
        if len(self.roadLineHashMap) == 0:
            print("··············StaticMap没有存储的KeyPoint··············")
        else:
            if detail is True:
                print("··············StaticMap的KeyPoint列表··············")
                for _, intId in self.keyPointIndexHashMap.items():
                    point = self.roadPointHashMap[intId]
                    print(point)
            print('··············StaticMap中KeyPoint总数为：' + str(len(self.keyPointIndexHashMap)) + '··············')

    # 打印所有存储在StaticMap中的RoadLine
    def printSegmentAll(self, detail):
        if len(self.segmentHashMap) == 0:
            print("··············StaticMap没有存储的Segment··············")
        else:
            if detail is True:
                print("··············StaticMap的Segment列表··············")
                for key in self.segmentHashMap:
                    print(self.segmentHashMap[key])
            print('··············StaticMap中Segment总数为：' + str(len(self.segmentHashMap)) + '··············')

    # 打印所有point的id与coordinate
    def printAllPointCoordinate(self):
        for key in self.roadPointHashMap:
            point = self.roadPointHashMap[key]
            print(str(point.intId) + " " + str(point.getLatitude()) + " " + str(point.getLongitude()))

    # 打印segment的邻接表
    def printAnswer(self):
        for key in self.segmentHashMap:
            segment = self.segmentHashMap[key]
            print(str(segment.endPoint1Id) + " " + str(segment.endPoint2Id) + " " + str(segment.length) + " " + str(
                segment.speed))
