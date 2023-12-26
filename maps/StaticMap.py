from interface.Map import *
import json
from maps.RoadLine import *
from maps.RoadPoint import *



# StaticMap: 静态地图
class StaticMap(Map):

    # 初始化StaticMap类
    def __init__(self, rootAddress) -> None:
        print("\n========================== 开始生成staticMap ==========================")
        super(StaticMap, self).__init__()

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
        self.printRoadLineAll(True)
        self.printKeyPointAll(False)
        self.printRoadPointAll(False)
        self.printSegmentAll(False)

        # 检查连通性
        print("-------------------------- 检查连通性 --------------------------")
        self.res = self.checkConnection()

        # 删除不连通roadLine
        print("-------------------------- 删除不连通的roadLine --------------------------")
        self.deleteDisconnectedMap()
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
            for roadLineJson in roadLineList:

                # 读出roadLine的coordinates生成point对象
                origCoordinatesList = roadLineJson["geometry"]["coordinates"]
                # 生成roadPointList,点的数目小于2个时返回None
                roadPointList = self.generateRoadPointList(roadLineJson["properties"]["osm_id"], origCoordinatesList)
                # 点的数目小于两个则不生成roadLine对象
                if roadPointList is None:
                    continue

                # 生成roadLine对象
                roadLine = RoadLine(roadLineJson=roadLineJson, roadPointList=roadPointList)
                # 当RoadLine的Id重复，则重复次数加一并更新Id
                while roadLine.id in self.roadLineHashMap:
                    # Step1：尝试拼接路段
                    oldRoadLine = self.roadLineHashMap[roadLine.id]
                    # 如果拼接成功
                    if self.mergeRoadLine(oldRoadLine, roadLine):
                        roadLine = oldRoadLine
                        break
                    # Step2：无法拼接，则重复次数加一并更新Id
                    roadLine.repetited()
                # 重新存入roadLine
                self.roadLineHashMap[roadLine.id] = roadLine

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
                self.roadPointIndexHashMap[roadPoint.stringId] = roadPoint.setRoadPointId()
            else:
                # 已存在，则读出原有的点
                roadPoint = self.roadPointHashMap[self.roadPointIndexHashMap[roadPoint.stringId]]
            # 添加roadLine的omsId信息到point中
            roadPoint.addOmsId(omsId)
            # 将roadPoint添加到HashMap
            self.roadPointHashMap[roadPoint.id] = roadPoint
            # 与上一个point重复，则不添加到roadPointList
            if len(roadPointList) == 0 or roadPointList[-1] != roadPoint.id:
                roadPointList.append(roadPoint.id)
        # roadLine中point的数目小于2时，则返回None
        if len(roadPointList) < 2:
            return None
        # roadLine中point的数目大于2时，将端点存入KeyPointIndex中，返回point的intId序列
        endPoint1 = self.roadPointHashMap[roadPointList[0]]
        endPoint2 = self.roadPointHashMap[roadPointList[-1]]
        self.keyPointIndexHashMap[endPoint1.stringId] = endPoint1.id
        self.keyPointIndexHashMap[endPoint2.stringId] = endPoint2.id
        return roadPointList

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
                omsIdList = [roadPointDic["properties"]["osm_id"], roadPointDic["properties"]["osm_id_2"]]
                # Step1:去重
                # 当相同坐标的点还未存储到roadPointIndexHashMap中
                if roadPoint.stringId not in self.roadPointIndexHashMap:
                    # 为roadPoint赋intId
                    roadPoint.setRoadPointId()
                    # 先将RoadPointId存入Id索引表
                    self.roadPointIndexHashMap[roadPoint.stringId] = roadPoint.id
                # 当相同坐标的点已经存储到roadPointIndexHashMap中
                else:
                    # 取出原有的点oldRoadPoint
                    oldRoadPoint = self.roadPointHashMap[self.roadPointIndexHashMap[roadPoint.stringId]]
                    # 合并相同stringId的Point并存入roadPointHashMap
                    roadPoint = oldRoadPoint.mergePoint(roadPoint)
                # Step2:与RoadLine交互
                # 用以存储RoadLineId
                for omsId in omsIdList:
                    isSaved = False
                    # 把omsId添加到roadPoint
                    if omsId not in roadPoint.omsIdList:
                        roadPoint.addOmsId(omsId)
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
                        if roadPoint.id in roadLine.roadPointList:
                            isSaved = True
                            continue
                        # 将point信息存入roadLine的roadPointList中
                        res = self.addPointToLine(roadLine, roadPoint)
                        if res:
                            isSaved = True
                    assert isSaved
                # Step3:存储Point
                # 将point添加到KeyPoint索引
                self.keyPointIndexHashMap[roadPoint.stringId] = roadPoint.id
                # 将Point放入roadPointHashMap
                self.roadPointHashMap[roadPoint.id] = roadPoint

    # 删除不连通的roadLine
    def deleteDisconnectedMap(self):
        for pointsId in self.res:
            for pointId in pointsId:
                point = self.roadPointHashMap[pointId]
                # 删除点相邻的roadLine
                for roadLineId in point.roadLineList:
                    if roadLineId in self.roadLineHashMap:
                        del self.roadLineHashMap[roadLineId]
                # 清空点的roadLineList
                point.isKeyPoint = False
                del self.keyPointIndexHashMap[point.stringId]
                self.roadPointHashMap[pointId] = point
