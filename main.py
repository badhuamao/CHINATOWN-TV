import requests
import re
import os
import base64

# --- 配置区 ---
SEARCH_QUERY = 'gotochinatown.net'
TOKEN = os.getenv("MY_GITHUB_TOKEN")

def search_github():
    if not TOKEN: return []
    # 扩大搜索范围
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
    raw_data = []
    seen_hashes = set()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    all_sources = list(set(search_github()))
    print(f"📡 开始深度打捞，来源总数: {len(all_sources)}")

    for url in all_sources:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200: continue
            
            content = resp.text
            # 尝试处理 Base64 编码（很多 VMess 订阅是全编码的）
            if len(content.strip()) > 30 and ' ' not in content.strip() and '\n' not in content.strip():
                try:
                    content = base64.b64decode(content.strip() + '=' * (-len(content.strip()) % 4)).decode('utf-8', errors='ignore')
                except: pass

            # 【野蛮逻辑】：只要这一行包含域名，整行抓走，不做任何剔除
            lines = content.split('\n')
            for line in lines:
                if "gotochinatown.net" in line:
                    clean_line = line.strip()
                    if clean_line and clean_line not in seen_hashes:
                        raw_data.append(clean_line)
                        seen_hashes.add(clean_line)
        except: continue
    return raw_data

if __name__ == "__main__":
    results = harvest()
    
    # 统一文件名，方便你查看
    with open("all_nodes.txt", "w", encoding="utf-8") as f:
        for r in results:
            f.write(r + "\n")
            
    print(f"✅ 打捞完成！共捕获 {len(results)} 条原始数据。")
