from interface.Map import *
from copy import deepcopy


# DynamicMap: 静态地图
class DynamicMap(Map):

    # 初始化DynamicMap类
    def __init__(self, staticMap, breakInfo) -> None:
        print("\n========================== 开始创建dynamicMap ==========================")
        super().__init__()
        # 存储地图画幅大小，以便画图使用
        self.mapScale = deepcopy(staticMap.mapScale)
        # 存储 RoadLineId--RoadLine
        self.roadLineHashMap = deepcopy(staticMap.roadLineHashMap)
        # 存储 RoadPoint的StringId--intId
        self.roadPointIndexHashMap = deepcopy(staticMap.roadPointIndexHashMap)
        # 存储 KeyPoint的StringId--intId
        self.keyPointIndexHashMap = deepcopy(staticMap.keyPointIndexHashMap)
        # 存储 initPointStringId--initPointIntId
        self.initPointIndexHashMap = dict()
        # 存储 Point的intId--Point
        self.roadPointHashMap = deepcopy(staticMap.roadPointHashMap)
        # 存储 segment的 str((stratPointId, endPointId))--id
        self.segmentIndexHashMap = dict()
        # 存储 segment的 id--Segment
        self.segmentHashMap = dict()
        # 存储 omsId--breakEventId
        self.breakEventIndexHashMap = dict()
        # newBreak事件发生的时间
        self.newBreakStartTime = None
        # 存储 omsId--newBreakEventId
        self.newBreakEventIndexHashMap = dict()
        # 存储 breakEventId--breakEvent
        self.breakEventHashMap = dict()
        # breakEvent速度查询表
        self.breakInfo = breakInfo
        # 存储 placePointId--placePoint
        self.placePointHashMap = dict()
        # 存储 pointId--peopleIdList
        self.peopleIndexHashMap = dict()
        # 存储 peopleId--people
        self.peopleHashMap = dict()

        # 对point进行的分区
        self.piece = deepcopy(staticMap.piece)
        # TODO 生成segment的时候计算每个散点的分区，并加入到每个分区的segmentSet中
        # 存储 DistrictCode--District
        self.districtHashMap = deepcopy(staticMap.districtHashMap)

        # 存储结果（非联通point）
        self.res = staticMap.res

        print("-------------------------- 清理数据 --------------------------")
        self.initMapForSegment()
        self.printRoadLineAll(False)
        self.printKeyPointAll(False)
        self.printRoadPointAll(False)
        self.printSegmentAll(False)

        print("========================== dynamicMap已创建 ==========================")

    # 生成segment
    def generateSegment(self, isNew=False):
        segmentWithBreak = []

        if len(self.roadPointHashMap) == 0 or len(self.roadLineHashMap) == 0:
            raise Exception("无法建立segmentMap")

        # 已有数据，需要重新刷新数据
        if len(self.segmentHashMap) != 0:
            self.initMapForSegment()

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
            pointListOfSegment = [keyPointsList[0].id]
            length = 0
            # 开始循环
            for pointsListIndex in range(1, len(pointsList)):
                # 将当前point添加到pointsList
                pointListOfSegment.append(pointsList[pointsListIndex].id)
                dist = getDistanceMeter(pointsList[pointsListIndex - 1].coordinate,
                                        pointsList[pointsListIndex].coordinate)
                length += dist
                # 发现当前point为keyPoint,生成Segment
                if pointsList[pointsListIndex].id == keyPointsList[keyPointsListIndex].id:
                    # 生成segment
                    segment = Segment(roadLineId=roadLineId,
                                      osmId=osmId,
                                      length=length,
                                      wide=wide,
                                      speed=speed,
                                      endPoint1Id=pointListOfSegment[0],
                                      endPoint2Id=pointListOfSegment[-1],
                                      roadPointList=pointListOfSegment)
                    length = 0
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
                        point.addRoadLine(segment.roadLineId)
                        # 添加相邻segment
                        point.addSegment(segment.id)
                        # 添加相邻point
                        if i != 0:
                            point.addPoint(segment.roadPointList[i - 1])
                        if i != len(segment.roadPointList) - 1:
                            point.addPoint(segment.roadPointList[i + 1])
                        # 存入信息更新后的point
                        self.roadPointHashMap[pointId] = point
                    # 将segment信息添加到roadLine中
                    roadLine.segmentList.append(segment.id)
                    # 存入segment
                    indexOfSegment = [segment.endPoint1Id, segment.endPoint2Id]
                    self.segmentIndexHashMap[str(indexOfSegment)] = segment.id
                    self.segmentHashMap[segment.id] = segment
                    # 更新循环信息，遍历segment中的下一个point
                    pointListOfSegment = [keyPointsList[keyPointsListIndex].id]
                    keyPointsListIndex += 1
            # 存储信息更新后的roadLine
            self.roadLineHashMap[roadLineId] = roadLine
            if isNew is False:
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
                            self.segmentHashMap[segment.id] = segment
                            segmentWithBreak.append(segment.id)
            if isNew is True:
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
                            segment.oldBreakEventList.append(breakEventId)
                            self.segmentHashMap[segment.id] = segment
                            segmentWithBreak.append(segment.id)
                # 如果道路涉及newBreakEvent
                if roadLine.osmId in self.newBreakEventIndexHashMap:
                    newBreakEventIdList = self.newBreakEventIndexHashMap[roadLine.osmId]
                    keyPointsOfRoadLine = self.getKeyPointsOfRoadLineOrSegment(roadLineId, onlyId=True)
                    for newBreakEventId in newBreakEventIdList:
                        newBreakEvent = self.breakEventHashMap[newBreakEventId]
                        index1 = keyPointsOfRoadLine.index(newBreakEvent.roadPointList[0])
                        index2 = keyPointsOfRoadLine.index(newBreakEvent.roadPointList[1])
                        if index2 < index1:
                            temp = index2
                            index2 = index1
                            index1 = temp
                        for i in range(index1, index2):
                            segment = self.segmentHashMap[roadLine.segmentList[i]]
                            segment.breakEventList.append(newBreakEventId)
                            self.segmentHashMap[segment.id] = segment
                            segmentWithBreak.append(segment.id)
        print("··············带有break事件的segment有：" + str(segmentWithBreak) + "··············")
        for segmentId in segmentWithBreak:
            segment = self.segmentHashMap[segmentId]
            print(segment)

    # 计算Segment的通行时间
    def transTimeOfSegment(self, segment, currentTime):
        if isinstance(segment, int) or isinstance(segment, list):
            segment = self.getSegment(segment)
        length = segment.length
        speed = segment.speed
        transTime = length / speed
        breakEventIdList = segment.breakEventList
        # 如果没有breakEvent发生，则直接计算时间
        if len(breakEventIdList) == 0:
            return transTime
        # 如果有breakEvent发生，计算其通行时间
        transTime = 0
        coordinates = self.getPointsOfRoadLineOrSegment(roadLineOrSegment=segment, onlyCoordinates=True)
        curSpeed = self.speedOfSegment(segment=segment, currentTime=currentTime)
        for i in range(1, len(coordinates)):
            dis = getDistanceMeter(coordinates[i-1], coordinates[i])
            curSpeed = self.speedOfSegment(segment=segment, currentTime=currentTime)
            curTransTime = dis/curSpeed
            transTime += curTransTime
            currentTime += curTransTime
        return transTime

    # 计算Segment的通行速度
    def speedOfSegment(self, segment, currentTime):
        if isinstance(segment, int) or isinstance(segment, list):
            segment = self.getSegment(segment)
        # 原始同行速度
        speed = segment.speed
        # break事件表
        breakEventIdList = segment.breakEventList
        # 如果没有breakEvent发生，则直接返回速度
        if len(breakEventIdList) == 0:
            return speed
        # 如果有breakEvent发生，查询其通行速度（目前只能计算同时发生一个break事件的情况）
        for breakEventId in breakEventIdList:
            breakEvent = self.breakEventHashMap[breakEventId]
            # 如果是newBreak
            if breakEvent.isNew:
                happendTime = breakEvent.happendTime
                if self.newBreakStartTime is not None:
                    happendTime = self.newBreakStartTime
                endTime =happendTime + breakEvent.continueTime
                if happendTime <= currentTime <= endTime:
                    breakSpeed = self.getSpeedInBreakEvent(breakEvent)
                    if breakSpeed < speed:
                        speed = breakSpeed
            # 如果不是newBreak
            else:
                happendTime = breakEvent.happendTime
                endTime = happendTime + breakEvent.continueTime
                if self.newBreakStartTime is not None and self.newBreakStartTime < endTime:
                    endTime = self.newBreakStartTime
                if happendTime <= currentTime <= endTime:
                    breakSpeed = self.getSpeedInBreakEvent(breakEvent)
                    if breakSpeed < speed:
                        speed = breakSpeed
        return speed

    # 获取segment
    def getSegment(self, segmentId):
        if isinstance(segmentId, list):
            segmentIdIndex1 = str(segmentId)
            segmentIdIndex2 = str([segmentId[1], segmentId[0]])
            segmentId = None
            if segmentIdIndex1 in self.segmentIndexHashMap:
                segmentId = self.segmentIndexHashMap[segmentIdIndex1]
            if segmentIdIndex2 in self.segmentIndexHashMap:
                segmentId = self.segmentIndexHashMap[segmentIdIndex2]
            if segmentId is None:
                return None
        return super(DynamicMap, self).getSegment(segmentId)

    # 通过break信息查询通行速度
    def getSpeedInBreakEvent(self, BreakEvent):
        typeOfBreakEvent = BreakEvent.breakType
        level = BreakEvent.breakLevel
        return self.breakInfo.getSpeed(typeOfBreakEvent, level)

    # 存入breakEvent
    def saveBreakEvent(self, breakEvent, new=False):
        breakEvent.speed = self.breakInfo.getSpeed(breakEvent.breakType, breakEvent.breakLevel)
        # 非newBreak
        if not new:
            # break信息的omsId不在索引中
            if breakEvent.omsId not in self.breakEventIndexHashMap:
                breakEventIdList = [breakEvent.breakEventId]
            # break信息的omsId在索引中
            else:
                breakEventIdList = self.breakEventIndexHashMap[breakEvent.omsId]
                breakEventIdList.append(breakEvent.breakEventId)
            self.breakEventIndexHashMap[breakEvent.omsId] = breakEventIdList
        # 是newBreak
        else:
            # newBreak信息的omsId不在索引中
            if breakEvent.omsId not in self.newBreakEventIndexHashMap:
                breakEventIdList = [breakEvent.breakEventId]
            # newBreak信息的omsId在索引中
            else:
                breakEventIdList = self.newBreakEventIndexHashMap[breakEvent.omsId]
                breakEventIdList.append(breakEvent.breakEventId)
            self.newBreakEventIndexHashMap[breakEvent.omsId] = breakEventIdList
        # 存入break信息
        self.breakEventHashMap[breakEvent.breakEventId] = breakEvent

    # 存入point
    def savePoint(self, point):
        self.roadPointIndexHashMap[point.stringId] = point.id
        if point.isKeyPoint:
            self.keyPointIndexHashMap[point.stringId] = point.id
        self.roadPointHashMap[point.id] = point

    # 打印segment的通行时间
    def printTransTimeOfSegment(self, currentTime = 0):
        for segment in self.segmentHashMap.values():
            speed = self.speedOfSegment(segment=segment, currentTime=currentTime)
            print('整体通行时间：' + str(segment.length/speed))
            coordinates = self.getPointsOfRoadLineOrSegment(roadLineOrSegment=segment, onlyCoordinates=True)
            transTime = self.speedOfSegment(segment=segment, currentTime=currentTime)


    # 打印所有存储在Map中的breakEventIndex
    def printBreakEventIndexAll(self, detail):
        if len(self.breakEventIndexHashMap) == 0:
            print("··············map没有存储的breakEvent··············")
        else:
            if detail is True:
                print("··············map的breakEventIndex列表··············")
                for key in self.breakEventIndexHashMap:
                    print("omsId:" + str(key) + "\tbreakEventIdList:" + str(self.breakEventIndexHashMap[key]))
            print('··············map中breakEvent所在的omsId总数为：' + str(len(self.breakEventIndexHashMap)) + '··············')

    # 打印所有存储在Map中的newBreakEventIndex
    def printNewBreakEventIndexAll(self, detail):
        if len(self.newBreakEventIndexHashMap) == 0:
            print("··············map没有存储的newBreakEvent··············")
        else:
            if detail is True:
                print("··············map的newBreakEventIndex列表··············")
                for key in self.newBreakEventIndexHashMap:
                    print("omsId:" + str(key) + "\tnewBreakEventIdList:" + str(self.newBreakEventIndexHashMap[key]))
            print('··············map中breakEvent所在的omsId总数为：' + str(
                len(self.newBreakEventIndexHashMap)) + '··············')

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

    # 打印所有存储在Map中的breakEvent
    def printPlacePointAll(self, detail):
        if len(self.placePointHashMap) == 0:
            print("··············map没有存储的placePoint··············")
        else:
            if detail is True:
                print("··············map的placePoint列表··············")
                for key in self.placePointHashMap:
                    print(self.placePointHashMap[key])
            print('··············map中placePoint总数为：' + str(len(self.placePointHashMap)) + '··············')

    # 打印所有存储在Map中的peopleIndex
    def printPeopleIndexAll(self, detail):
        if len(self.peopleIndexHashMap) == 0:
            print("··············map没有存储的people··············")
        else:
            if detail is True:
                print("··············map的peopleIndex列表··············")
                for key in self.peopleIndexHashMap:
                    print("pointId:" + str(key) + "\tpeopleIdList:" + str(self.peopleIndexHashMap[key]))
            print('··············map中people所在的point总数为：' + str(
                len(self.peopleIndexHashMap)) + '··············')

    # 打印所有存储在Map中的people
    def printPeopleAll(self, detail):
        if len(self.peopleHashMap) == 0:
            print("··············map没有存储的people··············")
        else:
            if detail is True:
                print("··············map的people列表··············")
                for key in self.peopleHashMap:
                    print(self.peopleHashMap[key])
            print('··············map中people总数为：' + str(len(self.peopleHashMap)) + '··············')

