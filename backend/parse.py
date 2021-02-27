import os
import elasticsearch
import json
import time
import logging
import sys
import pyquery as pq

_Program = os.path.basename(sys.argv[0])
_Logger = logging.getLogger(_Program)
logging.basicConfig(format='HTMLParser %(levelname)s %(asctime)s %(message)s')
logging.root.setLevel(level=logging.INFO)

ES_HOSTS = ['localhost:9200']

files = os.listdir('../content')
f = open('content.ndjson','w',encoding='utf-8')
for file in files:
    if file.find('.')==-1:
        _Logger.info('https:/ecchi.iwara.tv/videos/'+file)
        try:
            html = open('../content/'+file,'r',encoding='utf-8').read()
            root = pq.PyQuery(html)
            item = {}
            item['title'] = root.find('h1.title').eq(0).text()
            item["user_name"] =  root.find("div.node-info a.username").eq(0).text().strip()
            item["user_page"] = "https://ecchi.iwara.tv"+root.find("div.node-info a.username").eq(0).attr("href").strip()
            item["user_avatar"] = "https:"+root.find("div.node-info div.user-picture img").eq(0).attr("src").strip().replace('avatar_small','avatar_large')
            item["time"] = root.find("div.node-info .submitted").eq(0).text().strip().split("作成日:")[-1].strip()
            item["description"] = root.find(".field-type-text-with-summary").eq(0).text().strip() if len(root.find(".field-type-text-with-summary"))!=0 else ""
            item["tags"] = root.find(".field-name-field-categories").eq(0).text().strip().split('\n')
            item["like"],item["view"] = root.find(".node-views").eq(0).text().strip().split(' ')
            item['like'] = item['like'].strip().replace(',','')
            item['view'] = item['view'].strip().replace(',','')
            item["comment"] = root.find("#comments > .title:not(.comment-form)").eq(0).text().strip().split(' ')[-1].strip() if len(root.find("#comments > .title:not(.comment-form)"))!=0 else "0"
            item['url'] = root.find('head > link[rel=canonical]').eq(0).attr('href').split('?')[0]
            try:
                item['thumbnail'] = 'https:'+root.find('#video-player').eq(0).attr('poster').strip()
            except:
                try:
                    item['thumbnail'] = 'https://i.iwara.tv/sites/default/files/styles/thumbnail/public/video_embed_field_thumbnails/youtube/'+root.find('link[rel=canonical]').eq(-1).attr('href').strip().split('=')[-1]
                    _Logger.info('youtube '+item['thumbnail'])
                except:
                    _Logger.info('no video')
            item['id'] = item['url'].split('/')[-1]
            f.write(json.dumps(item,ensure_ascii=False)+'\n')
            f.flush()
        except:
            _Logger.error('failed,need check')
f.close()


es=  elasticsearch.Elasticsearch(hosts = ES_HOSTS, timeout=60, max_retries=10, retry_on_timeout=True)
count = 0
bulk = ''
for line in open('content.ndjson','r',encoding='utf-8'):
    data = json.loads(line.strip())
    data['@timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
    #data['time'] =data['time'].replace(' ','T')+':00+08:00'
    bulk+=json.dumps({ "update" : { "_index" : "iwara", "_id" : data["id"] } })+'\n'
    del data["id"]
    bulk+=json.dumps({'doc':data,'doc_as_upsert':True},ensure_ascii=False)+'\n'
    count+=1
    if count>=100:
        print(es.bulk(bulk))
        count = 0
        bulk = ''
print(es.bulk(bulk))