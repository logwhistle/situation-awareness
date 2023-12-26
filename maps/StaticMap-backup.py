import json

from geohash import encode
from maps.MapScale import MapScale
from maps.RoadLine import RoadLine
from maps.RoadPoint import RoadPoint
from maps.Segment import Segment
from utils.MapsUtil import *
from utils.Clustering import *


# StaticMap: 静态地图
class StaticMap:

    # 初始化StaticMap类
    def __init__(self, rootAddress) -> None:
        print("\n========================== 开始生成staticMap ==========================")
        # 存储地图画幅大小，以便画图使用
        self.mapScale = MapScale()
        # 存储 RoadLineId--RoadLine
        self.roadLineHashMap = dict()
        # 存储 RoadPoint的StringId--intId
        self.roadPointIndexHashMap = dict()
        # 存储KeyPoint的StringId--intId
        self.keyPointIndexHashMap = dict()
        # 存储 Point的intId--Point
        self.roadPointHashMap = dict()
        # 存储 SegmentId--Segment
        self.segmentHashMap = dict()
        # 对point进行的分区
        self.piece = None
        # 存储 DistrictCode--District
        self.districtHashMap = dict()
        # 存储结果（非联通point）
        self.res = None

        # 存入RoadLine
        print("-------------------------- 存入RoadLine --------------------------")
        self.addRoadLineAll(rootAddress + 'map\\RoadLine.json')
        self.printRoadLineAll(False)
        self.printKeyPointAll(False)
        self.printRoadPointAll(False)

        # 存入RoadPoint
        print("-------------------------- 存入RoadPoint --------------------------")
        self.addRoadPointAll(rootAddress + 'map\\RoadPoint.json')
        self.printRoadLineAll(False)
        self.printKeyPointAll(False)
        self.printRoadPointAll(False)

        # 生成segment
        print("-------------------------- 生成segment --------------------------")
        self.generateSegment()
        self.printRoadLineAll(False)
        self.printKeyPointAll(False)
        self.printRoadPointAll(False)
        self.printSegmentAll(False)

        # 检查连通性
        print("-------------------------- 检查连通性 --------------------------")
        self.res = self.checkConnection()

        # 删除不连通roadLine
        print("-------------------------- 删除不连通的roadLine --------------------------")

        self.printRoadLineAll(False)
        self.printKeyPointAll(False)
        self.printRoadPointAll(False)
        self.printSegmentAll(False)

        # 进行geohash分区
        self.generateDistrict()
        # point进行k-means分区
        self.piece = self.getPiece(4)

        print("========================== staticMap已生成 ==========================")

    # 添加所有roadLine信息
    def addRoadLineAll(self, roadLineFileAddress):
        # 读取Json文件
        with open(roadLineFileAddress, "r", encoding="utf-8") as f:
            # 读入RoadLine表存储为 roadLineList
            roadLineList = json.load(f)
            # 循环遍历RoadLine字典生成RoadLine类
            for roadLineDic in roadLineList:

                # 读出roadLine的coordinates生成point对象
                origCoordinatesList = roadLineDic["geometry"]["coordinates"]
                # 生成roadPointList,点的数目小于2个时返回None
                roadPointList = self.generateRoadPointList(roadLineDic["properties"]["osm_id"], origCoordinatesList)
                # 点的数目小于两个则不生成roadLine对象
                if roadPointList is None:
                    continue

                # 生成roadLine对象
                roadLine = RoadLine(roadLineDic, roadPointList)
                # 当RoadLine的Id重复，则重复次数加一并更新Id
                while roadLine.roadLineId in self.roadLineHashMap:
                    # Step1：尝试拼接路段
                    oldRoadLine = self.roadLineHashMap[roadLine.roadLineId]
                    # 如果拼接成功
                    if self.mergeRoadLine(oldRoadLine, roadLine):
                        roadLine = oldRoadLine
                        break
                    # Step2：无法拼接，则重复次数加一并更新Id
                    roadLine.repetited()
                # 重新存入roadLine
                self.roadLineHashMap[roadLine.roadLineId] = roadLine

    # 通过道路中的坐标点生成point对象
    def generateRoadPointList(self, omsId, origCoordinatesList):
        # 存储roadLine包含的roadPoint对象
        roadPointList = []
        # 循环遍历坐标点
        for origCoordinate in origCoordinatesList:
            # 调换经纬度位置
            coordinate = [origCoordinate[1], origCoordinate[0]]
            # 更新地图大小
            self.mapScale.refreshScale(coordinate)
            # 生成roadPoint对象
            roadPoint = RoadPoint(coordinate=coordinate)
            # 判断此点坐标是否已存在
            if roadPoint.stringId not in self.roadPointIndexHashMap:
                # 不存在，则生成intId并存储id索引
                self.roadPointIndexHashMap[roadPoint.stringId] = roadPoint.setRoadPointIntId()
            else:
                # 已存在，则读出原有的点
                roadPoint = self.roadPointHashMap[self.roadPointIndexHashMap[roadPoint.stringId]]
            # 添加roadLine的omsId信息到point中
            roadPoint.omsIdSet.add(omsId)
            # 将roadPoint添加到HashMap
            self.roadPointHashMap[roadPoint.intId] = roadPoint
            # 与上一个point重复，则不添加到roadPointList
            if len(roadPointList) == 0 or roadPointList[-1] != roadPoint.intId:
                roadPointList.append(roadPoint.intId)
        # roadLine中point的数目小于2时，则返回None
        if len(roadPointList) < 2:
            return None
        # roadLine中point的数目大于2时，将端点存入KeyPointIndex中，返回point的intId序列
        endPoint1 = self.roadPointHashMap[roadPointList[0]]
        endPoint2 = self.roadPointHashMap[roadPointList[-1]]
        self.keyPointIndexHashMap[endPoint1.stringId] = endPoint1.intId
        self.keyPointIndexHashMap[endPoint2.stringId] = endPoint2.intId
        return roadPointList

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
            roadLine1.roadPointList += roadLine2.roadPointList
            #     # 合并roadPointList与segmentList
            #     self.roadPointList.append(roadLine.roadPointList)
            #     self.segmentList.append(roadLine.segmentList)
            return roadLine1
        return None

    # 添加所有roadPoint信息
    def addRoadPointAll(self, roadPointFileAddress):
        # 读取Json文件
        with open(roadPointFileAddress, "r", encoding="utf-8") as f:
            # 读入RoadPoint表存储为 roadPointList
            roadPointList = json.load(f)
            # 循环遍历RoadPoint字典生成RoadPoint类
            for roadPointDic in roadPointList:
                # 生成RoadPoint类的对象
                roadPoint = RoadPoint(roadPointDic)
                # 与roadPoint相连的roadLine的omsId表
                roadLineList = [roadPointDic["properties"]["osm_id"], roadPointDic["properties"]["osm_id_2"]]
                # Step1:去重
                # 当相同坐标的点还未存储到roadPointIndexHashMap中
                if roadPoint.stringId not in self.roadPointIndexHashMap:
                    # 为roadPoint赋intId
                    roadPoint.setRoadPointIntId()
                    # 先将RoadPointId存入Id索引表
                    self.roadPointIndexHashMap[roadPoint.stringId] = roadPoint.intId
                # 当相同坐标的点已经存储到roadPointIndexHashMap中
                else:
                    # 取出原有的点oldRoadPoint
                    oldRoadPoint = self.roadPointHashMap[self.roadPointIndexHashMap[roadPoint.stringId]]
                    # 合并相同stringId的Point并存入roadPointHashMap
                    roadPoint = oldRoadPoint.mergePoint(roadPoint)
                # Step2:与RoadLine交互
                # 用以存储RoadLineId
                for omsId in roadLineList:
                    # 把omsId添加到roadPoint
                    if omsId not in roadPoint.omsIdSet:
                        roadPoint.omsIdSet.add(omsId)
                    # 分别循环遍历重复omsId的RoadLine
                    for j in range(0, 9):
                        # RoadLine的Id
                        roadLineId = str(omsId) + '/' + str(j)
                        # 不存在相应Id的RoadLine，说明已经没有未遍历的此omsId的道路
                        if roadLineId not in self.roadLineHashMap:
                            break
                        # 取出相应Id的RoadLine
                        roadLine = self.roadLineHashMap[roadLineId]
                        # 如果此Id已经存在于roadLine的roadPointList
                        if roadPoint.intId in roadLine.roadPointList:
                            continue
                        # 将point信息存入roadLine的roadPointList中
                        self.addPointToRoadLine(roadLine, roadPoint)
                # Step3:存储Point
                # 将point添加到KeyPoint索引
                self.keyPointIndexHashMap[roadPoint.stringId] = roadPoint.intId
                # 将Point放入roadPointHashMap
                self.roadPointHashMap[roadPoint.intId] = roadPoint

    # 添加point信息到roadLine
    def addPointToRoadLine(self, roadLineOrSegment, roadPoint):
        # 获取coordinateList
        coordinateList = []
        for pointId in roadLineOrSegment.roadPointList:
            coordinateList.append(self.roadPointHashMap[pointId].coordinate)
        # 查找点在roadLineOrSegment上的位置
        res = indexOfPoint(coordinateList, roadPoint.coordinate, roadLineOrSegment.wide)
        if res[0] is None:
            return False
        elif res[0] is False:
            roadLineOrSegment.addPoint(roadPoint.intId, res[1])
        else:
            raise RuntimeError("需要添加到roadLine或者segment的道路点出现重合，addPointToRoadLine方法无法添加point")

    # 生成segment
    def generateSegment(self):
        if len(self.roadPointHashMap) == 0 or len(self.roadLineHashMap) == 0:
            raise Exception("无法建立segmentMap")
        # 已有数据，需要重新刷新数据
        if len(self.segmentHashMap) != 0:
            # 清空self.segmentHashMap字典
            self.segmentHashMap = dict()
            # 清空roadLine需要重新赋值的变量
            for _, roadLine in self.roadLineHashMap.items():
                roadLine.segmentList = []
                self.roadLineHashMap[roadLine.roadLineId] = roadLine
            # 清空point需要重新赋值的变量
            for _, point in self.roadPointHashMap.items():
                point.isKeyPoint = False
                point.isPeopel = False
                point.roadLineSet = set()
                point.pointSet = set()
                point.segmentSet = set()
                self.roadPointHashMap[point.intId] = point

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
                dist = getDistanceMeter(pointsList[pointsListIndex-1].coordinate, pointsList[pointsListIndex].coordinate)
                length += dist
                # 发现当前point为keyPoint,生成Segment
                if pointsList[pointsListIndex].intId == keyPointsList[keyPointsListIndex].intId:
                    # 生成segment
                    segment = Segment(roadLineId, osmId, speed, length, wide, pointListOfSegment[0], pointListOfSegment[-1],
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
                    self.segmentHashMap[segment.segmentId] = segment
                    # 更新循环信息，遍历segment中的下一个point
                    pointListOfSegment = [keyPointsList[keyPointsListIndex].intId]
                    keyPointsListIndex += 1
            # 存储信息更新后的roadLine
            self.roadLineHashMap[roadLineId] = roadLine

    # 检查连通性
    def checkConnection(self):
        return connectState(self)

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

    # 进行geohash分区
    def generateDistrict(self):
        for point in self.roadPointHashMap.values():
            segmentSet = point.segmentSet
            code = encode(point.getLatitude(), point.getLongitude(), 7)
            if code not in self.districtHashMap:
                self.districtHashMap[code] = set()
            for segmentId in segmentSet:
                self.districtHashMap[code].add(segmentId)