import json
import pandas
import datetime
import requests

class GetSeatInfo():
    def __init__(self):
        self.client = requests.Session()
        self.headers = {
            'Referer': 'http://libzw.csu.edu.cn/home/web/seat/area/1'
        }
        
    def get_date(self):
        '''
        以形如2022-2-2的形式返回明天的日期
        '''
        SHA_TZ = datetime.timezone(
            datetime.timedelta(hours=8),
            name='Asia/Shanghai',
        )
        # 北京时间
        today = datetime.datetime.now(tz = SHA_TZ).date()
        tomorrow = today + datetime.timedelta(days = 1)
        return "%d-%d-%d" % (tomorrow.year, tomorrow.month, tomorrow.day)

    def get_seat_info(self, area, csv):
        '''
        图书馆area是树状分布的，比如`新校区`的areaid为1，它拥有孩子节点`一楼`（areaid为115）、`二楼`（areaid为2）、`三楼`（areaid为3）......
        而`二楼`拥有孩子节点`A区（areaid为43）`、`B区（areaid为41）`、`C区（areaid为42）`
        `A区`则不再有孩子节点，因为其下基本单元就不是区域，而是座位了
        
        本函数只需传入一个节点以及一个csv文件存储位置，就能找到该节点对应子树的所有叶子节点，进而将属于该大区域的所有座位信息存入指定的csv文件
        :param area: 区域id号，其中区域可以是诸如 新校区、新校区2楼、新校区2楼A区 此类的区域
        :csv: csv文件保存位置
        '''
        response = self.client.get("http://libzw.csu.edu.cn/api.php/v3areas/"+str(area), headers = self.headers)
        childArea = response.json()["data"]["list"]["childArea"]
        if childArea == None :
            url2 = "http://libzw.csu.edu.cn/api.php/spaces_old?area=" + str(area) + "&segment=" + str(self.get_booktime_id(area)[1]) + "&day=" + self.get_date() + "&startTime=07:30&endTime=22:00"
            response2 = self.client.get(url2, headers = self.headers)
            df = pandas.DataFrame(data = response2.json()["data"]["list"])
            df.to_csv(csv, mode = 'a', header = 0, index = 0)
            return
        else:
            for i in childArea:
                self.get_seat_info(i["id"], csv)

    def get_booktime_id(self, i):
        '''
        每天不同的area都有一个独特的bookTimeId
        该函数返回今天和明天的bookTimeId
        :param i: area编号
        '''
        url = "http://libzw.csu.edu.cn/api.php/v3areadays/" + str(i)
        response = self.client.get(url, headers = self.headers)
        return response.json()["data"]["list"][0]["id"], response.json()["data"]["list"][1]["id"]

collector = GetSeatInfo()
collector.get_seat_info(1, "./新校区座位表2.csv") #新校区id为1
collector.get_seat_info(28, "./铁道校区座位表2.csv") #铁道校区id为28
collector.get_seat_info(71, "./湘雅新校区座位表2.csv") #湘雅新校区id为71
collector.get_seat_info(94, "./本部校区座位表2.csv") #本部校区id为94
