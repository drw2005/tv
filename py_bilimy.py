# coding=utf-8
# !/usr/bin/python
import sys

sys.path.append('..')
from base.spider import Spider
import json
from requests import session, utils
import threading
import os
import time
import base64


class Spider(Spider):
    box_video_type = ''

    def getDependence(self):
        return ['py_bilibili']

    def getName(self):
        return "我的哔哩"

    def init(self, extend=""):
        self.bilibili = extend[0]
        print("============{0}============".format(extend))
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "动态": "动态",
            "关注": "关注",
            "收藏": "收藏",
            "历史记录": "历史记录",
            # ————————以下可自定义UP主，冒号后须填写UID————————
            #"虫哥说电影": "29296192",
            # ————————以下可自定义关键词，结果以搜索方式展示————————
            "周杰伦": "周杰伦",
            "狗狗": "汪星人",
            #"猫咪": "喵星人",
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        if (filter):
            filters = {}
            for lk in cateManual:
                if lk in self.bilibili.config['filter']:
                    filters.update({
                        cateManual[lk]: self.bilibili.config['filter'][lk]
                    })
                elif not cateManual[lk].isdigit():
                    link = cateManual[lk]
                    filters.update({
                        link: [{"key": "order", "name": "排序",
                                "value": [{"n": "综合排序", "v": "totalrank"}, {"n": "最新发布", "v": "pubdate"},
                                          {"n": "最多点击", "v": "click"}, {"n": "最多收藏", "v": "stow"},
                                          {"n": "最多弹幕", "v": "dm"}, ]},
                               {"key": "duration", "name": "时长",
                                "value": [{"n": "全部", "v": "0"}, {"n": "60分钟以上", "v": "4"},
                                          {"n": "30~60分钟", "v": "3"}, {"n": "5~30分钟", "v": "2"},
                                          {"n": "5分钟以下", "v": "1"}]}]
                    })
            result['filters'] = filters
        return result

    # 用户cookies，请在py_bilibili里填写，此处不用改
    cookies = 'buvid3=639BC80E-53EA-EAB4-88DD-AC777BF0EFF453435infoc; i-wanna-go-back=-1; buvid_fp_plain=undefined; DedeUserID=7827993; DedeUserID__ckMd5=3450c968d9d4d5b4; b_ut=5; CURRENT_BLACKGAP=0; nostalgia_conf=-1; theme_style=light; hit-dyn-v2=1; CURRENT_QUALITY=80; LIVE_BUVID=AUTO6016613313754464; b_nut=100; fingerprint3=d29bd155899849677c6cbe901195637e; fingerprint=38b752fc0e4062101aef78206f2e07a4; b_lsid=AB1C10AFC_1831BF7B09A; _uuid=A1014DFFC-DD58-19D8-D674-4E4736DBDB2C61007infoc; buvid_fp=38b752fc0e4062101aef78206f2e07a4; buvid4=290B9554-D72B-9FB7-63DA-FFD8AE52F7BB93514-022090815-QWaUPd4sJd4QUeu4q7utGg%3D%3D; CURRENT_FNVAL=4048; rpdid=|(JYl)mRRlm)0J'uYY)YlkJlk; innersign=0; hit-new-style-dyn=0; SESSDATA=974cdbbc%2C1685176208%2Ce363a%2Ab2; bili_jct=f1ecfe6ba2b9e1c089ad6217a6d5b0b7; sid=70q92dcr; bp_t_offset_7827993=733876247373807653; useragent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgNi4xOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTAzLjAuMC4wIFNhZmFyaS81MzcuMzY%3D;'

    def getCookie(self):
        self.cookies = self.bilibili.getCookie()
        return self.cookies

    def homeVideoContent(self):
        result = {}
        videos = self.bilibili.get_dynamic(1)['list'][0:5]
        result['list'] = videos
        return result

    def get_follow(self, pg, extend):
        tid = ''
        follow_config = self.bilibili.config["filter"].get('关注')
        # 默认显示关注列表第一个UP主投稿
        if follow_config:
            for i in follow_config:
                if i['key'] == 'tid':
                    if len(i['value']) > 0:
                        tid = i['value'][0]['v']
        if 'tid' in extend:
            tid = extend['tid']
        if tid:
            return self.get_up_videos(tid, pg)
        else:
            return {}

    def get_up_videos(self, tid, pg):
        result = {}
        url = 'https://api.bilibili.com/x/space/arc/search?mid={0}&pn={1}&ps=10'.format(tid, pg)
        rsp = self.fetch(url, headers=self.header, cookies=self.cookies)
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] == 0:
            videos = []
            vodList = jo['data']['list']['vlist']
            for vod in vodList:
                aid = str(vod['aid']).strip()
                title = vod['title'].strip().replace("<em class=\"keyword\">", "").replace("</em>", "")
                img = vod['pic'].strip()
                remark = "观看:" + self.bilibili.zh(vod['play']) + "　 " + str(vod['length']).strip()
                videos.append({
                    "vod_id": aid,
                    "vod_name": title,
                    "vod_pic": img + '@672w_378h_1c.jpg',
                    "vod_remarks": remark
                })
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 2
            result['total'] = 999999
        return result

    def categoryContent(self, tid, pg, filter, extend):
        self.box_video_type = "分区"
        if tid.isdigit():
            return self.get_up_videos(tid, pg)
        elif tid == "关注":
            return self.get_follow(pg, extend)
        else:
            result = self.bilibili.categoryContent(tid, pg, filter, extend)
            return result

    def cleanSpace(self, str):
        return str.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')

    lock = threading.Lock()

    def get_vod(self, vod, part, eid):
        url3 = "https://api.bilibili.com/x/web-interface/view?aid=%s" % str(eid)
        rsp3 = self.fetch(url3, headers=self.header, cookies=self.cookies)
        jRoot3 = json.loads(rsp3.text)
        pages = jRoot3['data']['pages']
        if len(pages) > 1:
            playUrl=''
            for p in pages:
                cid = p['cid']
                p_part = str(p['part']).strip()
                if p_part != part:
                    p_part = part + p_part
                playUrl += '{0}${1}_{2}#'.format(p_part, eid, cid)
            with self.lock:
                vod['vod_play_url'] += playUrl
        else:
            cid = jRoot3['data']['cid']
            with self.lock:
                vod['vod_play_url'] += '{0}${1}_{2}#'.format(part, eid, cid)
    
    def detailContent(self, array):
        if self.box_video_type == "搜索":
            mid = array[0]
            ps = 30
            # 获取UP主视频列表，ps后面为视频数量，不要太大以免IP被封
            url = 'https://api.bilibili.com/x/space/arc/search?mid={0}&ps={1}'.format(mid, ps)
            rsp = self.fetch(url, headers=self.header, cookies=self.cookies)
            content = rsp.text
            jRoot = json.loads(content)
            jo = jRoot['data']['list']['vlist']

            url2 = "https://api.bilibili.com/x/web-interface/card?mid={0}".format(mid)
            rsp2 = self.fetch(url2, headers=self.header, cookies=self.cookies)
            jRoot2 = json.loads(rsp2.text)
            jo2 = jRoot2['data']['card']
            name = jo2['name'].replace("<em class=\"keyword\">", "").replace("</em>", "")
            pic = jo2['face']
            desc = jo2['Official']['desc'] + "　" + jo2['Official']['title']
            vod = {
                "vod_id": mid,
                "vod_name": name + " " + "个人主页",
                "vod_pic": pic,
                "type_name": "最近投稿",
                "vod_year": "",
                "vod_area": "bilidanmu",
                "vod_remarks": "",  # 不会显示
                'vod_tags': 'mv',  # 不会显示
                "vod_actor": "粉丝数：" + self.bilibili.zh(jo2['fans']),
                "vod_director": name,
                "vod_content": desc,
                'vod_play_from': 'B站',
                'vod_play_url': ''
            }
            for tmpJo in jo:
                eid = tmpJo['aid']
                part = tmpJo['title'].replace("#", "-")
                t = threading.Thread(target=self.get_vod, args=(vod, part, eid, ))
                t.start()

            while True:
                _count = threading.active_count()
                #计算线程数，不出结果就调大，结果少了就调小
                if _count <= 2:
                    break
            
            result = {
                'list': [
                    vod
                ]
            }
            return result
        else:
            return self.bilibili.detailContent(array)

    def searchContent(self, key, quick):
        self.box_video_type = "搜索"
        if len(self.cookies) <= 0:
            self.getCookie()
        url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=bili_user&keyword={0}'.format(key)
        rsp = self.fetch(url, headers=self.header, cookies=self.cookies)
        content = rsp.text
        jo = json.loads(content)
        videos = []
        vodList = jo['data']['result']
        for vod in vodList:
            aid = str(vod['mid']) # str(vod["res"][0]["aid"])
            title = "UP主：" + vod['uname'].strip() + "  ☜" + key
            img = 'https:' + vod['upic'].strip()
            remark = "粉丝数" + self.bilibili.zh(vod['fans'])
            videos.append({
                "vod_id": aid,
                "vod_name": title,
                "vod_pic": img + '@672w_378h_1c.jpg',
                "vod_remarks": remark
            })
        result = {
            'list': videos
        }
        return result

    def playerContent(self, flag, id, vipFlags):
        return self.bilibili.playerContent(flag, id, vipFlags)

    config = {
        "player": {},
        "filter": {
        }
    }

    header = {
        "Referer": "https://www.bilibili.com",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }

    def localProxy(self, param):
        return [200, "video/MP2T", action, ""]