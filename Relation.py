import requests,sys,json,os,pyqrcode,time,requests.utils
from datetime import datetime


BASEDIR = os.path.dirname(os.path.realpath( sys.argv[0]))

class Relation:


    def main(self):
        self.init()
        self.start()
        self.log('=============================操作完成=============================')


# 复制/移动用户到关注列表
    def usersToTag(self,tagid,array):
        url = "https://api.bilibili.com/x/relation/tags/addUsers"
        users = ','.join(str(x) for x in array)
        params = {
            "fids": users,
            "tagids":tagid,
            "csrf":self.CONFIG['Cookies']['bili_jct']
        }
        data = self.sess.post(url=url,data=params).json()
        if data['code'] !=0 : 
            self.log('****分组操作失败')
            self.log(data)


# 关注/取关 操作: 如果type=1 则批量关注，否则遍历取关
    def modify(self,array,type):
        if array == [] : 
            self.log('操作用户列表为空') 
            return
        if type == 1 :
            users = ','.join(str(x) for x in array)
            params = {
                "fids" :users,
                "act":1,
                "re_src":11,
                "csrf":self.CONFIG['Cookies']['bili_jct']
            }
            data = self.sess.post(url="https://api.bilibili.com/x/relation/batch/modify",data=params).json()
            if data['code'] !=0 : self.log('****关注操作失败'+data)
            return
        else :
            for id in array:
                params = {
                    "fids" :id,
                    "act":2,
                    "re_src":11,
                    "csrf":self.CONFIG['Cookies']['bili_jct']
                }
                data = self.sess.post(url="https://api.bilibili.com/x/relation/batch/modify",data=params).json()
                if data['code'] !=0 : self.log('****取关操作失败'+data)
                


# 获取关注tag的用户列表
    def getUserBytag(self,tagid,index):
        self.log('获取关注tag用户列表次数='+str(index))
        data = self.sess.get("https://api.bilibili.com/x/relation/tag?tagid="+str(tagid)+"&pn="+str(index)).json()
        # 如果没有数据后返回
        if data['data'] == [] : return
        self.getUserBytag(tagid,index+1)
        # 获取关注列表中的用户
        for i in data['data']:
            if i['uname'] == '账号已注销' :
                self.log('已注销用户,不添加到关注分组中,id'+str(i['mid']))
                continue
            self.followings.append(i['mid'])
        if data['code'] != 0 : self.log('****获取分组用户错误'+data)

# 获取tagid
    def getTagId(self):
        data = self.sess.get("https://api.bilibili.com/x/relation/tags").json()
        if data['code'] != 0 : self.log('****获取分组id错误'+data)
        for da in data['data']:
            if da['name'] == self.CONFIG['tag_name'] : 
                self.log('获得分组tag——id'+str(da['tagid']))
                return da['tagid']

# 获取粉丝列表
    def getFlowers(self,index):
        
        self.log('获取粉丝用户列表次数='+str(index))
        data = self.sess.get("https://api.bilibili.com/x/relation/followers?vmid="+str(self.mid)+"&pn="+str(index)).json()
        # 如果没有数据后返回
        if data['data']['list'] == [] : return
        self.getFlowers(index+1)
        # 添加粉丝id到列表中，添加还没回关的用户到回关列表中
        for i in data['data']['list'] :
            if i['uname'] == '账号已注销' :
                self.log('已注销用户,不添加到回关列表,id'+str(i['mid']))
                continue
            self.followers.append(i['mid'])
            if i['attribute'] != 6 : self.unfollowings.append(i['mid'])
        


# 操作方法
    def start(self):
        # 粉丝列表
        self.followers = []
        # 关注列表
        self.followings = []
        # 回关列表
        self.unfollowings = []
        # 取关列表
        nofollowers = []
        # 添加分组标签的用户列表
        addtagusers = []

        # 获取粉丝和关注列表数据
        tagid = self.getTagId()
        self.getFlowers(1)
        self.getUserBytag(tagid,1)

        # 对未关注的添加关注
        self.log('回关列表'+str(self.unfollowings))
        self.modify(array=self.unfollowings,type=1)
        # 复制/移动 用户到标签中
        addtagusers = [x for x in self.followers if x not in self.followings]
        self.log('复制/移动用户标签列表'+str(addtagusers))
        self.usersToTag(array=addtagusers,tagid=tagid)
        # 取关 未互相关注的用户
        if self.CONFIG['is_check'] == False : return
        nofollowers = [x for x in self.followings if x not in self.followers]
        self.log('取关id列表'+str(nofollowers))
        self.modify(array=nofollowers,type=2)




# 初始化方法
    def init(self):
        self.sess = requests.Session()
        json_path = os.path.join(BASEDIR, "config.json")
        with open(json_path,'r',encoding='utf-8') as jf:
            self.CONFIG = json.load(jf)
        self.sess.headers = self.CONFIG['headers']
        # 判断是否需要登录
        if (self.CONFIG['Cookies'] == '' or self.CONFIG['Cookies'] == {}) :
            self.login()
        else :
            self.log("从config设置Cookies")
            self.sess.cookies = requests.utils.cookiejar_from_dict(self.CONFIG['Cookies'])
        d = self.sess.get('https://api.bilibili.com/x/web-interface/nav').json()
        if not d['data']['isLogin'] : self.login()
        # 获取登录人的userid
        self.mid = d['data']['mid']
        self.log(self.CONFIG)


# 登陆方法
    def login(self):
        cook = {}
        a = self.sess.get('https://www.bilibili.com')
        for co in self.sess.cookies:
            cook[co.name] = co.value
        rep = self.sess.get('https://passport.bilibili.com/x/passport-login/web/qrcode/generate').json()
        qrcode = rep['data']['url']
        token = rep['data']['qrcode_key']
        pyqrcode.create(qrcode).png((BASEDIR + '/qrcode.png'),scale=12)
        os.startfile((BASEDIR + '/qrcode.png'))
        while True:
            rst = self.sess.get('https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key='+token)
            j=rst.json()
            if j['data']['code'] == 0:
                self.log('登录成功')
                
                for co in rst.cookies:
                    cook[co.name] = co.value
                self.CONFIG['Cookies'] = cook
                self.setconfig()
                os.remove(BASEDIR + '/qrcode.png')
                return
            time.sleep(3)



    def setconfig(self):
        with open(BASEDIR+'/config.json', 'w',encoding='utf-8') as f:
            json.dump(self.CONFIG, f)

    def log(self,text):
        print('[{0}]: {1}\n'.format(datetime.now().strftime('%m/%d %H:%M'),text))

        if(not self.CONFIG['is_log']):
            return 
        
        log_path = os.path.join(BASEDIR, "log.txt")
        with open(log_path,'a',encoding='utf-8') as f:
            f.write('[{0}]: {1}\n'.format(datetime.now().strftime('%m/%d %H:%M'),text))





























if __name__ == '__main__':
    obj = Relation()
    obj.main()

