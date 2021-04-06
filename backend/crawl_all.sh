#列表页
rm -rf ../list
mkdir ../list
cd ../list
#batch数
for i in {0..99}
do
  date +'%Y-%m-%d %H:%M:%S'
  echo start batch $i
  #并发数
  for j in {0..19}
  do
    k=$((i*20+j))
    echo https://ecchi.iwara.tv/videos?page=$k
    curl -s -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36' -O https://ecchi.iwara.tv/videos?page=$k &
  done
  wait
  echo finish batch $i
done


#提取链接
rm -rf ../content
mkdir ../content
cd ../content
grep -oE '<h3 class="title"><a href="(.*)"'  ../list/* | awk -F\" '{print $4}' > seed_all.txt
lines=$(wc -l seed_all.txt | awk '{print $1}')

#详情页
for i in {0..7200}
do
  date +'%Y-%m-%d %H:%M:%S'
  echo start batch $i
  for j in {0..9}
  do
    k=$((i*10+j))
    url=https://ecchi.iwara.tv$(sed -n "${k},${k}p" seed_all.txt)
    echo $url
    curl -s -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36' -O $url &
  done
  wait
  sleep 3
  echo finish batch $i
done

cd ../backend
python3 parse.py
