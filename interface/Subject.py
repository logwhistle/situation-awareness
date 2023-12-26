from maps.DynamicMap import *
import json
from maps.BreakEvent import *
from session3.PlacePoint import *
from maps.People import *
from utils.MapsUtil import getDistanceMeter


# 情景
class Subject:
    def __init__(self, rootAddress, FileNumber, staticMap, BreakInfo):
        self.session = None
        self.subject = None
        self.fileNumber = FileNumber
        # 科目与情景地址
        self.subjectAddress = None

        # 存储发送Id
        self.sendId = None
        # 存储运行时长
        self.raceTime = None

        # 初步算法结果
        self.tempRes = None
        # 最终算法结果
        self.algorithmRes = None
        # 绘图用的结果
        self.drawMapRes = None
        # 文件结果
        self.fileRes = None

        # 创建动态地图
        self.dynamicMap = self.generationDynamicMap(staticMap, BreakInfo)

    # 生成动态地图
    def generationDynamicMap(self, staticMap, BreakInfo):
        if staticMap is None:
            return None
        return DynamicMap(staticMap, BreakInfo)

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
            print('·············· sendId = ' + str(self.sendId) + ' ··············')
            # 存储运行时长
            self.raceTime = clientPath["race_time"]
            print('·············· raceTime = ' + str(self.raceTime) + 's ··············')
        print("========================== 任务信息解析完成 ==========================")

    # 将数据结构传输给算法进行路径查找
    def algorithmRun(self):
        pass

    # 生成文件
    def generateFiles(self):
        res = dict()
        res['operate_id'] = self.sendId
        # 写出json
        with open(self.subjectAddress + 'team_path_' + str(self.sendId) + '.json', 'w')as f:
            json.dump(obj=res, fp=f)

    # 寻找点在Map中的点坐标在什么位置
    def searchForPointId(self, coordinate):
        pointId = self.dynamicMap.searchForPointId(coordinate)
        # 如果在静态图中无法找到点
        if pointId == -1:
            raise RuntimeError("client_path" + str(self.sendId) + "找不到点：" + str(coordinate))
        # 打印找到的Point与给定的coordinate和其之间的误差
        print(str(self.dynamicMap.roadPointHashMap[pointId].coordinate) + "\tPoint的id:" + str(pointId) + "\t")
        print(str(coordinate) + "：给定点点坐标\n两点距离误差为：" + str(
            getDistanceMeter(self.dynamicMap.roadPointHashMap[pointId].coordinate, coordinate)) + ', 是否为相近点：' + str(
            isClosePoint(coordinate, self.dynamicMap.roadPointHashMap[pointId].coordinate)))
        print("--------------------------")
        # 返回Point坐标
        return pointId

    # 解析break事件
    def parseBreakEven(self, breakEventDir, new=False):
        print("-------------------------- breakEvent --------------------------")
        omsId = breakEventDir["osm_id"]
        breakType = breakEventDir["break_type"]
        breakLevel = breakEventDir["break_level"]
        happendTime = breakEventDir["happend_time"]
        continueTime = breakEventDir["continue_time"]
        # 录入startPoint
        startPointId = self.searchForPointId(
            [breakEventDir["break_start_point"]["latitude"], breakEventDir["break_start_point"]["longitude"]])
        startPoint = self.dynamicMap.getPoint(startPointId)
        startPoint.isKeyPoint = True
        self.dynamicMap.savePoint(startPoint)
        # 录入endPoint
        endPointId = self.searchForPointId(
            [breakEventDir["break_end_point"]["latitude"], breakEventDir["break_end_point"]["longitude"]])
        endPoint = self.dynamicMap.getPoint(endPointId)
        endPoint.isKeyPoint = True
        self.dynamicMap.savePoint(endPoint)
        roadPointList = [startPointId, endPointId]
        # 生成breakEvent并存储到dynamicMap
        breakEvent = BreakEvent(omsId=omsId, isNew=new, breakType=breakType, breakLevel=breakLevel,
                                happendTime=happendTime, continueTime=continueTime, roadPointList=roadPointList)
        # 正常存储break，不存入newBreakIdList
        self.dynamicMap.saveBreakEvent(breakEvent, new=new)

    # 解析people
    def parsePeople(self, peopleDir):
        id = peopleDir['people_id']
        type = peopleDir["people_type"]
        coordinate = [peopleDir["people_point"]["latitude"], peopleDir["people_point"]["longitude"]]
        idOfPoint = self.searchForPointId(coordinate)
        people = People(idOfPeople=id, typeOfPeople=type, coordinate=coordinate, pointId=idOfPoint, initPointId=idOfPoint)
        point = self.dynamicMap.getPoint(idOfPoint)
        point.addPeople(people.id)
        point.isKeyPoint = True
        self.dynamicMap.savePoint(point)
        if point.id in self.dynamicMap.peopleIndexHashMap:
            self.dynamicMap.peopleIndexHashMap[point.id].append(people.id)
        else:
            self.dynamicMap.peopleIndexHashMap[point.id] = [people.id]
        self.dynamicMap.peopleHashMap[people.id] = people



    # 生成segment
    def generateSegments(self, isNew=False):
        print("========================== 生成segments ==========================")
        self.dynamicMap.generateSegment(isNew=isNew)
        print("========================== segments已生成 ==========================")
