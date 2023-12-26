class BreakInfo:
    def __init__(self):
        # 断路信息
        self.breakEventType = dict()
        # 道路状况等级表
        self.roadLevelHashMap = dict()
        # 桥梁、涵洞、建筑物状况等级表
        self.notRoadLevelHashMap = dict()


        self.initializationOfDic()

    # 初始化表格内容
    def initializationOfDic(self):
        # 断路信息表
        self.breakEventType[1] = "rod"  # 道路
        self.breakEventType[2] = "brg"  # 桥梁
        self.breakEventType[3] = "cul"  # 涵洞
        self.breakEventType[4] = "bud"  # 建筑物
        # 道路状况等级表
        self.roadLevelHashMap[1] = 10
        self.roadLevelHashMap[2] = 9.5
        self.roadLevelHashMap[3] = 9
        self.roadLevelHashMap[4] = 8.5
        self.roadLevelHashMap[5] = 8
        self.roadLevelHashMap[6] = 7.5
        self.roadLevelHashMap[7] = 7
        self.roadLevelHashMap[8] = 5
        self.roadLevelHashMap[9] = 2
        self.roadLevelHashMap[10] = 0
        # 桥梁、涵洞、建筑物状况等级表
        self.notRoadLevelHashMap[1] = 10
        self.notRoadLevelHashMap[2] = 8
        self.notRoadLevelHashMap[3] = 5
        self.notRoadLevelHashMap[4] = 2
        self.notRoadLevelHashMap[5] = 0
    # 查找速度
    def getSpeed(self, typeOfBreakEvent, level):
        breakEventType = self.breakEventType[typeOfBreakEvent]
        speed = -1
        if breakEventType == "rod":  # 道路
            speed = self.roadLevelHashMap[level]
        elif breakEventType == "brg" or breakEventType == "cul" or breakEventType == "bud":  # 桥梁
            if level in self.notRoadLevelHashMap:
                speed = self.notRoadLevelHashMap[level]
            else:
                speed = self.roadLevelHashMap[level]
                print("非道路信息中没有此level的breakEvent，已转从道路信息中查询")
        print("查询到break信息，类型为：" + breakEventType + ",等级为：" + str(level) + ",速度为：" + str(speed))
        return speed