from interface.Subject import *


class Session3Sbj2(Subject):
    def __init__(self, rootAddress, FileNumber, staticMap, BreakInfo):
        # 科目与情景地址
        super().__init__(rootAddress=rootAddress, FileNumber=FileNumber, staticMap=staticMap, BreakInfo=BreakInfo)
        self.session = 3
        self.subject = 2
        # 科目与情景地址
        self.subjectAddress = rootAddress + 'session_' + str(self.session) + '\\subject_' + str(self.subject) + '\\'
        # 人员初始点
        self.initPointList = []
        # 人员避难所
        self.placePointList = []

        # 第一次运行
        self.firstRun()

        # 第二次运行
        self.secondRun()

    # 第一次运行
    def firstRun(self):
        # 解析任务信息
        self.parseClientPathFile(self.subjectAddress + "client_path_" + str(self.fileNumber) + ".json", )

        # 生成segment
        self.generateSegments()
        self.dynamicMap.printRoadLineAll(False)
        self.dynamicMap.printKeyPointAll(False)
        self.dynamicMap.printRoadPointAll(False)
        self.dynamicMap.printSegmentAll(False)

        # 调用算法寻路
        self.tempRes = self.algorithmRun()

        # 生成文件
        self.generateFiles()

    # 第二次运行
    def secondRun(self):
        # 解析newBreak信息
        self.parseClientPathFile(self.subjectAddress + "client_path_" + str(self.fileNumber) + ".json",
                                 parseNewBreakEvent=True)

        # 生成segment
        self.generateSegments(isNew=True)
        self.dynamicMap.printRoadLineAll(False)
        self.dynamicMap.printKeyPointAll(False)
        self.dynamicMap.printRoadPointAll(False)
        self.dynamicMap.printSegmentAll(False)

        # 调用算法寻路
        self.algorithmRes = self.algorithmRun(secondTime=True)

        # 生成文件
        self.generateFiles(secondTime=True)

    # 读取clientPathFile文件信息
    def parseClientPathFile(self, clientPathFile, parseNewBreakEvent=False):
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

            # 处理initPoint
            print("-------------------------- 解析initPoint --------------------------")
            initPointList = clientPath["init_points"]
            for initPointDir in initPointList:
                self.parseInitPoint(initPointDir)
            # 打印initPoint解析结果
            self.printInitPointAll(True)

            # 处理避难所
            print("-------------------------- 解析placePoint --------------------------")
            placePointList = clientPath["place_points"]
            for placePointJson in placePointList:
                self.parsePlacePoint(placePointJson)
                # 打印placePoint解析结果
                self.dynamicMap.printPlacePointAll(True)

            # 处理break事件
            print("-------------------------- 解析break --------------------------")
            # 读取clientPathFile文件break事件
            breakListJson = clientPath["breaks"]
            # 遍历break事件
            for breakEventDir in breakListJson:
                # 解析break事件
                self.parseBreakEven(breakEventDir)
            # 打印breakEvent解析结果
            self.dynamicMap.printBreakEventIndexAll(True)
            self.dynamicMap.printBreakEventAll(True)

            # 处理people
            print("-------------------------- 解析people --------------------------")
            peopleListJson = clientPath["people"]
            for peopleDir in peopleListJson:
                self.parsePeople(peopleDir)
            # 打印people解析结果
            self.dynamicMap.printPeopleIndexAll(False)
            self.dynamicMap.printPeopleAll(True)

        print("========================== 任务信息解析完成 ==========================")

    # 解析initPoint
    def parseInitPoint(self, initPointDir):
        coordinate = [initPointDir["latitude"], initPointDir["longitude"]]
        idOfPoint = self.searchForPointId(coordinate)
        self.initPointList.append(idOfPoint)
        point = self.dynamicMap.getPoint(idOfPoint)
        point.isKeyPoint = True
        self.dynamicMap.savePoint(point)

    # 解析placePoint
    def parsePlacePoint(self, placePointJson):
        # 读取信息
        idOfPlacePoint = placePointJson["place_id"]
        typeOfPlacePoint = placePointJson["place_type"]
        coordinate = [placePointJson["place_point"]["latitude"], placePointJson["place_point"]["longitude"]]
        radius = placePointJson["place_radius"]
        idOfPoint = self.searchForPointId(coordinate)
        # 生成placePoint
        placePoint = PlacePoint(idOfPlacePoint=idOfPlacePoint, typeOfPlacePoint=typeOfPlacePoint, coordinate=coordinate,
                                radius=radius, idOfPoint=idOfPoint)
        point = self.dynamicMap.getPoint(idOfPoint)
        point.addPlacePoint(placePoint.id)
        point.isKeyPoint = True
        self.dynamicMap.savePoint(point)
        self.dynamicMap.placePointHashMap[idOfPlacePoint] = placePoint
        self.placePointList.append(idOfPoint)

    # 打印所有存储在Map中的peopleIndex
    def printInitPointAll(self, detail):
        if len(self.initPointList) == 0:
            print("··············没有的initPoint··············")
        else:
            print("··············map的initPointIndex列表··············")
            for pointId in self.initPointList:
                print(pointId, end='\t')
                print(self.dynamicMap.getPoint(pointId))
            print('··············map中initPoint总数为：' + str(len(self.initPointList)) + '··············')

    # 解析people
    def parsePeople(self, peopleDir):
        id = peopleDir['people_id']
        type = peopleDir["people_type"]
        coordinate = [peopleDir["people_point"]["latitude"], peopleDir["people_point"]["longitude"]]
        idOfPoint = self.searchForPointId(coordinate)
        initPId = 0
        initPDist = float('inf')

        # 重写部分，初始点确定
        for initPointId in self.initPointList:
            initPointCor = self.dynamicMap.getPoint(initPointId).coordinate
            dist = getDistanceMeter(initPointCor, coordinate)
            if dist < initPDist:
                initPDist = dist
                initPId = initPointId
        people = People(idOfPeople=id, typeOfPeople=type, coordinate=coordinate, pointId=idOfPoint, initPointId=initPId)
        # 重写部分，计算人口密度
        densityOfPeople = []
        for otherPeople in self.dynamicMap.peopleHashMap.values():
            dis = getDistanceMeter(otherPeople.coordinate, people.coordinate)
            if dis < 150:
                densityOfPeople.append(otherPeople.id)
                otherPeople.densityOfPeople.append(people.id)
                self.dynamicMap.peopleHashMap[otherPeople.id] = otherPeople
        people.densityOfPeople = densityOfPeople

        point = self.dynamicMap.getPoint(idOfPoint)
        point.addPeople(people.id)
        point.isKeyPoint = True
        self.dynamicMap.savePoint(point)
        if point.id in self.dynamicMap.peopleIndexHashMap:
            self.dynamicMap.peopleIndexHashMap[point.id].append(people.id)
        else:
            self.dynamicMap.peopleIndexHashMap[point.id] = [people.id]
        self.dynamicMap.peopleHashMap[people.id] = people

    def algorithmRun(self, secondTime=True):
        pass

    def generateFiles(self, secondTime=True):
        pass