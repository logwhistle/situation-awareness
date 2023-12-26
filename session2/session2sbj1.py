from interface.Subject import Subject
from session2.main import map_snitching
import json


# 科目二情景一
class Session2Sbj1(Subject):
    def __init__(self, rootAddress, FileNumber, staticMap, BreakInfo):
        super().__init__(rootAddress=rootAddress, FileNumber=FileNumber, staticMap=staticMap, BreakInfo=BreakInfo)
        self.session = 2
        self.subject = 1
        # 科目与情景地址
        self.subjectAddress = rootAddress + 'session_' + str(self.session) + '\\subject_' + str(self.subject) + '\\'
        # 图片地址
        self.imagesAddress = self.subjectAddress + 'images_' + str(self.fileNumber) + '\\'

        # 解析任务信息
        self.parseClientPathFile(self.subjectAddress + "client_path_" + str(self.fileNumber) + ".json")

        # 调用算法
        self.algorithmRes = self.algorithmRun()

        # 生成文件
        self.generateFiles()

    # 将数据结构传输给算法进行路径查找
    def algorithmRun(self):
        return map_snitching(self.imagesAddress)

    # 生成文件
    def generateFiles(self):
        print("========================== 处理结果并写出文件 ==========================")
        self.fileRes = dict()
        self.fileRes['operate_id'] = self.sendId
        self.fileRes['rescue_people_total'] = self.algorithmRes
        self.fileRes['pic_path'] = self.imagesAddress
        # 写出json文件
        with open(self.subjectAddress + 'team_path_' + str(self.sendId) + '.json', 'w')as f:
            json.dump(obj=self.fileRes, fp=f)
        print("========================== 结果已处理完成且文件已写出 ==========================")


