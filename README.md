# ufwlog-portIPsift  
Filter out all IP addresses and real addresses for the custom port from the UFW log  
从ufwlog中筛选出自定义port的所有访问IP和真实地址  
# 使用说明  
1.从https://cdn.jsdelivr.net/npm/geolite2-city@1.0.10/GeoLite2-City.mmdb.gz 下载GeoLite2-City数据库并解压放置于同级目录  
2.将你的ufw.log文件放在同级目录  
3.使用pip工具安装geoip2,ipdb,xpinyin  
```bash
pip install geoip2
```
```bash
pip install ipdb
```
```bash
pip install xpinyin
```

4.启动"ipsearch.py"  
