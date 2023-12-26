import math
import random


# from geopy import distance


# 计算两点之间的距离
def pointDistance(x1, y1, x2, y2):
    lineLength = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    return lineLength


# 计算点到直线距离
def pointToLineDistance(*args):
    if len(args) == 3:
        A2B, S2A, S2B = args
    elif len(args) == 6:
        x1, y1, x2, y2, x0, y0 = args
        # 线段的长度
        A2B = pointDistance(x1, y1, x2, y2)
        # (x1,y1)到点的距离
        S2A = pointDistance(x1, y1, x0, y0)
        # (x2,y2)到点的距离
        S2B = pointDistance(x2, y2, x0, y0)
        # 返回点到直线的距离
    else:
        raise ValueError
    return pointToLineDistance_(A2B, S2A, S2B)


def pointToLineDistance_(A2B, S2A, S2B):
    # 待测点与线段两段任意一点距离小于误差值则判断该点和端点重合，点到线的距离为0
    if S2B <= 0.000001 or S2A <= 0.000001:
        space = 0
        return space
    # 线段两段的距离小于误差值，则将该线段视为一个点，返回到其中一点的距离
    if A2B <= 0.000001:
        space = S2A
        return space
    # 过该点到线段的垂足不在线上，则返回与距离较近的端点的距离
    if S2B * S2B >= A2B * A2B + S2A * S2A:
        space = S2A
        return space
    if S2A * S2A >= A2B * A2B + S2B * S2B:
        space = S2B
        return space
    # 半周长p
    p = (A2B + S2A + S2B) / 2
    temp = p * (p - A2B) * (p - S2A) * (p - S2B)
    '''
    # 待调试与优化
    '''
    if temp <= 0:
        return 0

    # 海伦公式求面积
    s = math.sqrt(temp)
    # 返回点到线的距离(利用三角形面积公式求高)
    space = 2 * s / A2B
    return space


# 从字符串提取数字
def extractNum(string):
    tempStr = ''
    if '9' >= string[0] >= '0':
        for char in string:
            if ('9' >= char >= '0') or char == '.':
                tempStr += char
            else:
                break
    if tempStr == '':
        return None
    elif float(tempStr) % 1 == 0:
        return int(tempStr)
    else:
        return float(tempStr)


# 限制double精度
# 小数处理精度的位数，默认五位小数，每隔0.0001度，距离相差约10米
static_prec = 5


# 自定义精度
def precision(*args):
    if len(args) == 1:
        num = args[0]
        # 默认精度为小数点后5为
        prec = static_prec
    elif len(args) == 2:
        num, prec = args
    else:
        raise ValueError
    # 精度为-1时不进行精度限制
    if prec == -1:
        return num
    return round(num, prec)


# 判断坐标是否相同
def isSamePoint(coordinate1, coordinate2):
    return coordinate1[0] == coordinate2[0] and coordinate1[1] == coordinate2[1]


# 判断坐标是否相近
# 默认距离到达static_edge以内则为相近点
static_edge = 2


def isClosePoint(coordinate1, coordinate2):
    dis = getDistanceMeter(coordinate1, coordinate2)
    return dis < static_edge


# 计算两个经纬度坐标之间的距离
def getDistanceMeter(p1, p2):
    r = 6378137
    PI = 3.1415926535898
    x1 = p1[0] * PI / 180
    x2 = p2[0] * PI / 180
    y1 = p1[1] * PI / 180
    y2 = p2[1] * PI / 180
    dx = math.fabs(x1 - x2)
    dy = math.fabs(y1 - y2)
    p = math.pow(math.sin(dx / 2), 2) + math.cos(x1) * math.cos(x2) * math.pow(math.sin(dy / 2), 2)
    d = r * 2 * math.asin(math.sqrt(p))
    return d


# 判断Point是否包含在RoadLine中
def indexOfPoint(coordinates, roadPointCoordinate, wide):
    # 存储结果的索引
    index = 0
    # 存储最短距离
    minDistance = float("inf")
    # 是否与点相近
    isPoint = None

    # 计算待测Point与线段头端点的距离
    S2A = getDistanceMeter(roadPointCoordinate, coordinates[0])
    # 距离小于1米，则认为待测Point与RoadLine起始点匹配，更新最短距离与索引
    if S2A < 2:
        minDistance = S2A
        index = 0
        isPoint = True

    # 循环遍历匹配RoadLine的所有点
    for i in range(1, len(coordinates)):
        # 获取线段的头端点坐标
        source1 = coordinates[i - 1]
        # 获取线段的尾端点坐标
        source2 = coordinates[i]

        # 获取线段长度
        A2B = getDistanceMeter(source1, source2)
        # 计算待测Point与线段尾端点的距离
        S2B = getDistanceMeter(roadPointCoordinate, source2)
        # 计算点到直线距离
        dis = pointToLineDistance(A2B, S2A, S2B)
        # pointOnLine = (A2B ** 2 + S2B ** 2) > S2A ** 2 and A2B ** 2 + S2A ** 2 > S2B ** 2

        # 如果待测Point到线段尾端点的距离小于当前最小距离，则记录最小距离与索引
        if S2B < 2 and S2B < minDistance:
            minDistance = S2B
            index = i
            isPoint = True
        # 如果点到直线距离小于当前记录的最小距离，则记录最小距离与索引
        if dis < minDistance:
            minDistance = dis
            index = i
            isPoint = False

        # 为下一次循环做准备
        S2A = S2B

    # 设定一个判断Point在RoadLine的距离阈值
    edge = wide / 2
    if static_prec == 5:
        edge = wide * 2

    # 若最小值在阈值内，则输出对应的索引，否则输入-1
    if minDistance <= edge:
        return [isPoint, index, minDistance]
    return [None, index, minDistance]


# 向List中添加元素并去重，返回是否List[是否添加成功，添加后的List]
def addToList(list, obj, index=None):
    # 如果传入的pointId为空，返回false
    if (isinstance(obj, int) and obj > 0) or isinstance(obj, str):
        # 在表中还未记录当前值，则记录进表中，返回true
        if obj not in list:
            # 无给定的index
            if index is None:
                list.append(obj)
            # 给定了index
            else:
                list.insert(index, obj)
            return [True, list]
    # 已经记录在表中，则不记录，返回None
    return [False, list]


# 检查staticMap的连通性（昊艺）
def connectState(staticMap):
    pointMap = staticMap.keyPointIndexHashMap
    segementMap = staticMap.segmentHashMap
    n = len(pointMap)
    res = {}
    uf = UnionFind(pointMap)
    # 合并各个集合
    for _, v in segementMap.items():
        uf.union(v.roadPointList[0], v.roadPointList[-1])
    # 取出合并后的集合
    for _, v in pointMap.items():
        p = uf.find(uf.parent[v])
        if p not in res:
            res[p] = []
        cur = res[p]
        cur.append(v)
        res[p] = cur
    print("·············· map中相互连同的区域共有" + str(len(res)) + "片 ··············")
    # print("····························")
    list = []
    maxLength = 0
    maxLengthIndex = -1
    for _, v in res.items():
        list.append(v)
        if len(v) > maxLength:
            maxLength = len(v)
            maxLengthIndex = len(list) - 1
        print("连同区域：" + str(v))
    list.pop(maxLengthIndex)
    return list


def calculateDistance(segment, latitude, longtitude):
    return random.randint(0, 20)


# 并查集（昊艺）
class UnionFind():
    def __init__(self, pointMap):
        self.parent = dict()
        for _, pointId in pointMap.items():
            self.parent[pointId] = pointId

    def find(self, i):
        while self.parent[i] != i:
            i = self.parent[i]
        return i

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)
        return


if __name__ == "__main__":
    print("\n\n=========================单元测试=========================")

    print("-----pointDistance函数：计算两点之间距离-----")
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 4
    print("点1为（", x1, ", ", y1, "）")
    print("点2为（", x2, ", ", y2, "）")
    pointdistance = pointDistance(x1, y1, x2, y2)
    print("点1与点2之间的距离为：", pointdistance, "\n")

    print("-----pointToLineDistance函数：计算点到直线之间距离-----")
    x0 = 3
    y0 = 0
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 4
    print("点0为（", x0, ", ", y0, "）")
    print("点1为（", x1, ", ", y1, "）")
    print("点2为（", x2, ", ", y2, "）")
    pointtoLinedistance = pointToLineDistance(x1, y1, x2, y2, x0, y0)
    print("点0到点1与点2连线的距离为：", pointtoLinedistance, "\n")

    print("-----extractNum函数：从字符串提取数字-----")
    inputString = "18.1"
    print("inputString = ", inputString)
    extractnum = extractNum(inputString)
    print("字符串中的数字为：", extractnum, ", 数据类型为", type(extractnum), "\n")

    print("-----precision函数：限制数字精度-----")
    inputNum = 11.123456
    print("inputString = ", inputNum)
    num = precision(inputNum)
    print("精度为小数点后", static_prec, "位小数")
    print("精度降低后的值为：", num, ", 数据类型为", type(num), "\n")

    list1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    list2 = [10, 12, 13, 14, 15, 16]
    if list1[-1] == list2[0]:
        list2.pop(0)
    list1 += list2
    print(list1)
