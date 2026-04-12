import requests
import re
import os
import base64

# --- 配置区 ---
SEARCH_QUERY = 'dafei.de' # 换成新地盘
TOKEN = os.getenv("MY_GITHUB_TOKEN")

def search_github():
    if not TOKEN: return []
    # 扩大搜索范围，针对新域名进行全量检索
    search_url = f"https://api.github.com/search/code?q={SEARCH_QUERY}&sort=indexed"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    found_urls = []
    try:
        r = requests.get(search_url, headers=headers, timeout=10)
        if r.status_code == 200:
            for item in r.json().get('items', []):
                # 转换成 raw 链接直接读内容
                raw_url = item['html_url'].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                found_urls.append(raw_url)
    except: pass
    return found_urls

def harvest():
    raw_results = []
    seen_lines = set()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    all_sources = list(set(search_github()))
    print(f"📡 正在新矿区打捞，来源总数: {len(all_sources)}")

    for url in all_sources:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200: continue
            
            content = resp.text
            # 自动处理可能存在的 Base64 订阅格式
            if len(content.strip()) > 30 and ' ' not in content.strip() and '\n' not in content.strip():
                try:
                    content = base64.b64decode(content.strip() + '=' * (-len(content.strip()) % 4)).decode('utf-8', errors='ignore')
                except: pass

            # 【核心策略：整行提取】
            lines = content.split('\n')
            for line in lines:
                if "jzy88.top" in line:
                    clean_line = line.strip()
                    # 只要包含域名且不重复，就抓走
                    if clean_line and clean_line not in seen_lines:
                        raw_results.append(clean_line)
                        seen_hashes.add(clean_line)
        except: continue
    return raw_results

if __name__ == "__main__":
    results = harvest()
    
    # 依然输出到 all_nodes.txt，你可以直接从 GitHub 仓库里看“生肉”
    with open("all_nodes.txt", "w", encoding="utf-8") as f:
        for r in results:
            f.write(r + "\n")
            
    print(f"✅ 新矿区收割完成！共抓获 {len(results)} 条原始行。")
