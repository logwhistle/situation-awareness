import json
from PIL import Image
from utils.VisualUtils import *


class TestOfRes:
    def __init__(self, sbj=None, map=None, roadLineListList=None, segmentListList=None, pointIdListList=None):
        print("\n========================== 测试：开始运行 ==========================")
        # 存储任务
        self.sbj = sbj
        # 存储结果
        self.res = None
        if sbj is not None:
            self.res = sbj.drawMapRes
        # 存储地图
        self.map = map
        if map is None:
            self.map = sbj.dynamicMap
        # 存储需要专门绘制的对象
        self.roadLineListList = roadLineListList
        self.segmentListList = segmentListList
        self.pointIdListList = pointIdListList
        self.isolatedPoint = None
        if map is not None:
            self.isolatedPoint = self.map.res

        self.canvas = None

        # 打印信息
        self.printInfo(roadLineListList=self.roadLineListList, segmentListList=self.segmentListList,
                       pointIdListList=self.segmentListList)
        print("-------------------------- 测试：初始化完毕 --------------------------")

        # 绘制静态图
        if sbj is None:
            # 绘制静态图
            self.testOfStaticMap()
        else:
            print(
                '------------------------- Session' + str(self.sbj.session) + ' Subject' + str(
                    self.sbj.subject) + ' SendId' + str(self.sbj.sendId) + ' -------------------------')
            # 科目一情景一
            if sbj.session == 1 and sbj.subject == 1:
                self.testOfSession1Sbj1()
            # 科目一情景二
            elif sbj.session == 1 and sbj.subject == 2:
                self.testOfSession1Sbj2()
            # 科目二情景一
            elif sbj.session == 2 and sbj.subject == 1:
                self.testOfSession2Sbj1()
            # 科目二情景二
            elif sbj.session == 2 and sbj.subject == 2:
                self.testOfSession2Sbj2()
            # 科目三情景一
            elif sbj.session == 3 and sbj.subject == 1:
                self.testOfSession3Sbj1()
            # 科目三情景二
            elif sbj.session == 3 and sbj.subject == 2:
                self.testOfSession3Sbj2()

        print("========================== 测试：完成 ==========================")
        plt.show()

    # 打印信息
    def printInfo(self, roadLineListList=None, segmentListList=None, pointIdListList=None):
        if roadLineListList is not None:
            print("\n············ 打印：RoadLineInfo ············")
            for roadLineList in roadLineListList:
                for omsId in roadLineList:
                    for i in range(0, 9):
                        roadLineId = str(omsId) + "/" + str(i)
                        if roadLineId not in self.map.roadLineHashMap:
                            break
                        else:
                            roadLine = self.map.roadLineHashMap[roadLineId]
                            print(str(roadLine))
                            pointList = roadLine.roadPointList
                            print(pointList)
        if segmentListList is not None:
            print("············ 打印:SegmentInfo ············")
            for segmentList in segmentListList:
                for segmentId in segmentList:
                    segment = self.map.segmentHashMap[segmentId]
                    print(str(segment))
                    pointList = segment.roadPointList
                    print(pointList)
        if pointIdListList is not None:
            print("············ 打印:RoadPointInfo ············")
            for pointIdList in pointIdListList:
                for pointId in pointIdList:
                    point = self.map.roadPointHashMap[pointId]
                    print(str(point))

    # 建立画布
    def buildCanvas(self):
        # 新建画布
        margin = 0.01
        self.canvas = Basemap(llcrnrlon=self.map.mapScale.minLongitude - margin,
                              llcrnrlat=self.map.mapScale.minLatitude - margin,
                              urcrnrlon=self.map.mapScale.maxLongitude + margin,
                              urcrnrlat=self.map.mapScale.maxLatitude + margin)
        return self.canvas

    # 绘制独立对象
    def drawObject(self, roadLineListList=None, segmentListList=None, pointIdListList=None, printString=True,
                   colorOfStr="black", colorOfLine=None, colorOfPoint=None, marker="o", s=50):
        if roadLineListList is not None:
            for roadLineList in roadLineListList:
                roadLines = []
                for roadLineOmsId in roadLineList:
                    for i in range(0, 9):
                        roadLineId = str(roadLineOmsId) + "/" + str(i)
                        if roadLineId not in self.map.roadLineHashMap:
                            break
                        roadLines.append(self.map.roadLineHashMap[roadLineId])
                drawLinesOrSegments(self.map, self.canvas, roadLines, printString=printString, colorOfStr=colorOfStr,
                                    colorOfLine=randomColor(), colorOfPoint=colorOfPoint, details=True, s=25)
        if segmentListList is not None:
            for segmentList in segmentListList:
                segments = []
                for segmentId in segmentList:
                    segment = self.map.segmentHashMap[segmentId]
                    segments.append(segment)
                drawLinesOrSegments(self.map, self.canvas, segments, printString=printString, colorOfStr=colorOfStr,
                                    colorOfLine=randomColor(), colorOfPoint=colorOfPoint, details=True, s=25)
        if pointIdListList is not None:
            for pointIds in pointIdListList:
                points = []
                for pointId in pointIds:
                    points.append(pointId)
                drawPoints(self.map, self.canvas, points, printString=printString, colorOfPoint=colorOfPoint,
                           colorOfStr=colorOfStr, marker=marker, s=s)

    # 绘制基本地图
    def drawBaseMap(self, drawBreakEvemtSegment=False):
        for segmentId, segment in self.map.segmentHashMap.items():
            if drawBreakEvemtSegment and len(segment.breakEventList) != 0:
                drawLineOrSegment(self.map, self.canvas, segment, printString=True,
                                  colorOfStr="black", colorOfLine="red", drawPoint=True, colorOfPoint="red",
                                  marker='v', s=100, details=True)
            elif drawBreakEvemtSegment and len(segment.oldBreakEventList) != 0:
                drawLineOrSegment(self.map, self.canvas, segment, printString=True,
                                  colorOfStr="black", colorOfLine="red", drawPoint=True, colorOfPoint="red",
                                  marker='^', s=100, details=True)
            else:
                drawLineOrSegment(self.map, self.canvas, segment, printString=False,
                                  colorOfStr="black", colorOfLine="gray", drawPoint=False, colorOfPoint="black",
                                  marker='o', s=25, details=True)

    # 静态地图测试
    def testOfStaticMap(self):
        # 打印不连通point
        print("-------------------------- 静态地图测试 --------------------------")
        print("·············· 绘制：地图中的不连通point ··············")
        self.printInfo(roadLineListList=None, segmentListList=None, pointIdListList=self.isolatedPoint)

        # 建立画布
        self.buildCanvas()
        # 绘制基本地图
        self.drawBaseMap()
        # 绘制额外对象
        self.drawObject(self.roadLineListList, self.segmentListList, self.pointIdListList,
                        printString=True, colorOfStr="black", colorOfLine=None, colorOfPoint=None, marker="o", s=100)
        # 绘制孤立点
        if self.isolatedPoint is not None:
            for pointIdList in self.isolatedPoint:
                drawPoints(self.map, self.canvas, pointIdList, printString=True, colorOfPoint='red', colorOfStr='black',
                           marker="s", s=50)

        plt.title('staticMap', fontsize=20)

    # session1sbj1测试
    def testOfSession1Sbj1(self):
        # 建立画布
        canvas = self.buildCanvas()
        colorList = []

        # 绘制自定义对象
        plt.subplot(2, 2, 1)
        # 绘制基本地图
        self.drawBaseMap()
        # # 绘制孤立点对象
        # self.drawObject(roadLineListList=None, segmentListList=None, pointIdListList=self.isolatedPoint,
        #                 printString=True, colorOfStr="black", colorOfLine=None, colorOfPoint='red', marker="s", s=50)
        # 绘制额外对象
        self.drawObject(self.roadLineListList, self.segmentListList, self.pointIdListList, printString=True,
                        colorOfStr="black", colorOfLine=None, colorOfPoint=None, marker="o", s=100)
        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': test' + str(self.sbj.sendId))
        print("············ 绘制:自定义对象绘制完成 ············")

        # 绘制算法结果
        plt.subplot(2, 2, 2)
        # 绘制基本地图
        self.drawBaseMap(drawBreakEvemtSegment=True)
        # 绘制结果
        for routine in self.res:
            colorList.append(randomColor())
            drawLinesOrSegments(self.map, canvas, routine, printString=False, colorOfStr="black",
                                colorOfLine=colorList[-1], drawPoint=False, colorOfPoint=colorList[-1], details=True,
                                s=25)
        # 绘制起点
        startPoint = self.map.roadPointHashMap[self.sbj.startPointId]
        canvas.scatter(startPoint.coordinate[1], startPoint.coordinate[0], latlon=True, color="red", marker="h",
                       s=200)
        plt.annotate("Start:" + str(startPoint.id), xy=(startPoint.getLongitude(), startPoint.getLatitude()),
                     c="black")
        # 绘制终点
        endPoint = self.map.roadPointHashMap[self.sbj.endPointId]
        canvas.scatter(endPoint.coordinate[1], endPoint.coordinate[0], latlon=True, color="green", marker="H",
                       s=200)
        plt.annotate("End:" + str(endPoint.id), xy=(endPoint.getLongitude(), endPoint.getLatitude()), c="black")
        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': res' + str(
                self.sbj.sendId) + '\nfind routine: ' + str(len(self.res)))
        print("············ 绘制:算法结果绘制完成 ············")

        # 绘制文件内容
        # 读取Json文件
        print('-------------------------- 测试:开始测试teamPath --------------------------')
        with open(self.sbj.subjectAddress + 'team_path_' + str(self.sbj.sendId) + '.json', "r", encoding="utf-8") as f:
            # 读入teamPath字典存储为 clientPath
            teamPath = json.load(f)
            # 读取sendId判断是否一致
            operateId = teamPath['operate_id']
            if operateId == self.sbj.sendId:
                print("············ 测试： 任务Id匹配 ············")
            else:
                print('!!!!!!!!!!!! 测试异常：任务Id不匹配 !!!!!!!!!!!!')
            # 读取路径并绘制
            pathsJson = teamPath['paths']
            for i in range(0, len(pathsJson)):
                plt.subplot(2, len(pathsJson), len(pathsJson) + 1 + i)
                plt.title('Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': \nfile' + str(
                    self.sbj.sendId) + ", path" + str(i + 1))
                # 绘制基本地图
                self.drawBaseMap()
                # 读取一条路径
                pathJson = pathsJson[i]
                # 存储point的经度
                x = []
                # 存储point的纬度
                y = []
                # 循环遍历point坐标，存储经纬度
                for j in range(0, len(pathJson)):
                    pointJson = pathJson[j]
                    x.append(pointJson['longitude'])
                    y.append(pointJson['latitude'])
                # 绘制segment
                canvas.plot(x, y, c=colorList[i], latlon=True)
                #     # 打印point的id
                #     if j % 1 == 0:
                #         plt.annotate("p:" + str(i) + '.' + str(j), xy=(pointJson['longitude'], pointJson['latitude']),
                #                      c='black')
                #
                # # 绘制本组point
                # canvas.scatter(x, y, latlon=True, color=color, marker='o', s=25)
                print('············ 绘制: teamPath' + str(i + 1) + '绘制完成 ············')

    # session1sbj2测试
    def testOfSession1Sbj2(self):
        # 建立画布
        canvas = self.buildCanvas()
        colorList = []

        # 绘制自定义对象
        plt.subplot(2, 2, 1)

        # 绘制基本地图
        self.drawBaseMap(drawBreakEvemtSegment=False)

        # # 绘制第二次出发起点
        # self.drawObject(roadLineListList=None, segmentListList=None, pointIdListList=[self.sbj.startPointIds],
        #                 printString=True, colorOfStr="black", colorOfLine=None, colorOfPoint='blue', marker="^", s=200)

        # 绘制额外对象
        self.drawObject(self.roadLineListList, self.segmentListList, self.pointIdListList, printString=True,
                        colorOfStr="black", colorOfLine=None, colorOfPoint=None, marker="o", s=100)

        # 绘制起点
        startPoint = self.map.roadPointHashMap[self.sbj.startPointId]
        canvas.scatter(startPoint.coordinate[1], startPoint.coordinate[0], latlon=True, color="red", marker="h",
                       s=200)
        plt.annotate("Start:" + str(startPoint.id), xy=(startPoint.getLongitude(), startPoint.getLatitude()),
                     c="black")
        # 绘制终点
        endPoint = self.map.roadPointHashMap[self.sbj.endPointId]
        canvas.scatter(endPoint.coordinate[1], endPoint.coordinate[0], latlon=True, color="green", marker="H",
                       s=200)
        plt.annotate("End:" + str(endPoint.id), xy=(endPoint.getLongitude(), endPoint.getLatitude()), c="black")

        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': test' + str(
                self.sbj.sendId))
        print("············ 绘制:自定义对象绘制完成 ············")

        # 绘制算法结果
        plt.subplot(2, 2, 2)
        # 绘制基本地图
        self.drawBaseMap(drawBreakEvemtSegment=True)

        # 绘制第一次寻路结果
        for i in range(0, len(self.res[0])):
            routine = self.res[0][i]
            segmentList = []
            for segment in routine:
                segmentList.append(segment)
            colorList.append(randomColor())
            drawLinesOrSegments(self.map, canvas, segmentList, printString=False, colorOfStr="black",
                                colorOfLine=colorList[-1], drawPoint=False, colorOfPoint=colorList[-1], details=True,
                                s=25)

        # 绘制第二次寻路结果
        for i in range(0, len(self.res[1])):
            routine = self.res[1][i]
            segmentList = []
            for segment in routine:
                segmentList.append(segment)
            drawLinesOrSegments(self.map, canvas, segmentList, printString=False, colorOfStr="black",
                                colorOfLine=colorList[i], drawPoint=True, colorOfPoint=colorList[i], details=True, s=25)

        # 绘制起点
        startPoint = self.map.roadPointHashMap[self.sbj.startPointId]
        canvas.scatter(startPoint.coordinate[1], startPoint.coordinate[0], latlon=True, color="red", marker="h", s=200)
        plt.annotate("Start:" + str(startPoint.id), xy=(startPoint.getLongitude(), startPoint.getLatitude()),
                     c="black")
        # 绘制终点
        endPoint = self.map.roadPointHashMap[self.sbj.endPointId]
        canvas.scatter(endPoint.coordinate[1], endPoint.coordinate[0], latlon=True, color="green", marker="H", s=200)
        plt.annotate("End:" + str(endPoint.id), xy=(endPoint.getLongitude(), endPoint.getLatitude()), c="black")
        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': res' + str(
                self.sbj.sendId) + '\nfind routine: ' + str(len(self.res)))
        print("············ 绘制:算法结果绘制完成 ············")

        # 绘制文件内容
        # 读取Json文件
        print('-------------------------- 测试:开始测试teamPath --------------------------')
        with open(self.sbj.subjectAddress + 'team_path_' + str(self.sbj.sendId) + '.json', "r",
                  encoding="utf-8") as f:
            # 读入teamPath字典存储为 clientPath
            teamPath = json.load(f)
            # 读取sendId判断是否一致
            operateId = teamPath['operate_id']
            if operateId == self.sbj.sendId:
                print("············ 测试： 任务Id匹配 ············")
            else:
                print('!!!!!!!!!!!! 测试异常：任务Id不匹配 !!!!!!!!!!!!')

            # 读取路径并绘制
            pathsJson = [teamPath['firstPoints'], teamPath['secondPathInfos']]
            for i in range(0, len(pathsJson[0])):
                plt.subplot(2, len(pathsJson[0]), len(pathsJson[0]) + 1 + i)
                plt.title('Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': \nfile' + str(
                    self.sbj.sendId) + ", path" + str(i + 1))

                # 绘制基本地图
                self.drawBaseMap(drawBreakEvemtSegment=True)

                # 打印第一次寻路结果
                pathJson = pathsJson[0][i]
                # 存储point的经度
                x = []
                # 存储point的纬度
                y = []
                # 循环遍历point坐标，存储经纬度
                for j in range(0, len(pathJson)):
                    pointJson = pathJson[j]
                    x.append(pointJson['longitude'])
                    y.append(pointJson['latitude'])
                # 绘制segment
                canvas.plot(x, y, c=colorList[i], latlon=True)

                # 绘制第二次寻路结果
                if i < len(pathsJson[1]):
                    secondPathInfos = pathsJson[1][i]
                    roadId = secondPathInfos['road_id']
                    pathJson = secondPathInfos['paths']
                    # 存储point的经度
                    x = []
                    # 存储point的纬度
                    y = []
                    if len(pathJson) > 0:
                        # 循环遍历point坐标，存储经纬度
                        for j in range(0, len(pathJson)):
                            pointJson = pathJson[j]
                            x.append(pointJson['longitude'])
                            y.append(pointJson['latitude'])
                        # 绘制segment
                        canvas.plot(x, y, c='black', latlon=True)
                        canvas.scatter(x, y, latlon=True, color="red", marker='o', s=10)
                    # 绘制第二次寻路起点
                    newStartPointId = self.sbj.startPointIds[i]
                    newStartPoint = self.map.getPoint(newStartPointId)
                    canvas.scatter(newStartPoint.getLongitude(), newStartPoint.getLatitude(), latlon=True,
                                   color='black', marker='^', s=150)
                print('············ 绘制: teamPath' + str(i + 1) + '绘制完成 ············')

                #     # 打印point的id
                #     if j % 1 == 0:
                #         plt.annotate("p:" + str(i) + '.' + str(j), xy=(pointJson['longitude'], pointJson['latitude']),
                #                      c='black')
                #
                # # 绘制本组point
                # canvas.scatter(x, y, latlon=True, color=color, marker='o', s=25)

    def testOfSession2Sbj1(self):
        # 读取Json文件
        print('-------------------------- 测试:开始测试teamPath --------------------------')
        with open(self.sbj.subjectAddress + 'team_path_' + str(self.sbj.sendId) + '.json', "r", encoding="utf-8") as f:
            # 读入teamPath字典存储为 clientPath
            teamPath = json.load(f)
            # 读取sendId判断是否一致
            operateId = teamPath['operate_id']
            if operateId == self.sbj.sendId:
                print("············ 测试： 任务Id匹配 ············")
            else:
                print('!!!!!!!!!!!! 测试异常：任务Id不匹配 !!!!!!!!!!!!')
            rescuePeopleTotal = teamPath['rescue_people_total']
            print('············ rescuePeopleTotal = ' + str(rescuePeopleTotal) + ' ············')
        # img = Image.open(self.sbj.imagesAddress + 'result.png')
        # img.show()

    def testOfSession2Sbj2(self):
        # 建立画布
        canvas = self.buildCanvas()
        colorList = []

        # 绘制自定义对象
        plt.subplot(2, 2, 1)
        # 绘制基本地图
        self.drawBaseMap()

        # 绘制额外对象
        self.drawObject(self.roadLineListList, self.segmentListList, self.pointIdListList, printString=True,
                        colorOfStr="black", colorOfLine=None, colorOfPoint=None, marker="o", s=100)
        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': test' + str(
                self.sbj.sendId))
        print("············ 绘制:自定义对象绘制完成 ············")

        # 绘制算法结果
        plt.subplot(2, 2, 2)
        # 绘制基本地图
        self.drawBaseMap(drawBreakEvemtSegment=True)

        # # 绘制结果
        # for routine in self.res:
        #     colorList.append(randomColor())
        #     drawLinesOrSegments(self.map, canvas, routine, printString=False, colorOfStr="black",
        #                         colorOfLine=colorList[-1], drawPoint=False, colorOfPoint=colorList[-1],
        #                         details=True, s=25)

        # 绘制人员
        x = [[], [], [], [], [], []]
        y = [[], [], [], [], [], []]
        colorList = ['#00FF00', '#0000FF', '#FF6100', '#8B4513', '#FF0000', '#FFFFFF']

        # 按照人员类型标记颜色
        for people in self.map.peopleHashMap.values():
            type = people.type
            x[type - 1].append(people.coordinate[1])
            y[type - 1].append(people.coordinate[0])
            # plt.annotate("Init:" + str(people.id), xy=(people.coordinate[1], people.coordinate[0]), c="black")
        for i in range(0, 6):
            canvas.scatter(x[i], y[i], latlon=True, color=colorList[i], marker="o", s=10)

        # # 按照起始点不同标记颜色
        # for people in self.map.peopleHashMap.values():
        #     initPointId = people.initPointId
        #     index = self.sbj.initPointList.index(initPointId)
        #     x[index].append(people.coordinate[1])
        #     y[index].append(people.coordinate[0])
        #     # plt.annotate("Init:" + str(people.id), xy=(people.coordinate[1], people.coordinate[0]), c="black")
        # for i in range(0, 5):
        #     canvas.scatter(x[i], y[i], latlon=True, color=colorList[i], marker="o", s=10)

        # # 绘制起始点
        # x = []
        # y = []
        # for pointId in self.sbj.startPointList:
        #     point = self.map.getPoint(pointId=pointId)
        #     x.append(point.getLongitude())
        #     y.append(point.getLatitude())
        #     plt.annotate("Init:" + str(point.id), xy=(point.getLongitude(), point.getLatitude()), c="black")
        # canvas.scatter(x, y, latlon=True, color="red", marker="h", s=100)
        # canvas.scatter(x, y, latlon=True, color="black", marker="h", s=50)

        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': res' + str(self.sbj.sendId))
        print("············ 绘制:算法结果绘制完成 ············")


        # 读取Json文件
        print('-------------------------- 测试:开始测试teamPath --------------------------')
        with open(self.sbj.subjectAddress + 'team_path_' + str(self.sbj.sendId) + '.json', "r", encoding="utf-8") as f:
            # 读入teamPath字典存储为 clientPath
            teamPath = json.load(f)
            # 读取sendId判断是否一致
            operateId = teamPath['operate_id']
            if operateId == self.sbj.sendId:
                print("············ 测试： 任务Id匹配 ············")
            else:
                print('!!!!!!!!!!!! 测试异常：任务Id不匹配 !!!!!!!!!!!!')

    # session3sbj1测试
    def testOfSession3Sbj1(self):
        # 建立画布
        canvas = self.buildCanvas()
        colorList = []

        # 绘制自定义对象
        plt.subplot(2, 2, 1)
        # 绘制基本地图
        self.drawBaseMap()
        # # 绘制孤立点对象
        # self.drawObject(roadLineListList=None, segmentListList=None, pointIdListList=self.isolatedPoint,
        #                 printString=True, colorOfStr="black", colorOfLine=None, colorOfPoint='red', marker="s", s=50)
        # 绘制额外对象
        self.drawObject(self.roadLineListList, self.segmentListList, self.pointIdListList, printString=True,
                        colorOfStr="black", colorOfLine=None, colorOfPoint=None, marker="o", s=100)
        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': test' + str(
                self.sbj.sendId))
        print("············ 绘制:自定义对象绘制完成 ············")

        # 绘制算法结果
        plt.subplot(2, 2, 2)
        # 绘制基本地图
        self.drawBaseMap(drawBreakEvemtSegment=True)

        # # 绘制结果
        # for routine in self.res:
        #     colorList.append(randomColor())
        #     drawLinesOrSegments(self.map, canvas, routine, printString=False, colorOfStr="black",
        #                         colorOfLine=colorList[-1], drawPoint=False, colorOfPoint=colorList[-1],
        #                         details=True, s=25)





        # 绘制人员
        x = [[], [], [], [], [], []]
        y = [[], [], [], [], [], []]
        colorList = ['#00FF00', '#0000FF', '#FF6100', '#8B4513', '#FF0000', '#FFFFFF']

        # 按照人员类型标记颜色
        for people in self.map.peopleHashMap.values():
            type = people.type
            x[type-1].append(people.coordinate[1])
            y[type-1].append(people.coordinate[0])
            # plt.annotate("Init:" + str(people.id), xy=(people.coordinate[1], people.coordinate[0]), c="black")
        for i in range(0, 6):
            canvas.scatter(x[i], y[i], latlon=True, color=colorList[i], marker="o", s=10)

        # # 按照起始点不同标记颜色
        # for people in self.map.peopleHashMap.values():
        #     initPointId = people.initPointId
        #     index = self.sbj.initPointList.index(initPointId)
        #     x[index].append(people.coordinate[1])
        #     y[index].append(people.coordinate[0])
        #     # plt.annotate("Init:" + str(people.id), xy=(people.coordinate[1], people.coordinate[0]), c="black")
        # for i in range(0, 5):
        #     canvas.scatter(x[i], y[i], latlon=True, color=colorList[i], marker="o", s=10)

        # 绘制起始点
        x = []
        y = []
        for pointId in self.sbj.initPointList:
            point = self.map.getPoint(pointId=pointId)
            x.append(point.getLongitude())
            y.append(point.getLatitude())
            plt.annotate("Init:" + str(point.id), xy=(point.getLongitude(), point.getLatitude()), c="black")
        canvas.scatter(x, y, latlon=True, color="red", marker="h", s=100)
        canvas.scatter(x, y, latlon=True, color="black", marker="h", s=50)

        # 绘制目标点
        x = []
        y = []
        for pointId in self.sbj.placePointList:
            point = self.map.getPoint(pointId=pointId)

            x.append(point.getLongitude())
            y.append(point.getLatitude())
            plt.annotate("Place:" + str(point.id), xy=(point.getLongitude(), point.getLatitude()), c="black")
        canvas.scatter(x, y, latlon=True, color="red", marker="H", s=100)
        canvas.scatter(x, y, latlon=True, color="black", marker="H", s=50)

        # 绘制标题
        plt.title(
            'Session' + str(self.sbj.session) + ' Subject' + str(self.sbj.subject) + ': res' + str(self.sbj.sendId))
        print("············ 绘制:算法结果绘制完成 ············")
