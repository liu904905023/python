import os
import multiprocessing
from time import ctime, sleep
import urllib.request
import urllib.error

import requests

import MongodbClient
from MongodbClient import MongodbClient
from bs4 import BeautifulSoup
from MongodbClient import MongodbClient
import threading


class testClass(object):
    def __init__(self):
        self.proxies = {'http': "http://127.0.0.1:1080", "https": "https://127.0.0.1:1080"}

    def download(self, url_p_v):
        try:
            bbb = requests.get(url_p_v, proxies=self.proxies)
        except:
            print("这个有问题{}".format(url_p_v))
        soup = BeautifulSoup(bbb.content.decode("utf-8"), "lxml")
        video = soup.find_all('source')
        pics = soup.find_all('meta', attrs={"property": "og:image"})
        dir = 'F:\\Data\\tumblr\\'
        if len(video) > 0:
            medium_url = (video[0]['src'])
            print("开始下载视频{}".format(medium_url))

            medium_name = medium_url.split("/")[-1].split("?")[0]
            medium_name = "_".join([medium_url.split("/")[-2],
                                    medium_name])
            file_path = os.path.join(dir, medium_name)
            if os.path.exists(file_path):
                print('{}此文件已存在'.format(medium_name))
            else:
                retry_times = 0
                while retry_times < 5:
                    try:
                        resp = requests.get(medium_url,
                                            stream=True,
                                            proxies=self.proxies,
                                            timeout=10)
                        if resp.status_code == 403:
                            pass
                        with open(file_path, 'wb') as fh:
                            for chunk in resp.iter_content(chunk_size=1024):
                                fh.write(chunk)
                        break
                    except:
                        pass
                    retry_times += 1
                else:
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
                    print("从%s下载%s失败\n" % (medium_url, medium_name))
        else:
            print("开始下载图片")

            for pic in pics:
                print("开始下载图片{}".format(pic['content']))
                filename = os.path.basename(pic['content'])
                suffix = os.path.splitext(pic['content'])
                if suffix[1] == "":
                    filename += ".jpg"
                picfile = '{}/{}'.format(dir, filename)
                if os.path.exists(picfile):
                    print('{}此文件已存在'.format(picfile))
                else:
                    retry_times = 0
                    while retry_times < 5:
                        try:
                            resp = requests.get(pic['content'],

                                                proxies=self.proxies,
                                                timeout=10)

                            with open(file=picfile, mode='wb') as f:
                                f.write(resp.content)
                                f.close()
                        except:
                            pass
                            retry_times += 1

                    else:
                        try:
                            os.remove(picfile)
                        except OSError:
                            pass
                        print("从%s下载%s失败\n" % (pic['content'], filename))

    def worker(self, offsize):
        datas = []
        db = MongodbClient()
        db.changeTable('trueUrl')
        for i in range(offsize + 1, offsize + 21):
            # for i in range(4,5):
            url = "https://904905023.tumblr.com/likes/page/{}".format(i)
            print("开始获取{}".format(url))
            proxy_handler = urllib.request.ProxyHandler(self.proxies)
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req)
            content = (res.read().decode('utf-8'))
            soup = BeautifulSoup(content, 'lxml')
            data = soup.find_all(class_="post-blog")
            if len(data) > 0:
                for i in data:
                    datas.append(i['href'])
                    # db.put(i['src'])
            # print(datas)
            for url_p_v in range(len(datas)):
                thread = threading.Thread(target=self.download, args=(datas[url_p_v],))
                # thread.setDaemon(True) ##设置守护线程
                thread.start()  ##启动线程


if __name__ == "__main__":
    group = [x * 20 for x in range(0, 4)]
    for i in (group):
        a = testClass()
        p = multiprocessing.Process(target=a.worker, args=(i,))
        p.start()

        # print("The number of CPU is:" + str(multiprocessing.cpu_count()))
        # for p in multiprocessing.active_children():
        #     print("child   p.name:" + p.name + "\tp.id" + str(p.pid))
        # print("END!!!!!!!!!!!!!!!!!")
