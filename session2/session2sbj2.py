from interface.Subject import *
import json
from geohash import encode, neighbors
from utils.MapsUtil import calculateDistance
from session2.path_planning.rescue_people import assign_task
from session1.KSPWLO import parse_adj, KSPWLO_Searcher
from session2.Algorithm2 import *


# 科目一情景一
class Session2Sbj2(Subject):
    def __init__(self, rootAddress, FileNumber, staticMap, BreakInfo):
        super().__init__(rootAddress=rootAddress, FileNumber=FileNumber, staticMap=staticMap, BreakInfo=BreakInfo)
        self.session = 2
        self.subject = 2
        # 科目与情景地址
        self.subjectAddress = rootAddress + 'session_' + str(self.session) + '\\subject_' + str(self.subject) + '\\'
        # 储存救援人员总数
        self.rescuePeopleTotal = None
        # 发车点id列表
        self.startPointList = []

        # 解析任务信息
        self.parseClientPathFile(self.subjectAddress + "client_path_" + str(self.fileNumber) + ".json")
        # self.dynamicMap.printRoadPointAll(True)

        # 生成segment
        self.generateSegments()

        # 调用算法寻路
        self.algorithmRes = self.algorithmRun()

        # # 生成文件
        # self.generateFiles()

    # 读取clientPathFile文件信息
    def parseClientPathFile(self, clientPathFile):
        print("\n========================== 开始解析任务信息 ==========================")
        # 读取Json文件
        with open(clientPathFile, "r", encoding="utf-8") as f:
            # 读入clientPath字典存储为 clientPath
            clientPath = json.load(f)
            # 从clientPath字典读取相关信息
            # 存储发送Id
            self.sendId = clientPath["send_id"]
            # 存储运行时长
            self.raceTime = clientPath["race_time"]
            # 储存救援人员总数
            self.rescuePeopleTotal = clientPath["rescue_people_total"]

            # 处理people
            print("-------------------------- 解析people --------------------------")
            peopleListJson = clientPath["rescue_people"]
            for peopleDir in peopleListJson:
                self.parsePeople(peopleDir)
            # 打印people解析结果
            self.dynamicMap.printPeopleIndexAll(False)
            self.dynamicMap.printPeopleAll(False)
        print("========================== 任务信息解析完成 ==========================")

    # 将数据结构传输给算法进行路径查找
    def algorithmRun(self):
        print("========================== 算法开始 ==========================")

        print(assign_task(self.dynamicMap))

        print("========================== 算法结束 ==========================")
        return None

    # 生成文件
    def generateFiles(self):
        print("========================== 处理结果并写出文件 ==========================")
        self.drawMapRes = []
        # 存储json文件的内容
        carPoints = dict()
        for i in range(0, len(self.algorithmRes)):
            # 存入car_id
            carPoints["car_id"] = i
            # 存入startPoint
            startPointJson = dict()
            startPoint = self.dynamicMap.getPoint(self.startPointList[i])
            startPointJson['longitude'] = startPoint.getLongitude()
            startPointJson['latitude'] = startPoint.getLatitude()
            carPoints["start_point"] = startPointJson
            # 存入pass_points
            passPoints = []
            carPointsClass = self.algorithmRes[i]
            # for routineTup in carPointsClass:

        #     path = []
        #     pathTup = pathClass.edges
        #     # 存储json文件的一条路
        #     pathJson = []
        #     lastCoordinate = self.dynamicMap.roadPointHashMap[self.startPointId].coordinate
        #     pointJson = dict()
        #     pointJson["longitude"] = lastCoordinate[1]
        #     pointJson["latitude"] = lastCoordinate[0]
        #     for tup in pathTup:
        #         segment = self.dynamicMap.getSegment(list(tup))
        #         path.append(segment)
        #         # 处理输出的json文件
        #         # 获取segment的所有point坐标
        #         pointsCor = self.dynamicMap.getPointsOfRoadLineOrSegment(roadLineOrSegment=segment,
        #                                                                  onlyCoordinates=True)
        #         # 顺序相反
        #         if pointsCor[-1] == lastCoordinate:
        #             pointsCor.reverse()
        #
        #         for i in range(1, len(pointsCor)):
        #             pointCor = pointsCor[i]
        #             pointJson = dict()
        #             pointJson["longitude"] = pointCor[1]
        #             pointJson["latitude"] = pointCor[0]
        #             pathJson.append(pointJson)
        #         lastCoordinate = pointsCor[-1]
        #     # 添加到json中的paths
        #     pathsJson.append(pathJson)
        #     self.drawMapRes.append(path)

        self.fileRes = dict()
        self.fileRes['operate_id'] = self.sendId
        self.fileRes['car_point_total'] = 3
        self.fileRes['car_points'] = carPoints
        # 写出json
        with open(self.subjectAddress + 'team_path_' + str(self.sendId) + '.json', 'w')as f:
            json.dump(obj=self.fileRes, fp=f)
        print("========================== 结果已处理完成且文件已写出 ==========================")

    # 获取分区方法
    def mapPersonToSegment(self, person, staticMap, precision):
        code = encode(person["people_point"]["latitude"], person["people_point"]["longitude"], precision)
        print(code)
        segmentSet = self.getDistrict(code, staticMap)
        neighborList = neighbors(code)
        # 将每个相邻区域的seg加入集合
        for neighbor in neighborList:
            neighborSegmentSet = self.getDistrict(neighbor, staticMap)
            if neighborSegmentSet is not None:
                segmentSet = segmentSet | neighborSegmentSet
            else:
                continue
        if len(segmentSet) == 0:
            print("人所在区域内无segment")
            return
            # 精度缩小
            # return self.mapPersonToSegment(person, staticMap, precision - 1)
        else:
            segmentId = self.searchInDistrict(segmentSet, person["people_point"]["latitude"],
                                              person["people_point"]["longitude"])
        return segmentId

    # 从集合中选择与给定点最近的segId
    def searchInDistrict(self, segSet, latitude, longtitude):
        minDistance = 1000
        nearestSegmentId = None
        for segmentId in segSet:
            # 计算点到segment距离
            distance = calculateDistance(segmentId, latitude, longtitude)
            if distance < minDistance:
                minDistance = distance
                nearestSegmentId = segmentId
        return nearestSegmentId

    # 根据编码返回区域
    def getDistrict(self, code, staticMap):
        if code in staticMap.districtHashMap:
            return staticMap.districtHashMap[code]
        else:
            return None
