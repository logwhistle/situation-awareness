from interface.Subject import *
import json
from session1.KSPWLO import parse_adj, KSPWLO_Searcher, KSPWLO_reSearcher


# 科目一情景二
class Session1Sbj2(Subject):
    def __init__(self, rootAddress, FileNumber, staticMap, BreakInfo):
        super().__init__(rootAddress=rootAddress, FileNumber=FileNumber, staticMap=staticMap, BreakInfo=BreakInfo)
        self.session = 1
        self.subject = 2
        # 科目与情景地址
        self.subjectAddress = rootAddress + 'session_' + str(self.session) + '\\subject_' + str(self.subject) + '\\'

        # 存储起始点Id
        self.startPointId = None
        # 存储终止点Id
        self.endPointId = None
        # 存储第二次的起点组
        self.startPointIds = None

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
        self.parseClientPathFile(self.subjectAddress + "client_path_" + str(self.fileNumber) + ".json", parseNewBreakEvent=True)

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
            if not parseNewBreakEvent:
                # 从clientPath字典读取相关信息
                # 存储发送Id
                self.sendId = clientPath["send_id"]
                # 存储运行时长
                self.raceTime = clientPath["race_time"]
                # 存储起始点坐标
                print("-------------------------- 解析起点 --------------------------")
                self.startPointId = self.searchForPointId(
                    [clientPath["start_point"]["latitude"], clientPath["start_point"]["longitude"]])
                startPoint = self.dynamicMap.getPoint(self.startPointId)
                startPoint.isKeyPoint = True
                self.dynamicMap.savePoint(startPoint)
                # 存储终止点坐标
                print("-------------------------- 解析终点 --------------------------")
                self.endPointId = self.searchForPointId(
                    [clientPath["end_point"]["latitude"], clientPath["end_point"]["longitude"]])
                endPoint = self.dynamicMap.getPoint(self.endPointId)
                endPoint.isKeyPoint = True
                self.dynamicMap.savePoint(endPoint)
                print("-------------------------- 解析breakEvent --------------------------")
                # 读取clientPathFile文件break信息
                breakList = clientPath["breaks"]
                # 遍历break事件
                for breakEventDir in breakList:
                    # 解析break事件
                    self.parseBreakEven(breakEventDir)
                # breakEvent解析结果
                self.dynamicMap.printBreakEventIndexAll(True)
                self.dynamicMap.printBreakEventAll(True)
            else:
                print("-------------------------- 解析newBreakEvent --------------------------")
                # 读取newBreakStartTime
                self.dynamicMap.newBreakStartTime = clientPath["new_break_start_time"]
                # 读取clientPathFile文件break信息
                newBreakList = clientPath["newBreaks"]
                # 遍历newBreak事件
                for newBreakEventDir in newBreakList:
                    # 解析break事件
                    self.parseBreakEven(newBreakEventDir, new=True)
                # breakEvent解析结果
                self.dynamicMap.printNewBreakEventIndexAll(True)
                self.dynamicMap.printBreakEventAll(True)
                print("-------------------------- 计算第二次寻路起点 --------------------------")
                # 记录第二次寻路的起点
                self.startPointIds = []
                # 循环遍历第一次寻路的结果
                for pathClass in self.tempRes:
                    # 标记是否已找到新起点
                    findedStartPoint = False
                    # 记录当前时间
                    currentTime = 0
                    # 遍历路线的每个segment的的端点表示
                    for tup in pathClass.edges:
                        # 获取对应的segment、id以及同行时间
                        segment = self.dynamicMap.getSegment(list(tup))
                        transTimeOfSegment = self.dynamicMap.transTimeOfSegment(segment=segment,
                                                                                currentTime=currentTime)
                        # 新起点不在此路段上
                        if currentTime + transTimeOfSegment < self.dynamicMap.newBreakStartTime:
                            currentTime += transTimeOfSegment
                            continue
                        # 新起点在此路段上
                        else:
                            # 获取segment的所有point坐标
                            pointsCor = self.dynamicMap.getPointsOfRoadLineOrSegment(roadLineOrSegment=segment, onlyCoordinates=True)
                            # 顺序相反,正在遍历的segment头点与坐标末端点相同
                            lastPointCor = self.dynamicMap.getPoint(list(tup)[-1]).coordinate
                            if lastPointCor == pointsCor[0]:
                                pointsCor.reverse()
                            # 遍历坐标点寻找新起点
                            for i in range(1, len(pointsCor)):
                                # 计算当前点与前一点的距离
                                distance = getDistanceMeter(pointsCor[i - 1], pointsCor[i])
                                # 计算此时间segment的速度
                                speed = self.dynamicMap.speedOfSegment(segment=segment, currentTime=currentTime)
                                # 计算通行时间
                                transTime = distance / speed
                                # 新起点还未到达
                                if currentTime + transTime < self.dynamicMap.newBreakStartTime:
                                    currentTime += transTime
                                    continue
                                # 到达新起点
                                else:
                                    newStartPointId = self.dynamicMap.searchForPointId(pointsCor[i - 1])
                                    newStartPoint = self.dynamicMap.roadPointHashMap[newStartPointId]
                                    newStartPoint.isKeyPoint = True
                                    self.dynamicMap.savePoint(newStartPoint)
                                    self.startPointIds.append(newStartPointId)
                                    findedStartPoint = True
                                    print('·············· 找到新起点' + str(newStartPoint) + ' ··············')
                                    break
                            break
                    if not findedStartPoint:
                        # 此条路没找到新起点，说明newBreak发生时已经跑到终点
                        print('未找到起点')
                        self.startPointIds.append(self.endPointId)
                print(self.startPointIds)
                print(self.endPointId)
        print("========================== 任务信息解析完成 ==========================")

    # 将数据结构传输给算法进行路径查找
    def algorithmRun(self, secondTime=False):
        overlap_theta = 0.2
        parsedGraph = {"parsed_adj": parse_adj(self.dynamicMap)}
        pathClasses = None
        if not secondTime:
            print("========================== 算法开始第一次寻路 ==========================")
            kspf = KSPWLO_Searcher(parsedGraph)
            pathClasses = kspf.search(start=self.startPointId, target=self.endPointId, K=5, overlap_theta=overlap_theta)
            print("========================== 算法第一次寻路结束 ==========================")
        else:
            print("========================== 算法开始第二次寻路 ==========================")
            kspf_re = KSPWLO_reSearcher(parsedGraph)
            for startPointId in self.startPointIds:
                if pathClasses is None:
                    K = 1
                else:
                    K = len(pathClasses) + 1
                pathClasses = kspf_re.search(start=startPointId, target=self.endPointId, K=K,
                                             overlap_theta=overlap_theta, init_state=pathClasses)
            print("========================== 算法第二次寻路结束 ==========================")
        return pathClasses

    # 生成文件
    def generateFiles(self, secondTime=False):
        if not secondTime:
            print("========================== 处理第一次寻路结果 ==========================")
            self.drawMapRes = [[], []]
            # 存储json文件五条路
            firstPoints = []
            for pathClass in self.tempRes:
                path = []
                pathTup = pathClass.edges
                # 存储json文件的一条路
                pathJson = []
                # 存入起点
                lastCoordinate = self.dynamicMap.roadPointHashMap[self.startPointId].coordinate
                pointJson = dict()
                pointJson["longitude"] = lastCoordinate[1]
                pointJson["latitude"] = lastCoordinate[0]
                pathJson.append(pointJson)
                # 循环遍历路线的segment
                for tup in pathTup:
                    segment = self.dynamicMap.getSegment(list(tup))
                    path.append(segment)
                    # 处理输出的json文件
                    # 获取segment的所有point坐标
                    pointsCor = self.dynamicMap.getPointsOfRoadLineOrSegment(roadLineOrSegment=segment,
                                                                             onlyCoordinates=True)
                    # 顺序相反
                    if pointsCor[-1] == lastCoordinate:
                        pointsCor.reverse()
                    # 记录坐标点
                    for j in range(1, len(pointsCor)):
                        pointCor = pointsCor[j]
                        pointJson = dict()
                        pointJson["longitude"] = pointCor[1]
                        pointJson["latitude"] = pointCor[0]
                        pathJson.append(pointJson)
                    lastCoordinate = pointsCor[-1]
                # 添加到json中的paths
                firstPoints.append(pathJson)
                self.drawMapRes[0].append(path)
            self.fileRes = dict()
            self.fileRes['firstPoints'] = firstPoints
            print("========================== 第一次寻路结果已处理完成 ==========================")
        else:
            print("========================== 处理第二次寻路结果并写出文件 ==========================")
            # 存储第二次寻路的五条路
            secondPathInfos = []
            for i in range(0, len(self.algorithmRes)):
                pathClass = self.algorithmRes[i]
                path = []
                routineTup = pathClass.edges
                # 存储json文件的一条路
                pathJson = []
                # 存入起点
                lastCoordinate = self.dynamicMap.roadPointHashMap[self.startPointIds[i]].coordinate
                pointJson = dict()
                pointJson["longitude"] = lastCoordinate[1]
                pointJson["latitude"] = lastCoordinate[0]
                pathJson.append(pointJson)
                # 循环遍历路线的segment
                for tup in routineTup:
                    segment = self.dynamicMap.getSegment(list(tup))
                    path.append(segment)
                    # 处理输出的json文件
                    # 获取segment的所有point坐标
                    pointsCor = self.dynamicMap.getPointsOfRoadLineOrSegment(roadLineOrSegment=segment,
                                                                             onlyCoordinates=True)
                    # 顺序相反
                    if pointsCor[-1] == lastCoordinate:
                        pointsCor.reverse()
                    # 记录坐标点
                    for j in range(1, len(pointsCor)):
                        pointCor = pointsCor[j]
                        pointJson = dict()
                        pointJson["longitude"] = pointCor[1]
                        pointJson["latitude"] = pointCor[0]
                        pathJson.append(pointJson)
                    lastCoordinate = pointsCor[-1]
                # 添加到json中的secondPathInfos
                pathInfo = dict()
                pathInfo['road_id'] = i + 1
                pathInfo['paths'] = pathJson
                secondPathInfos.append(pathInfo)
                self.drawMapRes[1].append(path)
            self.fileRes['secondPathInfos'] = secondPathInfos
            self.fileRes['operate_id'] = self.sendId
            # 写出json
            with open(self.subjectAddress + 'team_path_' + str(self.sendId) + '.json', 'w')as f:
                json.dump(obj=self.fileRes, fp=f)
            print("========================== 第二次寻路结果已处理完成且文件已写出 ==========================")

