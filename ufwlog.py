import re
import geoip2.database
import os
import time
import ipdb
from xpinyin import Pinyin
from collections import defaultdict
# 提取日志中的唯一 IPv4 和 IPv6 地址
def extract_ips_from_port(log_file_path, port):
    ipv4_set = set()  # 用于存储唯一的IPv4地址
    ipv6_set = set()  # 用于存储唯一的IPv6地址
    
    # 正则表达式,用于匹配IPv4和IPv6地址以及端口号
    ipv4_pattern = re.compile(r"SRC=((?:\d{1,3}\.){3}\d{1,3}).*DPT=(\d+)")
    ipv6_pattern = re.compile(r"SRC=([0-9a-fA-F:]+).*DPT=(\d+)")

    with open(log_file_path, 'r') as file:
        for line in file:
            # 检查IPv4地址
            ipv4_match = ipv4_pattern.search(line)
            if ipv4_match:
                src_ip, dpt_port = ipv4_match.groups()
                if int(dpt_port) == port and is_valid_ipv4(src_ip):
                    ipv4_set.add(src_ip)
            
            # 检查IPv6地址
            ipv6_match = ipv6_pattern.search(line)
            if ipv6_match:
                src_ip, dpt_port = ipv6_match.groups()
                if int(dpt_port) == port and is_valid_ipv6(src_ip):
                    ipv6_set.add(src_ip)

    return list(ipv4_set), list(ipv6_set)

# 检查 IPv4 地址的有效性
def is_valid_ipv4(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not (0 <= int(part) <= 255):
            return False
    return True

# 检查 IPv6 地址的有效性
def is_valid_ipv6(ip):
    if ":" in ip:
        try:
            return ip.count("::") <= 1 and all(0 <= int(block, 16) <= 0xFFFF for block in ip.split(":") if block)
        except ValueError:
            return False
    return False

# 使用 geoip2 查询 IP 地址的地理位置,只返回国家和城市
def get_location(ip_address):
    try:
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')  # 请确保路径正确
        response = reader.city(ip_address)
        if response.country.name=="China" :
            if is_valid_ipv4(ip_address)==True:
                db = ipdb.District("ipipfree.ipdb")  # 修改为正确的路径
                p=Pinyin()
                country = "China"  # 国家
                result = db.find(ip_address, "CN")
                temp=p.get_pinyin(str(result[1]))
                s = temp.split('-')
                city_name = ''
                for i in range(0,len(s)):
                    city_name = city_name+s[i].capitalize()
                city = city_name if len(result) > 1 else 'Unknown'  # 城市
                return {'country': country, 'city': city}
            else:
                country = response.country.name or 'Unknown'
                city = response.city.name or 'Unknown'
                return {'country': country, 'city': city}
        if response.country.name=="Hong Kong" or response.country.name=="Taiwan" or response.country.name=="Macao":
            country = "China"
            city = response.city.name or 'Unknown'
            return {'country': country, 'city': city}
        else:
            country = response.country.name or 'Unknown'
            city = response.city.name or 'Unknown'
            return {'country': country, 'city': city}
    except Exception as e:
        return {'country': 'Unknown', 'city': 'Unknown'}
# 输出格式化函数,确保对齐
def print_ip_location(ip, location, ip_column_width, country_column_width, city_column_width):
    print(
        f"* {ip.ljust(ip_column_width)}"
        f"{location['country'].ljust(country_column_width)}"
        f"{location['city'].ljust(city_column_width)}"
    )

# 计算列宽度
def calculate_column_widths(ip_list):
    max_ip_length = max(len(ip) for ip in ip_list) if ip_list else 15
    ip_column_width = max(max_ip_length + 5, 20)  # IP 列最小宽度为 20,动态调整
    country_column_width = 25  # 国家列宽度固定为 15
    city_column_width = 20     # 城市列宽度固定为 20
    return ip_column_width, country_column_width, city_column_width

# 主程序,结合 IP 提取和位置查询
def query_ips(log_file_path):
    while True:
        try:
            port_to_check = int(input("请输入要查询的端口号(或输入0退出):"))
            if port_to_check == 0:
                print("* 程序已退出")
                break

            # 获取日志文件的大小
            file_size = os.path.getsize(log_file_path) / 1000
            estimated_time = round(file_size / 131500, 1)

            # 输出提示信息
            print(f"* 请等待读取...")
            print(f"* 此日志的大小为: {file_size / 1024:.2f} MB")
            print(f"* 可能需要用时: {estimated_time} 秒")

            # 记录处理开始时间
            start_time = time.time()

            unique_ipv4, unique_ipv6 = extract_ips_from_port(log_file_path, port_to_check)

            # 计算列宽
            all_ips = unique_ipv4 + unique_ipv6
            ip_column_width, country_column_width, city_column_width = calculate_column_widths(all_ips)

# 统计国家访问次数的字典
            ipv4_country_stats = defaultdict(int)
            ipv6_country_stats = defaultdict(int)

            # 输出 IPv4 结果
            if unique_ipv4:
                print(f"与端口 {port_to_check} 相关的唯一IPv4地址及位置信息如下(共 {len(unique_ipv4)} 个IP):")
                print(f"{'IP地址'.ljust(ip_column_width)}{'国家'.ljust(country_column_width-2)}{'城市'.ljust(city_column_width)}")
                print("*" * (ip_column_width + country_column_width + city_column_width))
                for ip in unique_ipv4:
                    location = get_location(ip)  # 获取 IP 地址的地理位置
                    ipv4_country_stats[location['country']] += 1  # 统计国家出现次数
                    print_ip_location(ip, location, ip_column_width, country_column_width, city_column_width)
                print(f"查询完成,共有{len(unique_ipv4)}个V4IP访问此端口")
                print("*" * (ip_column_width + country_column_width + city_column_width))
                sorted_ipv4_stats = sorted(ipv4_country_stats.items(), key=lambda x: x[1], reverse=True)
                print("IPV4国家访问次数统计:")
                for country, count in sorted_ipv4_stats:
                    print(f"* {country}: {count} 次")
            else:
                print(f"没有找到与端口 {port_to_check} 相关的IPv4日志")

            # 输出 IPv6 结果
            if unique_ipv6:
                print(f"\n与端口 {port_to_check} 相关的唯一IPv6地址及位置信息如下(共 {len(unique_ipv6)} 个IP):")
                print(f"{'IP地址'.ljust(ip_column_width)}{'国家'.ljust(country_column_width-2)}{'城市'.ljust(city_column_width)}")
                print("*" * (ip_column_width + country_column_width + city_column_width))
                for ip in unique_ipv6:
                    location = get_location(ip)  # 获取 IP 地址的地理位置
                    ipv6_country_stats[location['country']] += 1  # 统计国家出现次数
                    print_ip_location(ip, location, ip_column_width, country_column_width, city_column_width)
                print(f"查询完成,共有{len(unique_ipv6)}个V6IP访问此端口")
                print("*" * (ip_column_width + country_column_width + city_column_width))

                # 排序并输出IPv6国家访问次数统计
                sorted_ipv6_stats = sorted(ipv6_country_stats.items(), key=lambda x: x[1], reverse=True)
                print("IPV6国家访问次数统计:")
                for country, count in sorted_ipv6_stats:
                    print(f"* {country}: {count} 次")
            else:
                print(f"\n没有找到与端口 {port_to_check} 相关的IPv6日志")

            # 记录处理结束时间
            end_time = time.time()
            total_time = round(end_time - start_time, 1)
            print(f"\n* 查询完成,实际用时 {total_time} 秒")

        except ValueError:
            print("* 输入无效,请输入一个有效的端口号")

# 执行查询
log_file_path = 'ufw.log'  # UFW日志文件的路径
query_ips(log_file_path)
