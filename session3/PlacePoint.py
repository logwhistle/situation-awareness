class PlacePoint:
    def __init__(self, idOfPlacePoint=0, typeOfPlacePoint=0, coordinate=None, radius=0, idOfPoint=0):
        self.id = idOfPlacePoint
        self.type = typeOfPlacePoint
        self.coordinate = coordinate
        self.radius = radius
        self.pointId = idOfPoint

    # 转化成字符串
    def __str__(self) -> str:
        return "PlacePoint { " + \
               "id=" + str(self.id) + \
               ", type=" + str(self.type) + \
               ", coordinate=" + str(self.coordinate) + \
               ", radius=" + str(self.radius) + \
               ", pointId=" + str(self.pointId) + \
               ' }'
