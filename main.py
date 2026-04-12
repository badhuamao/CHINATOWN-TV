import requests
import re
import os
import base64

# --- 配置区 ---
SEARCH_QUERY = 'gotochinatown.net'
TOKEN = os.getenv("MY_GITHUB_TOKEN")

def search_github():
    if not TOKEN: return []
    # 扩大搜索范围，不带协议前缀，只搜域名
    search_url = f"https://api.github.com/search/code?q={SEARCH_QUERY}&sort=indexed"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    found_urls = []
    try:
        r = requests.get(search_url, headers=headers, timeout=10)
        if r.status_code == 200:
            for item in r.json().get('items', []):
                raw_url = item['html_url'].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                found_urls.append(raw_url)
    except: pass
    return found_urls

def harvest():
    raw_results = []
    seen_lines = set()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    all_sources = search_github()
    print(f"📡 正在深度扫荡 {len(all_sources)} 个源文件...")

    for url in all_sources:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200: continue
            
            # Base64 自动穿透逻辑（处理订阅链接）
            content = resp.text.strip()
            if len(content) > 30 and ' ' not in content and '\n' not in content:
                try:
                    content = base64.b64decode(content + '=' * (-len(content) % 4)).decode('utf-8', errors='ignore')
                except: pass

            # 【核心策略：整行收割】
            lines = content.split('\n')
            for line in lines:
                if "gotochinatown.net" in line:
                    clean_line = line.strip()
                    if clean_line and clean_line not in seen_lines:
                        # 记录每一行，不管它是什么协议
                        raw_results.append(clean_line)
                        seen_lines.add(clean_line)
        except: continue
    return raw_results

if __name__ == "__main__":
    nodes = harvest()
    # 结果存入 raw_harvest.txt，这就是咱们的“原始矿堆”
    with open("raw_harvest.txt", "w", encoding="utf-8") as f:
        for n in nodes:
            f.write(n + "\n")
            
    print(f"✅ 深度收割完成！共抓获 {len(nodes)} 条原始数据。")
