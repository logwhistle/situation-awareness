from utils.MapsUtil import *


class Segment:
    idStart = 0

    def __init__(self,
                 roadLineId,
                 osmId,
                 length,
                 wide,
                 speed,
                 endPoint1Id,
                 endPoint2Id,
                 roadPointList):
        # 给Segment的Id赋值
        Segment.idStart += 1
        self.id = Segment.idStart
        # 对象类型
        self.type = 'Segment'
        # 记录所属的RoadLine的id
        self.roadLineId = roadLineId
        # 所属的RoadLine的osmid
        self.osmId = osmId
        # Segment长度
        self.length = length
        # Segment宽度
        self.wide = wide
        # Segment限速
        self.speed = speed
        # 端点1的Id
        self.endPoint1Id = endPoint1Id
        # 端点2的Id
        self.endPoint2Id = endPoint2Id
        # Segment的散点Id
        self.roadPointList = roadPointList
        # breakEventList
        self.breakEventList = []
        # newBreakEventList
        self.oldBreakEventList = []
        # peopleList
        self.peopleList = []

    # 记录segment所包含的point
    def addPoint(self, pointId, index=None):
        addRes = addToList(list=self.roadPointList, obj=pointId, index=index)
        self.roadPointList = addRes[1]
        return addRes[0]

    # 转化成字符串
    def __str__(self) -> str:
        return "Segment { " + \
               "id=" + str(self.id) + \
               ", type=" + str(self.type) + \
               ", roadLineId=" + str(self.roadLineId) + \
               ", osmId=" + str(self.osmId) + \
               ", length=" + str(self.length) + \
               ", speed=" + str(self.speed) + \
               ", endPoint1Id=" + str(self.endPoint1Id) + \
               ", endPoint2Id=" + str(self.endPoint2Id) + \
               ", roadPointList=" + str(self.roadPointList) + \
               ", breakEventList=" + str(self.breakEventList) + \
               ", oldBreakEventList=" + str(self.oldBreakEventList) + \
               ", peopleList=" + str(self.peopleList) + \
               ' }'
