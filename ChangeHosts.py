import requests
import bs4
import time

#hosts路径（根据实际情况修改）
hostsfile="C:\\Windows\\System32\\drivers\\etc\\hosts"

#爬虫开始
try :
    url='https://github.com/521xueweihan/GitHub520'
    r = requests.get(url,timeout=12)
    r.encoding = 'utf-8'
    t = r.text
    soup = bs4.BeautifulSoup(t,'html.parser')
except :
    print('爬虫失败')
#爬虫结束
#取得hosts
nh = []
for i in soup.find_all('pre'):
    nh.append(i.text)
#nh转换为列表形式
nh=nh[0]
hosts=[]
#读到原hosts内容
with open(hostsfile,'r') as fd:
    hosts=fd.readlines()

#删除hosts中第23行到41行（具体要修改多长，需要自己在hosts文件里面看长度，这里我的是23到40行）
for i in range(23,41)[::-1]:
    del hosts[i]

#在被删除原github hosts的区域增加新的github hosts
hosts.append(nh)
#把列表内容全部连接起来
hosts=''.join(hosts)
#复写入文件
with open('C:/Windows/System32/drivers/etc/hosts','w') as fd:
    fd.write(hosts)

print('修改成功,3秒后自动关闭')
time.sleep(3)
