import requests
import re
import os
import base64

# --- 配置区 ---
SEARCH_QUERY = 'gotochinatown.net'
TOKEN = os.getenv("MY_GITHUB_TOKEN")

def search_github():
    if not TOKEN: return []
    # 增加搜索深度，不带协议关键词
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
    raw_data_lines = []
    seen_hashes = set()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    all_sources = list(set(search_github()))
    print(f"📡 正在深度扫描 {len(all_sources)} 个来源...")

    for url in all_sources:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200: continue
            
            # 原始内容（包含 Base64 解码尝试）
            content = resp.text
            if len(content.strip()) > 30 and ' ' not in content.strip() and '\n' not in content.strip():
                try:
                    content = base64.b64decode(content.strip() + '=' * (-len(content.strip()) % 4)).decode('utf-8')
                except: pass

            # 【核心策略改动】：
            # 1. 抓取包含域名的整行
            # 2. 如果是 JSON/YAML，尝试抓取它所在的整个大括号或缩进块
            
            # 先按行切分，抓取所有包含目标的行
            lines = content.split('\n')
            for line in lines:
                if "gotochinatown.net" in line:
                    clean_line = line.strip()
                    if clean_line not in seen_hashes:
                        raw_data_lines.append(f"--- 来源: {url[:50]}... ---")
                        raw_data_lines.append(clean_line)
                        raw_data_lines.append("") # 留个空行方便阅读
                        seen_hashes.add(clean_line)
        except: continue
    return raw_data_lines

if __name__ == "__main__":
    results = harvest()
    
    # 纯原始输出，不做任何加工
    with open("all_nodes_raw.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
            
    print(f"✅ 深度打捞完成！共保存 {len(results)//3} 组原始数据到 all_nodes_raw.txt")
