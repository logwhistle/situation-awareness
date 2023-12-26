
class MapScale:

    # 初始化StaticMap类
    def __init__(self) -> None:
        # 存储最西端经度
        self.minLongitude = float("inf")
        # 存储最东端经度
        self.maxLongitude = 0
        # 存储最北端纬度
        self.maxLatitude = 0
        # 存储最南端纬度
        self.minLatitude = float("inf")

    # 从coordinate获得数据，更新画幅大小
    def refreshScale(self, coordinate):
        # flag = False

        if coordinate[0] < self.minLatitude:
            self.minLatitude = coordinate[0]
            flag = True

        if coordinate[0] > self.maxLatitude:
            self.maxLatitude = coordinate[0]
            flag = True

        if coordinate[1] < self.minLongitude:
            self.minLongitude = coordinate[1]
            flag = True

        if coordinate[1] > self.maxLongitude:
            self.maxLongitude = coordinate[1]
            flag = True

        # if flag:
        #     print("点坐标：" + str(coordinate))
        #     print(str(self))

    # 输出画幅大小
    def __str__(self):
        return "画幅大小为：" + "\n"\
               "最小经度为：" + str(self.minLongitude) + "\n"\
               "最大经度为：" + str(self.maxLongitude) + "\n"\
               "最小纬度为：" + str(self.minLatitude) + "\n"\
               "最大纬度为：" + str(self.maxLatitude) + "\n"
