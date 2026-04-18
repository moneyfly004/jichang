import requests
import re
import csv
import os
import time
from urllib.parse import urlparse

# 定义抓取配置和路径
CSV_PATH = os.environ.get("CSV_PATH", "/Users/apple/Downloads/shell/airports.csv")

# ================= 抓取来源配置 =================
# Telegram 免签网页版列表 (找一些专门分享机场的开放频道)
TG_CHANNELS = [
    "sharejichang",
    "jichang_share",
    "v2rayshare",
    "clash_share",
    "mianfeijichang",
    "sspjcv2b"
]

# GitHub 上经常汇总机场的开源 README.md 或接口
GITHUB_RAW_URLS = [
    # 可以放置长期维护机场清单的 raw 地址
    "https://raw.githubusercontent.com/abshare/abshare/main/README.md",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt"
]

# 屏蔽列表：抓取时自动忽略这些常见和非机场域名
BLACKLIST_DOMAINS = [
    "t.me", "telegram.org", "github.com", "githubusercontent.com",
    "youtube.com", "twitter.com", "google.com", "x.com", "apple.com",
    "passwordmonster.com", "v2board.com", "cloudflare.com", "gmail.com",
    "qq.com"
]

def load_existing_db():
    sites = {}
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get("url", "").strip()
                    if url.startswith("http"):
                        # 以 domain 为 key 去重
                        netloc = urlparse(url).netloc
                        sites[netloc] = row
        except Exception as e:
            print(f"[-] 读取主干库异常: {e}")
    return sites

def save_db(sites_dict):
    sites_list = list(sites_dict.values())
    if not sites_list:
        return
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url", "panel_type", "fail_count", "last_status"])
        writer.writeheader()
        for s in sites_list:
            writer.writerow(s)

def extract_valid_urls(text):
    """通过正则提取并清洗 URL"""
    extracted = set()
    # 提取所有包含 http 的字符串块，忽略前后标签
    urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s<"\'\)]*)?', text)
    for u in urls:
        u = u.strip()
        netloc = urlparse(u).netloc
        if not netloc:
            continue
        
        # 排除黑名单
        is_blocked = any(bd in netloc for bd in BLACKLIST_DOMAINS)
        if is_blocked:
            continue
            
        # 排除仅仅提取出来的纯顶级后缀或者异常字符串
        if len(netloc.split('.')) < 2:
            continue
            
        # 如果携带了明显的特型后缀则过滤，比如 .jpg .js
        if u.lower().endswith(('.jpg', '.png', '.css', '.js', '.md', '.html', '.zip')):
            continue
            
        # 提取根 URL （大部分机场直接主页就能注册）
        base_url = f"{urlparse(u).scheme}://{netloc}"
        extracted.add(base_url)
    return extracted

def scrape_telegram(channel):
    url = f"https://t.me/s/{channel}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    print(f"[*] 侦听 Telegram 频道: {channel}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            urls = extract_valid_urls(r.text)
            print(f"  -> {channel} 提取到有效外链: {len(urls)} 个。")
            return urls
    except Exception as e:
        print(f"[!] {channel} 探测失败: {str(e)[:50]}")
    return set()

def scrape_github(raw_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    print(f"[*] 侦听 Github 资源库: {raw_url.split('/')[-1]}...")
    try:
        r = requests.get(raw_url, headers=headers, timeout=10)
        if r.status_code == 200:
            urls = extract_valid_urls(r.text)
            print(f"  -> Github端 提取到有效外链: {len(urls)} 个。")
            return urls
    except Exception as e:
        print(f"[!] Github探测失败: {str(e)[:50]}")
    return set()

def main():
    print("========================================")
    print("  Spider: 自我进化搜索引擎启动")
    print("========================================")
    
    existing_sites = load_existing_db()
    original_count = len(existing_sites)
    print(f"[*] 目前掌握机场底库: {original_count} 个")
    
    all_new_urls = set()
    
    # 爬取 Telegram
    for ch in TG_CHANNELS:
        all_new_urls.update(scrape_telegram(ch))
        time.sleep(1)
        
    # 爬取 Github
    for gh in GITHUB_RAW_URLS:
        all_new_urls.update(scrape_github(gh))
        time.sleep(1)
        
    print(f"\n[*] 汇总抓取到疑似新机场域名: {len(all_new_urls)} 个")
    
    # 查重与合并入库
    new_added = 0
    for u in all_new_urls:
        netloc = urlparse(u).netloc
        if netloc not in existing_sites:
            # 加入进字典中
            existing_sites[netloc] = {
                "name": f"New_{netloc.split('.')[0]}",
                "url": u,
                "panel_type": "",
                "fail_count": 0,
                "last_status": "未测"
            }
            new_added += 1
            
    print(f"[*] 去重后成功新增: {new_added} 个新鲜机场进入血库。")
    if new_added > 0:
        save_db(existing_sites)
        print(f"[*] CSV 数据库已保存更新，当前规模池: {len(existing_sites)}。")
    print("========================================")
    print("进化爬虫探测完毕，即将交由主程序执行跑库。")

if __name__ == "__main__":
    main()
