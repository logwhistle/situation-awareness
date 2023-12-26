from utils.MapsUtil import *


class RoadPoint:
    # 数字id的起始编号，从1开始赋值
    intIdStart = 0

    # 构造器
    def __init__(self, json_file=None, coordinate=None):
        # Point的string类型Id
        self.stringId = ""
        # Point的int类型Id
        self.id = -1
        # Point的类型
        self.isKeyPoint = False
        self.isInitPoint = False
        self.type = None

        # Point的经纬度
        self.coordinate = []
        # 与Point相连的RoadLine的omsId列表
        self.omsIdList = []
        # 与Point相连的RoadLine列表
        self.roadLineList = []
        # 与Point相连的point列表
        self.pointList = []
        # 与Point相连的Segment列表
        self.segmentList = []
        # Point所在的点的people列表
        self.peopleList = []
        # 公共场所placePoint列表
        self.placePointList = []

        # 自己新建Point
        if json_file is None:
            # 存储点经纬度
            self.coordinate = coordinate
        # 从json文件读入Point
        else:
            # # 存储第一个相邻的RoadLine的Id
            # oms_id = json_file["properties"]["osm_id"]
            # self.addRoadLine(str(oms_id))
            # # 存储第二个相邻的RoadLine的Id
            # oms_id2 = json_file["properties"]["osm_id_2"]
            # self.addRoadLine(str(oms_id2))
            # 存储点的经纬度
            self.coordinate.append(json_file["geometry"]["coordinates"][1])
            self.coordinate.append(json_file["geometry"]["coordinates"][0])
        # 给string类型的Id赋值
        self.stringId = '[' + str(precision(self.coordinate[0])) + ',' + str(precision(self.coordinate[1])) + ']'

    # 对于重新划分segment进行point中无关数据的清理
    def initPointForResegment(self):
        self.isKeyPoint = False
        self.isInitPoint = False
        self.type = None
        # 与Point相连的roadLine集合
        self.roadLineList = []
        # 与point相连的point集合
        self.pointList = []
        # 与Point相连的segment集合
        self.segmentList = []
        # Point所在的点的people集合
        self.peopleList = []

    # 获取纬度
    def getLatitude(self):
        return self.coordinate[0]

    # 获取经度
    def getLongitude(self):
        return self.coordinate[1]

    # 生成并返回Point的intId
    def setRoadPointId(self):
        if self.id < 0:
            RoadPoint.intIdStart += 1
            self.id = RoadPoint.intIdStart
        return self.id

    # 判断是否为同一个点
    def isSamePoint(self, point):
        return isSamePoint(self.coordinate, point.coordinate)

    # 判断是否为相近的点
    def isClosePoint(self, point):
        return isClosePoint(self.coordinate, point.coordinate)

    # 合并另一个点，将点的roadLineSet和segmentSet合并
    def mergePoint(self, point):
        for roadLineId in point.roadLineList:
            self.addRoadLine(roadLineId)
        for segmentId in point.segmentList:
            self.addSegment(segmentId)
        return self

    # 添加point所连接的roadLine的omsId
    def addOmsId(self, omsId, index=None):
        addRes = addToList(list=self.omsIdList, obj=omsId, index=index)
        self.omsIdList = addRes[1]
        return addRes[0]

    # 添加point所连接的roadLine的id
    def addRoadLine(self, roadLineId, index=None):
        addRes = addToList(list=self.roadLineList, obj=roadLineId, index=index)
        self.roadLineList = addRes[1]
        return addRes[0]

    # 添加point相邻的point的id
    def addPoint(self, pointId, index=None):
        addRes = addToList(list=self.pointList, obj=pointId, index=index)
        self.pointList = addRes[1]
        return addRes[0]

    # 添加Point所连接的Segment的id
    def addSegment(self, segmentId, index=None):
        addRes = addToList(list=self.segmentList, obj=segmentId, index=index)
        self.segmentList = addRes[1]
        return addRes[0]

    # 添加在point的people的id
    def addPeople(self, peopleId, index=None):
        addRes = addToList(list=self.peopleList, obj=peopleId, index=index)
        self.peopleList = addRes[1]
        return addRes[0]

    # 添加在point的公共场所placePoint的id
    def addPlacePoint(self, placePointId, index=None):
        addRes = addToList(list=self.placePointList, obj=placePointId, index=index)
        self.placePointList = addRes[1]
        return addRes[0]

    # (测试用)打印Point所连接的RoadLine的id
    def printRoadLine(self):
        if len(self.roadLineList) == 0:
            print("··············点", self.stringId, "没有关联的RoadLine··············")
        else:
            print("··············点", self.stringId, "的关联RoadLine列表··············")
            for roadLineId in self.roadLineList:
                print("RoadLine：", roadLineId)
        print("此Point共连通RoadLine数量为：" + str(len(self.roadLineList)) + "\n")

    # (测试用)打印Point所连接的Segment的id
    def printSegment(self):
        if len(self.segmentList) == 0:
            print("··············点", self.stringId, "没有关联Segment··············")
        else:
            print("··············点", self.stringId, "的关联Segment列表··············")
            for segmentId in self.segmentList:
                print("Segment：", segmentId)
        print("此Point共连通Segment数量为：" + str(len(self.segmentList)) + "\n")

    # 转化成字符串
    def __str__(self) -> str:
        return "RoadPoint { " + \
               "stringId=" + str(self.stringId) + \
               ", id=" + str(self.id) + \
               ", isKeyPoint=" + str(self.isKeyPoint) + \
               ", isInitPoint=" + str(self.isInitPoint) + \
               ", type=" + str(self.type) + \
               ", coordinate=" + str(self.coordinate) + \
               ", omsIdList=" + str(self.omsIdList) + \
               ", roadLineList=" + str(self.roadLineList) + \
               ", pointList=" + str(self.pointList) + \
               ", segmentList=" + str(self.segmentList) + \
               ", peopleList=" + str(self.peopleList) + \
               ", placePointList=" + str(self.placePointList) + \
               ' }'

#
# if __name__ == "__main__":
#     print("\n****************************** RoadPoint 测 试 开 始 ******************************")
#
#     # 示例eg1的数据
#     eg1 = RoadPoint({"type": "Feature", "properties": {"osm_id": 0, "osm_id_2": 2},
#                      "geometry": {"type": "Point", "coordinates": [105.7201544, 38.838968]}})
#     print("\n--------------- eg1 ---------------")
#     print(str(eg1))
#
#     # 示例eg2的数据
#     eg2 = RoadPoint({"type": "Feature", "properties": {"osm_id": 1, "osm_id_2": 3},
#                      "geometry": {"type": "Point", "coordinates": [105.7201544, 38.838968]}})
#     print("\n--------------- eg2 ---------------")
#     print(str(eg2))
#
#     # 示例eg3的数据
#     eg3 = RoadPoint({"type": "Feature", "properties": {"osm_id": 0, "osm_id_2": 2},
#                      "geometry": {"type": "Point", "coordinates": [105.72015, 38.83897]}})
#     print("\n--------------- eg3 ---------------")
#     print(str(eg3))
#
#     # 示例eg4的数据
#     eg4 = RoadLine({"type": "Feature",
#                     "properties": {"osm_id": 818, "NAME": "无名路", "EC": "null", "TYPE": "0640", "WIDE": "6.2",
#                                    "SPIDE": "30km\/h", "LENGTH": "412.625833577711", "RTYPE": "乡村道路", "LANE": 1.0,
#                                    "Shape_Leng": 412.62583357800003, "IsBreak": "null", "IsThreaten": "null",
#                                    "IsBlocked": "null"}, "geometry": {"type": "LineString",
#                                                                       "coordinates": [[105.5521319, 38.7257021],
#                                                                                       [105.5521330, 38.7257035],
#                                                                                       [105.5521319, 38.7257022],
#                                                                                       [105.5521319, 38.7257022],
#                                                                                       [105.5521319, 38.7257022],
#                                                                                       [105.5521319, 38.7257022],
#                                                                                       [105.5521319, 38.7257022],
#                                                                                       [105.5521319, 38.7257022],
#                                                                                       [105.5521319, 38.7257022]]}})
#     print("\n--------------- eg4 ---------------")
#     print(str(eg4))
#
#     # 示例eg5的数据
#     eg5 = RoadPoint(None, eg4, [38.7257022, 105.5521319])
#     print("\n--------------- eg5 ---------------")
#     print(str(eg5))
#
#     print("\n*************** 测试getLongitude()与getLongitude()：获取经纬度 ***************")
#     print("eg1的经度为：" + str(eg1.getLongitude()))
#     print("eg1的纬度为：" + str(eg1.getLatitude()))
#
#     print("\n*************** 测试setRoadPointIntId()：生成并返回Point的Id ***************")
#     print("eg1的Id为：" + str(eg1.setRoadPointIntId()))
#     print("eg2的Id为：" + str(eg2.setRoadPointIntId()))
#
#     print("\n*************** 测试isSamePoint()：判断是否为相同点 ***************")
#     print("eg1与eg2是否相同：" + str(eg1.isSamePoint(eg2)))
#     print("eg1与eg3是否相同：" + str(eg1.isSamePoint(eg3)))
#
#     print("\n*************** 测试isClosePoint()：判断是否为相近点 ***************")
#     print("eg1与eg2是否相近：" + str(eg1.isClosePoint(eg2)))
#     print("eg1与eg3是否相近：" + str(eg1.isClosePoint(eg3)))
#
#     print("\n*************** 测试mergePoint()：合并点 ***************")
#     print(str(eg1))
#     print(str(eg2))
#     eg1.mergePoint(eg2)
#     print(str(eg1))
#     print(str(eg2))
#
#     print("\n*************** 测试addRoadLine()与printRoadLine()：添加并打印RoadLine ***************")
#     eg1.printRoadLine()
#     eg1.addRoadLine(506)
#     eg1.printRoadLine()
#
#     print("\n*************** 添加并打印Segment ***************")
#     eg1.printSegment()
#     eg1.addSegment(556)
#     eg1.printSegment()
#
#     print("\n****************************** RoadPoint 测 试 结 束 ******************************\n")
