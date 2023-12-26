from interface.Subject import *
import json
from session1.KSPWLO import parse_adj, KSPWLO_Searcher


# 科目一情景一
class Session1Sbj1(Subject):
    def __init__(self, rootAddress, FileNumber, staticMap, BreakInfo):
        super().__init__(rootAddress=rootAddress, FileNumber=FileNumber, staticMap=staticMap, BreakInfo=BreakInfo)
        self.session = 1
        self.subject = 1
        # 科目与情景地址
        self.subjectAddress = rootAddress + 'session_' + str(self.session) + '\\subject_' + str(self.subject) + '\\'

        # 存储起始点Id
        self.startPointId = None
        # 存储终止点Id
        self.endPointId = None

        # 解析任务信息
        self.parseClientPathFile(self.subjectAddress + "client_path_" + str(self.fileNumber) + ".json")

        # 生成segment
        self.generateSegments()

        # 调用算法寻路
        self.algorithmRes = self.algorithmRun()

        # 生成文件
        self.generateFiles()

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
            # 读取clientPathFile文件break信息
            breakList = clientPath["breaks"]
            # 遍历break事件
            for breakEventDir in breakList:
                # 解析break事件
                self.parseBreakEven(breakEventDir)
            # breakEvent解析结果
            self.dynamicMap.printBreakEventIndexAll(True)
            self.dynamicMap.printBreakEventAll(True)
        print("========================== 任务信息解析完成 ==========================")

    # 将数据结构传输给算法进行路径查找
    def algorithmRun(self):
        print("========================== 算法开始寻路 ==========================")
        startPointId = self.startPointId
        endPointId = self.endPointId
        K = 10
        overlap_theta = 0.1
        parsedGraph = {"parsed_adj": parse_adj(self.dynamicMap)}
        kspf = KSPWLO_Searcher(parsedGraph)
        pathClass = kspf.search(startPointId, endPointId, K, overlap_theta)
        print("========================== 算法寻路结束 ==========================")
        return pathClass

    # 生成文件
    def generateFiles(self):
        print("========================== 处理结果并写出文件 ==========================")
        self.drawMapRes = []
        # 存储json文件的十条路
        pathsJson = []
        for pathClass in self.algorithmRes:
            path = []
            pathTup = pathClass.edges
            # 存储json文件的一条路
            pathJson = []
            lastCoordinate = self.dynamicMap.roadPointHashMap[self.startPointId].coordinate
            pointJson = dict()
            pointJson["longitude"] = lastCoordinate[1]
            pointJson["latitude"] = lastCoordinate[0]
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

                for i in range(1, len(pointsCor)):
                    pointCor = pointsCor[i]
                    pointJson = dict()
                    pointJson["longitude"] = pointCor[1]
                    pointJson["latitude"] = pointCor[0]
                    pathJson.append(pointJson)
                lastCoordinate = pointsCor[-1]
            # 添加到json中的paths
            pathsJson.append(pathJson)
            self.drawMapRes.append(path)
        self.fileRes= dict()
        self.fileRes['operate_id'] = self.sendId
        self.fileRes['paths'] = pathsJson
        # 写出json
        with open(self.subjectAddress + 'team_path_' + str(self.sendId) + '.json', 'w')as f:
            json.dump(obj=self.fileRes, fp=f)
        print("========================== 结果已处理完成且文件已写出 ==========================")
