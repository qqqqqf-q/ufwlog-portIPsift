# ufwlog-portIPsift

**Filter out all IP addresses and real addresses for the custom port from the UFW log**

从 UFW 日志中筛选出自定义端口的所有 IP 和真实地址。

## 使用方法

1. 从 [GeoLite2-City 数据库](https://cdn.jsdelivr.net/npm/geolite2-city@1.0.10/GeoLite2-City.mmdb.gz) 下载并解压到同级目录。
2. 将你的 `ufw.log` 文件放在同级目录。
3. 使用 `pip` 工具安装所需库：
   ```bash
   pip install geoip2
   pip install ipdb
   pip install xpinyin
