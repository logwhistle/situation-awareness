
class People:

    def __init__(self, idOfPeople=0, typeOfPeople=0, coordinate=None, pointId=0, initPointId=0, densityOfPeople=[]):
        # id
        self.id = idOfPeople
        # 类型
        self.type = typeOfPeople
        # 坐标
        self.coordinate = coordinate
        # 所在pointId
        self.pointId = pointId
        # 初始点initPointId
        self.initPointId = initPointId
        # 人口密度
        self.densityOfPeople = densityOfPeople

    # 转化成字符串
    def __str__(self) -> str:
        return "People { " + \
               "id=" + str(self.id) + \
               ", type=" + str(self.type) + \
               ", coordinate=" + str(self.coordinate) + \
               ", pointId=" + str(self.pointId) + \
               ", initPointId=" + str(self.initPointId) + \
               ", densityOfPeople=" + str(self.densityOfPeople) + \
               ' }'
