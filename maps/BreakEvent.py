
class BreakEvent:
    # 数字id的起始编号，从1开始赋值
    intIdStart = 0

    # 构造器
    def __init__(self, omsId, isNew, breakType, breakLevel, happendTime, continueTime, roadPointList):
        # break事件的id
        BreakEvent.intIdStart += 1
        self.breakEventId = BreakEvent.intIdStart
        # omsId
        self.omsId = omsId
        # 是否是newBreakEvent
        self.isNew = isNew
        # breakType灾害类型
        self.breakType = breakType
        # breakLevel灾害等级
        self.breakLevel = breakLevel
        # happendTime发生时间
        self.happendTime = happendTime
        # continueTime持续时间
        self.continueTime = continueTime
        # 端点索引
        self.roadPointList = roadPointList
        # breakEvent发生时的通行速度
        self.speed = None

    # 转化成字符串
    def __str__(self) -> str:
        return "BreakEvent { " + \
               "breakEventId=" + str(self.breakEventId) + \
               ", omsId=" + str(self.omsId) + \
               ", isNew=" + str(self.isNew) + \
               ", breakType=" + str(self.breakType) + \
               ", breakLevel=" + str(self.breakLevel) + \
               ", happendTime=" + str(self.happendTime) + \
               ", continueTime=" + str(self.continueTime) + \
               ", roadPointList=" + str(self.roadPointList) + \
               ' }'