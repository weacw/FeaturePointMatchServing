from ImageMatch.Cores import *

class ImageTrain():
    def __init__(self, db_name):
        """初始化
           Args:
            db_name (string): 数据库名称
        """
        self.desArray = []
        self.db_name = db_name
        self.annoyindx = AnnoyIndex_driver(db_name)

    def addMarkerDes(self, id, des):
        """添加单个识别图数据

        Args:
            des (description): 通过opencv orb展开的图像描述符
        """
        if isinstance(des, np.ndarray) is False:
            des = np.array(des)

        desDict = dict()
        desDict['id'] = id
        desDict['des'] = des
        self.desArray.append(desDict)

    def generateMarkerDB(self):
        """用于生成追踪数据库

        Returns:
            Bool: True即为构建数据库成功，反之则为失败
        """
        try:        
            self.annoyindx.buildAnnoyIndexDB(self.desArray)
            return True
        except Exception:
            print(Exception)
            return False
