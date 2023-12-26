from utils.MapsUtil import *
from maps.MapScale import MapScale
from maps.Segment import Segment
from utils.Clustering import *
from geohash import encode


# Map: 地图
class Map:

    # 初始化Map类
    def __init__(self) -> None:
        # 存储地图画幅大小，以便画图使用
        self.mapScale = MapScale()
        # 存储 roadLineId--roadLine
        self.roadLineHashMap = dict()
        # 存储 roadPoint的stringId--roadPointId
        self.roadPointIndexHashMap = dict()
        # 存储 keyPoint的stringId--roadPointId
        self.keyPointIndexHashMap = dict()
        # 存储 Point的id--Point
        self.roadPointHashMap = dict()
        # 存储 Segment的id--Segment
        self.segmentHashMap = dict()
        # 对point进行的分区
        self.piece = None
        # 存储 DistrictCode--District
        self.districtHashMap = dict()
        # 存储结果（非联通point）
        self.res = None

    # 尝试合并两条roadLine
    def mergeRoadLine(self, roadLine1, roadLine2):
        canMerge = False
        roadLine1FirstCoordinate = self.roadPointHashMap[roadLine1.roadPointList[0]].coordinate
        roadLine1LastCoordinate = self.roadPointHashMap[roadLine1.roadPointList[-1]].coordinate
        roadLine2FirstCoordinate = self.roadPointHashMap[roadLine2.roadPointList[0]].coordinate
        roadLine2LastCoordinate = self.roadPointHashMap[roadLine2.roadPointList[-1]].coordinate
        # roadLine1的最后一个坐标与roadLine2的第一个坐标相近
        if isClosePoint(roadLine1LastCoordinate, roadLine2FirstCoordinate):
            if roadLine1.roadPointList[-1] == roadLine2.roadPointList[0]:
                roadLine2.roadPointList.pop(0)
            canMerge = True

        # roadLine1的第一个坐标与roadLine2的最后一个坐标相近
        elif isClosePoint(roadLine1FirstCoordinate, roadLine2LastCoordinate):
            tempList = roadLine1.roadPointList
            roadLine1.roadPointList = roadLine2.roadPointList
            roadLine2.roadPointList = tempList
            if roadLine1.roadPointList[-1] == roadLine2.roadPointList[0]:
                roadLine2.roadPointList.pop(0)
            canMerge = True

        # roadLine1的最后一个坐标与roadLine2的最后一个坐标相近
        elif isClosePoint(roadLine1LastCoordinate, roadLine2LastCoordinate):
            roadLine2.roadPointList.reverse()
            if roadLine1.roadPointList[-1] == roadLine2.roadPointList[0]:
                roadLine2.roadPointList.pop(0)
            canMerge = True

        # roadLine1的第一个坐标与roadLine2的第一个坐标相近
        elif isClosePoint(roadLine1FirstCoordinate, roadLine2FirstCoordinate):
            roadLine1.roadPointList.reverse()
            if roadLine1.roadPointList[-1] == roadLine2.roadPointList[0]:
                roadLine2.roadPointList.pop(0)
            canMerge = True

        # 当两条roadLine需要合并，合并除了坐标点以外的其他属性
        if canMerge:
            roadLine1 = roadLine1.mergeRoadLine(roadLine2)
        return canMerge

    # 添加point信息到Line
    def addPointToLine(self, roadLineOrSegment, roadPoint):
        # 获取coordinateList
        coordinateList = self.getPointsOfRoadLineOrSegment(roadLineOrSegment.id, onlyCoordinates=True)
        # 查找点在roadLineOrSegment上的位置
        res = indexOfPoint(coordinateList, roadPoint.coordinate, roadLineOrSegment.wide)
        if res[0] is None:
            return False
        elif res[0] is False:
            roadLineOrSegment.addPoint(roadPoint.id, res[1])
            return True
        else:
            raise RuntimeError("需要添加到roadLine或者segment的道路点出现重合，addPointToRoadLine方法无法添加point")

    # 为生成segment初始化部分信息
    def initMapForSegment(self):
        # 清空self.segmentHashMap字典
        self.segmentHashMap = dict()
        # 清空roadLine需要重新赋值的变量
        for roadLine in self.roadLineHashMap.values():
            roadLine.initRoadLineForResegment()
            self.roadLineHashMap[roadLine.id] = roadLine
        # 清空point需要重新赋值的变量
        for point in self.roadPointHashMap.values():
            point.initPointForResegment()
            self.roadPointHashMap[point.id] = point

    # 生成segment
    def generateSegment(self):
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
                    self.segmentHashMap[segment.id] = segment
                    # 更新循环信息，遍历segment中的下一个point
                    pointListOfSegment = [keyPointsList[keyPointsListIndex].id]
                    keyPointsListIndex += 1
            # 存储信息更新后的roadLine
            self.roadLineHashMap[roadLineId] = roadLine

    # 检查连通性
    def checkConnection(self):
        return connectState(self)

    # 获取point
    def getPoint(self, pointId):
        id = -1
        if isinstance(pointId, str):
            id = self.roadPointIndexHashMap[pointId]
        elif isinstance(pointId, int):
            id = pointId
        if id == -1:
            raise RuntimeError("getPoint()传入参数类型错误")
        return self.roadPointHashMap[id]

    # 获取roadLine
    def getRoadLine(self, roadLineId):
        if roadLineId not in self.roadLineHashMap:
            raise RuntimeError("getRoadLine()传入参数类型错误")
        else:
            return self.roadLineHashMap[roadLineId]

    # 获取segment
    def getSegment(self, segmentId):
        if segmentId not in self.segmentHashMap:
            raise RuntimeError("getSegment()传入参数类型错误")
        else:
            return self.segmentHashMap[segmentId]
        
    # 存入point
    def savePoint(self, point):
        self.roadPointIndexHashMap[point.stringId] = point.id
        if point.isKeyPoint:
            self.keyPointIndexHashMap[point.stringId] = point.id
        self.roadPointHashMap[point.id] = point

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

    # 对地图进行k-means分区
    def getPiece(self, n_clusters=4):
        # 对Point进行K-means分类
        X = []
        for _, pointId in self.keyPointIndexHashMap.items():
            point = self.roadPointHashMap[pointId]
            if len(point.segmentList) > 2:
                X.append(point.coordinate)
        molde = Cluster(X, n_clusters)
        return molde

    # 获取segment的k-means分区权重，用以算法使用
    def getWeightOfSegment(self, pointId1, pointId2):
        point1 = self.roadPointHashMap[pointId1]
        point2 = self.roadPointHashMap[pointId2]
        return self.piece.predict(point1.coordinate, point2.coordinate)

    # 获取RoadLineOrSegment的StartPoint&EndPoint
    def getSEPointOfRoadLineOrSegment(self, roadLineOrSegment, onlyId=False, onlyCoordinates=False):
        sePointOfRoadLineOrSegment = []
        if isinstance(roadLineOrSegment, int) or isinstance(roadLineOrSegment, str):
            roadLineOrSegment = self.getRoadLineOrSegment(roadLineOrSegment)
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
    def getKeyPointsOfRoadLineOrSegment(self, roadLineOrSegment, onlyId=False, onlyCoordinates=False):
        keyPointOfRoadLine = []
        if isinstance(roadLineOrSegment, int) or isinstance(roadLineOrSegment, str):
            roadLineOrSegment = self.getRoadLineOrSegment(roadLineOrSegment)
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
    def getPointsOfRoadLineOrSegment(self, roadLineOrSegment, onlyCoordinates=False):
        pointOfRoadLine = []
        if isinstance(roadLineOrSegment, int) or isinstance(roadLineOrSegment, str):
            roadLineOrSegment = self.getRoadLineOrSegment(roadLineOrSegment)
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
        for point in self.roadPointHashMap.values():
            dis = getDistanceMeter(coordinate, point.coordinate)
            if dis < minDistance:
                minDistance = dis
                pointId = point.id
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
        for roadLine in self.roadLineHashMap.values():
            # # （测试用）打印特定成员数的表
            # if len(roadLine.roadPointList) > 0:
            #     continue

            # roadPointList的内容为空
            if len(roadLine.roadPointList) == 0:
                print("\n·······RoadLine" + str(roadLine.roadLineId) + "没有Point·······")
                counter += 1
                continue
            # roadPointList的内容不为空
            print("\n·······RoadLine" + str(roadLine.roadLineId) + "的Point列表·······")
            for pointItem in roadLine.roadPointList:
                print("Point[" + str(pointItem[0]) + "]\t交汇点坐标索引:" + str(pointItem[1]) + \
                      "\t坐标为" + str(self.roadPointHashMap[pointItem[0]].coordinate), end="")
                if not detail:
                    print()
                else:
                    roadPoint = self.roadPointHashMap[pointItem][0]
                    print(str(roadPoint))

            print("RoadLine: {0} 共有coordinate {1}个".format(str(roadLine.roadLineId), str(len(roadLine.coordinates))))
        print('没有交汇点的道路共有' + str(counter) + '条')
        return

    # （待检查）打印每个RoadLine下所包含的PointList
    def printSegmentListOfRoadLines(self, detail):
        # 不存在RoadLine的情况
        if len(self.roadLineHashMap) == 0:
            print("··············Map没有存储的RoadLine,无法打印segment··············")
            return
        exceptionLineList = []
        # 循环遍历RoadLine
        for roadLine in self.roadLineHashMap.values():
            # # （测试用）打印特定成员数的表
            # if roadLine.id != 1263:
            #     continue
            # SegmentList的内容为空
            if len(roadLine.segmentList) == 0:
                print("\n·······RoadLine" + str(roadLine.roadLineId) + "没有segment·······")
                continue
            # segmentList的内容不为空
            print("\n·······RoadLine" + str(roadLine.roadLineId) + "的segment列表·······")
            sumLength = 0
            for segmentId in roadLine.segmentList:
                print("segment[" + str(segmentId) + "]", end="")
                if not detail:
                    print()
                else:
                    # 打印segment长度
                    segment = self.segmentHashMap[segmentId]
                    print("长度:" + str(segment.length))
                    sumLength += segment.length
                    print(str(segment))
            print()

            lineLength = 0
            for i in range(1, len(roadLine.coordinates)):
                dis = getDistanceMeter(roadLine.coordinates[i - 1], roadLine.coordinates[i])
                lineLength += dis

            print("segment总长度为：" + str(sumLength))
            print("roadLine总长度为：" + str(lineLength))
            print("omsId为" + str(roadLine.osmId) + "的道路总长度为：" + str(roadLine.length))
            print("omsId为" + str(roadLine.osmId) + "的端点距离为：" + str(getDistanceMeter(roadLine.coordinates[0], roadLine.coordinates[-1])))

            print("RoadLine: {0} 共有segment {1}个 共有point {2}个".format(str(roadLine.roadLineId), str(
                len(roadLine.segmentList)), str(len(roadLine.roadPointList))))

            if lineLength > (10 + roadLine.length):
                exceptionLineList.append(roadLine.osmId)

            if len(roadLine.roadPointList) - 1 != len(roadLine.segmentList):
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
        for roadPoint in self.roadPointHashMap.values():
            # # （测试用）打印特定成员数的表
            # if len(roadPoint.roadLineList) > 2:
            #     continue

            # Point的roadLineList内容为空
            if len(roadPoint.roadLineList) == 0:
                print("\n·······Point[" + str(roadPoint.id) + "]没有连接RoadLine·······")
                continue
            # Point的roadLineList内容不为空
            print("\n·······Point[" + str(roadPoint.id) + "]的RoadLine列表·······")
            for RoadLineId in roadPoint.roadLineList:
                print("RoadLine：" + RoadLineId + "\t", end="")
                if not detail:
                    print()
                else:
                    roadLine = self.roadLineHashMap[RoadLineId]
                    print(str(roadLine))
        return

    # 打印所有存储在Map中的RoadLine
    def printRoadLineAll(self, detail):
        if len(self.roadLineHashMap) == 0:
            print("··············Map没有存储的RoadLine··············")
        else:
            if detail is True:
                print("··············Map的RoadLine列表··············")
                for roadLine in self.roadLineHashMap.values():
                    print(roadLine)
            print('··············Map中RoadLine总数为：' + str(len(self.roadLineHashMap)) + '··············')

    # 打印所有存储在Map中的RoadPoint
    def printRoadPointAll(self, detail):
        if len(self.roadLineHashMap) == 0:
            print("··············Map没有存储的RoadPoint··············")
        else:
            if detail is True:
                print("··············Map的RoadPoint列表··············")
                for point in self.roadPointHashMap.values():
                    if len(point.peopleList) > 1:
                        print(point)
            print('··············Map中RoadPoint总数为：' + str(len(self.roadPointHashMap)) + '··············')

    # 打印所有存储在Map中的KeyPoint
    def printKeyPointAll(self, detail):
        if len(self.roadLineHashMap) == 0:
            print("··············Map没有存储的KeyPoint··············")
        else:
            if detail is True:
                print("··············Map的KeyPoint列表··············")
                for pointId in self.keyPointIndexHashMap.values():
                    point = self.roadPointHashMap[pointId]
                    print(point)
            print('··············Map中KeyPoint总数为：' + str(len(self.keyPointIndexHashMap)) + '··············')

    # 打印所有存储在Map中的RoadLine
    def printSegmentAll(self, detail):
        if len(self.segmentHashMap) == 0:
            print("··············Map没有存储的Segment··············")
        else:
            if detail is True:
                print("··············Map的Segment列表··············")
                for segment in self.segmentHashMap.values():
                    print(segment)
            print('··············Map中Segment总数为：' + str(len(self.segmentHashMap)) + '··············')

    # 打印所有point的id与coordinate
    def printAllPointCoordinate(self):
        for point in self.roadPointHashMap.values():
            print(str(point.id) + " " + str(point.getLatitude()) + " " + str(point.getLongitude()))

    # 打印segment的邻接表
    def printAnswer(self):
        for segment in self.segmentHashMap.values():
            print(str(segment.endPoint1Id) + " " + str(segment.endPoint2Id) + " " + str(segment.length) + " " + str(
                segment.speed))

    # 进行geohash分区
    def generateDistrict(self):
        for point in self.roadPointHashMap.values():
            segmentList = point.segmentList
            code = encode(point.getLatitude(), point.getLongitude(), 7)
            if code not in self.districtHashMap:
                self.districtHashMap[code] = set()
            for segmentId in segmentList:
                self.districtHashMap[code].add(segmentId)
