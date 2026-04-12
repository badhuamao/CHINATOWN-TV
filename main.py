import requests
import re
import os
import base64

# --- 配置区 ---
SEARCH_QUERY = 'gotochinatown.net'
TOKEN = os.getenv("MY_GITHUB_TOKEN")

def search_github():
    if not TOKEN: return []
    # 扩大搜索，不加任何协议后缀
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
    raw_output = []
    seen_lines = set()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    all_sources = search_github()
    print(f"📡 正在全站深度打捞，共计 {len(all_sources)} 个潜在源码...")

    for url in all_sources:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200: continue
            
            # 处理 Base64（订阅链接经常整段编码）
            content = resp.text.strip()
            if len(content) > 30 and ' ' not in content and '\n' not in content:
                try:
                    content = base64.b64decode(content + '=' * (-len(content) % 4)).decode('utf-8', errors='ignore')
                except: pass

            # 【野蛮收割逻辑】：只要这行带域名，整行抓走
            lines = content.split('\n')
            for line in lines:
                if "gotochinatown.net" in line:
                    clean_line = line.strip()
                    if clean_line and clean_line not in seen_lines:
                        # 记录来源，方便咱们回溯
                        raw_output.append(f"📍 SOURCE: {url[:60]}")
                        raw_output.append(clean_line)
                        raw_output.append("-" * 30)
                        seen_lines.add(clean_line)
        except: continue
    return raw_output

if __name__ == "__main__":
    results = harvest()
    with open("all_nodes_raw.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    print(f"✅ 任务完成！捞上来 {len(results)//3} 条原始信息。")
