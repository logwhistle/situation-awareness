from utils.MapsUtil import *


class RoadLine:
    # 初始化RoadLine类
    def __init__(self, roadLineJson, roadPointList) -> None:
        # RoadLine的原始Id
        self.osmId = -1
        # RoadLine原始Id重复次数
        self.repetition = 0
        # RoadLine唯一id
        self.id = ""
        # 对象类型
        self.type = 'RoadLine'
        # RoadLine通行速度
        self.speed = 0
        # RoadLine长度
        self.length = 0
        # RoadLine宽度
        self.wide = 0
        # RoadLine所有的Point
        self.roadPointList = []
        # RoadLine所包含的Segment的Id
        self.segmentList = []

        # RoadLine的属性赋值
        self.osmId = int(roadLineJson["properties"]["osm_id"])
        self.id = self.refreshId()
        self.speed = float(extractNum(roadLineJson["properties"]["SPIDE"])) * 10 / 36  # 速度单位换算，将km/h转化成m/s
        self.length = float(extractNum(roadLineJson["properties"]["LENGTH"]))
        self.wide = float(extractNum(roadLineJson["properties"]["WIDE"]))
        self.roadPointList = roadPointList

    # 刷新RoadLine的id（字符串类型）
    def refreshId(self):
        # 更新roadLineId
        id = str(self.osmId) + "/" + str(self.repetition)
        # 返回更新后的roadLineId
        return id

    # 处理RoadLine的Id重复的情况
    def repetited(self):
        # 重复次数加一
        self.repetition += 1
        # 更新roadLineId
        self.id = self.refreshId()
        # 更新道路Id
        return self.id

    # 对于重新划分segment进行roadLine中无关数据的清理
    def initRoadLineForResegment(self):
        self.segmentList = []

    # 记录roadLine所包含的point
    def addPoint(self, pointId, index=None):
        addRes = addToList(list=self.roadPointList, obj=pointId, index=index)
        self.roadPointList = addRes[1]
        return addRes[0]

    # 记录RoadLine所包含的Segment
    def addSegment(self, segmentId, index=None):
        addRes = addToList(list=self.segmentList, obj=segmentId, index=index)
        self.segmentList = addRes[1]
        return addRes[0]

    # 合并两个roadLine
    def mergeRoadLine(self, roadLine):
        self.roadPointList += roadLine.roadPointList
        self.segmentList += roadLine.segmentList

    # （测试用）打印RoadLine所包含的所有Point
    def printPointArray(self):
        if len(self.roadPointList) == 0:
            print("··············RoadLine" + self.id + "没有Point··············")
        else:
            print("··············RoadLine" + str(self.id) + "的Point列表··············")
            for pointId in self.roadPointList:
                print("PointId:" + str(pointId))
        print("此RoadLine所包含的Point数量为：" + str(len(self.roadPointList)) + "\n")

    # （测试用）打印RoadLine所包含的所有Segment
    def printSegmentArray(self):
        if len(self.segmentList) == 0:
            print("··············RoadLine" + self.id + "没有Point··············")
        else:
            print("··············RoadLine" + str(self.id) + "的Segment列表··············")
            for sid in self.segmentList:
                print("SegmentId:" + str(sid))
        print("此RoadLine所包含的Segment数量为：" + str(len(self.segmentList)) + "\n")

    # 转化成字符串
    def __str__(self) -> str:
        return "RoadLine{" + \
               "osmId=" + str(self.osmId) + \
               ", repetition=" + str(self.repetition) + \
               ", id='" + str(self.id) + \
               ", type='" + str(self.type) + \
               ", speed=" + str(self.speed) + \
               ", length=" + str(self.length) + \
               ", wide=" + str(self.wide) + \
               ", roadPointList=" + str(self.roadPointList) + \
               ", segmentList=" + str(self.segmentList) + \
               '}'
