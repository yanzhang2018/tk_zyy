# -*- coding: gbk -*-
import tkinter as tk
import psutil
import base64
import requests
import yaml
import urllib3 
import io
from PIL import Image,ImageTk


# 忽略ssl警告
urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)

# 检测进程，获取端口和token
cmds = list[str]
for process in psutil.process_iter():
    if process.name().removesuffix(".exe") == "LeagueClientUx":
        cmds = process.cmdline()
        break
for cmd in cmds:
    ary = cmd.split("=")
    if ary[0] == "--remoting-auth-token":
        token = ary[1]

    if ary[0] == "--app-port":
        port = ary[1]

tokens = base64.b64encode(("riot:%s" % token).encode())
author = { "Authorization":"Basic %s" % tokens.decode()}

# 查询当前召唤师
result = requests.get(
        url = "https://127.0.0.1:" + port + "/lol-summoner/v1/current-summoner",
        headers = author,
        verify = False
)
if result.status_code == 200:
    result.encoding = "utf-8"
    userinfo = yaml.load(result.text, Loader=yaml.FullLoader)
    result.close()
   
userimg='https://wegame.gtimg.com/g.26-r.c2d3c/helper/lol/assis/images/resources/usericon/%s.png'%(userinfo['profileIconId'])


result = requests.get(
        url = "https://127.0.0.1:" + port + "/lol-ranked/v1/ranked-stats/%s" %(userinfo['puuid']),
        headers = author,
        verify = False
)
if result.status_code == 200:
    result.encoding = "utf-8"
    rank_info= yaml.load(result.text, Loader=yaml.FullLoader)
    result.close()

result = requests.get(
        url = "https://127.0.0.1:" + port + "/lol-match-history/v1/products/lol/%s/matches" %userinfo['puuid'],
        headers = author,
        verify = False
)
if result.status_code == 200:
    result.encoding = "utf-8"
    match_history = yaml.load(result.text, Loader=yaml.FullLoader)
    # print( match_history )
    result.close()







# 布置主窗口
root_window =tk.Tk()
root_window.title('zyy助手')
root_window.geometry('400x200')
root_window.resizable(0,0)


# 显示召唤师头像
image_bytes = requests.get(userimg).content
data_stream = io.BytesIO(image_bytes)
pil_image = Image.open(data_stream)
tk_image = ImageTk.PhotoImage(pil_image)
lab1 =tk.Label(root_window,image=tk_image)
lab1.pack()

#  显示召唤师名字
lab2 =tk.Label(root_window,text=userinfo["displayName"])
lab2.pack()

#  显示召唤师单双段位
lab3 =tk.Label(root_window,text=rank_info["queueMap"]['RANKED_SOLO_5x5']['tier'])
lab3.pack()

# 显示搜索栏
name_entry = tk.Entry(root_window,)
name_entry.pack()



# 搜索按钮绑定函数
def search():
    name = name_entry.get()
    # print(name)
    result=requests.get(
    url = "https://127.0.0.1:" + port + "/lol-summoner/v1/summoners/",
    headers = author,
    params={'name':name},
    verify = False,
    )
    s_info = yaml.load(result.text, Loader=yaml.FullLoader)
    search_id=(s_info['summonerId'])
    result.close()


    result=requests.get(
    url = "https://127.0.0.1:" + port + "/lol-match-history/v3/matchlist/account/%d"%search_id,  
    headers = author,
    params={'begIndex':0,'endIndex':8,},
    verify = False,
    )
    his_info = yaml.load(result.text, Loader=yaml.FullLoader)
    # print(his_info["games"]["games"])
    # print(len(his_info["games"]["games"]))
    result.close()


    newWindow = tk.Toplevel(root_window)
    newWindow.title('(%s)的战绩'%name)
    newWindow.geometry('400x200')
    newWindow.resizable(0,0)




    for i in his_info['games']['games']:
        start_time = i["gameCreationDate"][0:10]
        champ_id =i["participants"][0]["championId"]
        # print(champ_id)


        result=requests.get(
            url = "https://127.0.0.1:" + port + "/lol-champ-select/v1/grid-champions/"
                  + str(i['participants'][0]['championId']),
            headers = author,
            verify = False,
        )
        champion="["+result.json()['name']+"]"
        result.close()
        gamemode=i["gameMode"]
        kill=i["participants"][0]["stats"]["kills"]
        deaths=i["participants"][0]["stats"]["deaths"]
        assists=i["participants"][0]["stats"]["assists"]
        w_d=i["participants"][0]["stats"]['win']
        if w_d:
            wd="胜"
        else:
            wd="败"

        output=start_time+'\t'+ wd +'\t' +str(kill)+'/'+str(deaths)+'/'+str(assists)+'\t' + gamemode +"\t " +champion
        out_lab=tk.Label(newWindow,text=output,anchor="nw")
        out_lab.pack()






# 显示搜索按钮
search_button=tk.Button(root_window,text='查询',command=search)
search_button.pack()





#启动窗口
root_window.mainloop()

