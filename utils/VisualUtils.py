import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import random

# 获得随机颜色
import maps.StaticMap


def randomColor():
    # 高对比度域
    # 随机生成红色值
    value = [random.randint(16, 50), random.randint(200, 255)]
    red = value[random.randint(0, 1)]
    # 随机生成绿色值
    value = [random.randint(16, 50), random.randint(200, 255)]
    green = value[random.randint(0, 1)]
    # 随机生成蓝色值
    value = [random.randint(16, 50), random.randint(200, 255)]
    if red < 100 and green < 100:
        blue = value[1]
    elif red > 100 and green > 100:
        blue = value[0]
    else:
        blue = value[random.randint(0, 1)]
    # 生成颜色
    color = hex(red)[-2:] + hex(green)[-2:] + hex(blue)[-2:]
    # 返回颜色值
    return "#" + color

    # # 全颜色域
    # colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    # color = ""
    # for i in range(6):
    #     color += colorArr[random.randint(0, 14)]
    # return "#" + color


# 绘制一组point
def drawPoints(map, canvas, points, printString=False, colorOfPoint=None, colorOfStr="black", marker="o", s=25):
    # 存储point的经度
    x = []
    # 存储point的纬度
    y = []
    # 如果没有给定颜色，则随机生成这一组点的颜色
    if colorOfPoint is None:
        colorOfPoint = randomColor()
    # 循环遍历point坐标，存储经纬度
    for point in points:
        if isinstance(point, int):
            point = map.getPoint(point)
        x.append(point.getLongitude())
        y.append(point.getLatitude())
        # 打印point的id
        if printString:
            plt.annotate("p:" + str(point.id), xy=(point.getLongitude(), point.getLatitude()), c=colorOfStr)
    # 绘制本组point
    canvas.scatter(x, y, latlon=True, color=colorOfPoint, marker=marker, s=s)


# 绘制路线
def drawLineOrSegment(map, canvas, lineOrSegment, printString=False, colorOfStr="black",
                      colorOfLine="gray", drawPoint=True, colorOfPoint="black", marker='o', s=25, details=True):
    if isinstance(lineOrSegment, str) or isinstance(lineOrSegment, int):
        lineOrSegment = map.getRoadLineOrSegment[lineOrSegment]
    pointList = []
    # 不绘制细节信息
    if not details:
        # 获取起点终点
        pointList = [map.getPoint(lineOrSegment.roadPointList[0]), map.getPoint(lineOrSegment.roadPointList[-1])]
    # 绘制细节信息
    else:
        # 获取所有point
        for pointId in lineOrSegment.roadPointList:
            pointList.append(map.getPoint(pointId))
    # 存储point的经度
    x = []
    # 存储point的纬度
    y = []
    # 遍历点，添加经度与纬度
    for i in range(0, len(pointList)):
        x.append(pointList[i].getLongitude())
        y.append(pointList[i].getLatitude())
    # 绘制路线
    canvas.plot(x, y, c=colorOfLine, latlon=True)
    # 打印路线Id
    if printString:
        x = (pointList[int(len(pointList) / 2) - 1].getLongitude() + pointList[
            int(len(pointList) / 2)].getLongitude()) / 2
        y = (pointList[int(len(pointList) / 2) - 1].getLatitude() + pointList[
            int(len(pointList) / 2)].getLatitude()) / 2
        if lineOrSegment.type == "Segment":
            plt.annotate("s:" + str(lineOrSegment.id), xy=(x, y), c=colorOfStr)
        if lineOrSegment.type == "RoadLine":
            plt.annotate("l:" + str(lineOrSegment.id), xy=(x, y), c=colorOfStr)
    # 绘制起点终点
    if drawPoint:
        drawPoints(map, canvas, [pointList[0].id, pointList[-1].id], printString=printString, colorOfPoint=colorOfPoint,
                   colorOfStr=colorOfStr, marker=marker, s=s)


# 绘制一组路线
def drawLinesOrSegments(map, canvas, lines, printString=False, colorOfStr="black", colorOfLine=None, drawPoint=True,
                        colorOfPoint=None, details=True, s=25):
    # 如果没有设置line颜色，则随机生成一个颜色
    if colorOfLine == None:
        colorOfLine = randomColor()
    # 如果point的颜色没有设置，则颜色跟随point
    if colorOfPoint == None:
        colorOfPoint = colorOfLine
    # 遍历一组路线
    for i in range(0, len(lines)):
        line = lines[i]
        drawLineOrSegment(map, canvas, lineOrSegment=line, printString=printString, colorOfStr=colorOfStr,
                          colorOfLine=colorOfLine, drawPoint=drawPoint, colorOfPoint=colorOfPoint, marker='o', s=s,
                          details=details)
