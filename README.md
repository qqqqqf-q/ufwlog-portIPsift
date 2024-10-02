# ufwlog-portIPsift  
Filter out all IP addresses and real addresses for the custom port from the UFW log  
从ufwlog中筛选出自定义port的所有访问IP和真实地址  
# 使用说明  
1.从右侧的release中下载最新的zip压缩包并解压  
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
