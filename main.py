import requests
import re
import os
import base64

# --- 配置区 ---
# 关键字直接设为新域名
SEARCH_QUERY = 'gotochinatown.net'
TOKEN = os.getenv("MY_GITHUB_TOKEN")

def search_github():
    if not TOKEN: return []
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
    seen_content = set()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 获取全站搜索到的所有源链接
    all_sources = search_github()
    print(f"📡 搜索到 {len(all_sources)} 个潜在源码文件...")

    for url in all_sources:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200: continue
            content = resp.text.strip()
            
            # Base64 自动解码（为了看到里面的真面目）
            if len(content) > 30 and ' ' not in content and '\n' not in content:
                try:
                    content = base64.b64decode(content + '=' * (-len(content) % 4)).decode('utf-8')
                except: pass

            # 【核心逻辑】：只要这一行包含域名，我们就把这一行完整拿走
            # 这种方式最粗暴，也最不容易漏掉节点
            lines = content.split('\n')
            for line in lines:
                clean_line = line.strip()
                if "gotochinatown.net" in clean_line:
                    # 去重，防止同一个节点反复刷屏
                    if clean_line not in seen_content:
                        raw_results.append(clean_line)
                        seen_content.add(clean_line)
        except: continue
    return raw_results

if __name__ == "__main__":
    nodes = harvest()
    
    # 咱们不写 YAML 了，直接写个纯文本文件
    with open("all_nodes.txt", "w", encoding="utf-8") as f:
        for n in nodes:
            f.write(n + "\n")
            
    print(f"✅ 任务完成！共扫出 {len(nodes)} 行包含目标的原始数据。")
    print("📁 结果已存入 all_nodes.txt")
