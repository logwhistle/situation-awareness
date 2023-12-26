import json

from geohash import encode, neighbors
from session2.SegementWithPeople import SegmentWithPeople
from utils.MapsUtil import calculateDistance


class Session2Sbj2:
    def __init__(self, clientPathFile, staticMap):
        # 储存救援人员总数
        self.peopleNum = None
        # 存储发送Id
        self.sendId = None
        # 存储运行时长
        self.raceTime = None
        # 存储带people信息的segment
        self.segmentWithPeopleHashMap = {}

        # 构造segmentWithPeopleHashMap
        self.generateSegmentWithPeople(staticMap)

        # 读json文件，遍历并更新segmentWithPeopleHashMap
        self.loadClientPathFile(clientPathFile, staticMap)

        #算法入口
        print("请开始你的表演")

    def generateSegmentWithPeople(self, staticMap):
        if staticMap.segmentHashMap is None:
            raise RuntimeError("静态图中无segment，无法生成segmentWithBreakHashMap")
        for _, v in staticMap.segmentHashMap.items():
            segmentWithPeople = SegmentWithPeople(v)
            self.segmentWithPeopleHashMap[v.segmentId] = segmentWithPeople

    def loadClientPathFile(self, clientPathFile, staticMap):

        with open(clientPathFile, "r", encoding="utf-8") as f:
            # 读入clientPath字典存储为 clientPath
            clientPath = json.load(f)
            # 从clientPath字典读取相关信息
            # 储存救援人员总数
            self.peopleNum = clientPath["rescue_people_total"]
            # 存储发送Id
            self.sendId = clientPath["send_id"]
            # 存储运行时长
            self.raceTime = clientPath["race_time"]

            peopleList = clientPath["rescue_people"]
            for person in peopleList:
                # 把person映射到segment上
                segmentId = self.mapPersonToSegment(person, staticMap, 7)
                self.segmentWithPeopleHashMap[segmentId].peopleList.append(person["people_id"])

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
            #return self.mapPersonToSegment(person, staticMap, precision - 1)
        else:
            segmentId = self.searchInDistrict(segmentSet, person["people_point"]["latitude"],
                                              person["people_point"]["longitude"])
        return segmentId

    # 从集合中选择与给定点最近的segId
    def searchInDistrict(self, segSet, latitude, longtitude):
        minDistance = 1000
        nearestSegmentId = None
        for segmentId in segSet:
            #计算点到segment距离
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
