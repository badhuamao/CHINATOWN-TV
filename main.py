import requests
import re
import os
import yaml

# --- 配置区 ---
SEARCH_QUERY = 'fastervpn.world'
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

def parse_and_convert():
    all_raw_content = ""
    
    # 1. 从 GitHub 自动化打捞内容
    sources = list(set(search_github()))
    for url in sources:
        try:
            all_raw_content += requests.get(url, timeout=10).text + "\n"
        except: continue
    
    # 2. 从你手动维护的 urls.txt 读取内容 (核心新增)
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            all_raw_content += f.read() + "\n"

    # --- 开始转换逻辑 ---
    seen = set()
    clash_config = {
        "proxies": [],
        "proxy-groups": [
            {"name": "🚀 自动选择", "type": "url-test", "proxies": [], "url": "http://www.gstatic.com/generate_204", "interval": 300},
            {"name": "🔰 全部节点", "type": "select", "proxies": []}
        ],
        "rules": ["MATCH,🚀 自动选择"]
    }

    # 提取所有 Hy2 链接
    found_hy2 = re.findall(r'hy2://[^\s\'"<>]+', all_raw_content)
    for link in found_hy2:
        if link not in seen:
            match = re.match(r'hy2://([^@]+)@([^:]+):(\d+)', link)
            if match:
                pwd, host, port = match.groups()
                name = f"🚀_{host[:5]}_{port}"
                clash_config["proxies"].append({
                    "name": name, "type": "hysteria2", "server": host, "port": int(port),
                    "password": pwd, "ssl": True, "skip-cert-verify": True
                })
                seen.add(link)

    if clash_config["proxies"]:
        names = [p["name"] for p in clash_config["proxies"]]
        clash_config["proxy-groups"][0]["proxies"] = names
        clash_config["proxy-groups"][1]["proxies"] = names
        return yaml.dump(clash_config, allow_unicode=True, sort_keys=False)
    return None

if __name__ == "__main__":
    result = parse_and_convert()
    if result:
        with open("clash.yaml", "w", encoding="utf-8") as f:
            f.write(result)
        print("✅ 混合转换成功！")
