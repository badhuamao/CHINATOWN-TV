import requests
import re
import os
import yaml
import socket

# --- 配置区 ---
SEARCH_QUERY = 'fastervpn.world'
TOKEN = os.getenv("MY_GITHUB_TOKEN")
TIMEOUT = 3 # 端口测试超时时间（秒），太长会拖慢进度

def check_port(host, port):
    """简单的 TCP 握手测试，判断服务器端口是否开放"""
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return True
    except:
        return False

def search_github():
    if not TOKEN: return []
    # 搜索包含关键字的文件
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
    # 1. 自动打捞
    sources = list(set(search_github()))
    for url in sources:
        try:
            all_raw_content += requests.get(url, timeout=10).text + "\n"
        except: continue
    # 2. 手动补充
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            all_raw_content += f.read() + "\n"

    seen = set()
    clash_config = {
        "proxies": [],
        "proxy-groups": [
            {"name": "🚀 自动选择", "type": "url-test", "proxies": [], "url": "http://www.gstatic.com/generate_204", "interval": 300},
            {"name": "🔰 全部节点", "type": "select", "proxies": []}
        ],
        "rules": ["MATCH,🚀 自动选择"]
    }

    # 提取 Hy2 链接
    found_hy2 = re.findall(r'hy2://([^@]+)@([^:]+):(\d+)', all_raw_content)
    
    print(f"🕵️ 开始质量检查，共发现 {len(found_hy2)} 个潜在节点...")
    
    for pwd, host, port in found_hy2:
        port = int(port)
        node_id = f"{host}:{port}"
        
        if node_id not in seen:
            # --- 核心改良：活检 ---
            if check_port(host, port):
                name = f"✅_{host[:5]}_{port}"
                clash_config["proxies"].append({
                    "name": name, "type": "hysteria2", "server": host, "port": port,
                    "password": pwd, "ssl": True, "skip-cert-verify": True
                })
                print(f"  [PASS] {node_id}")
            else:
                print(f"  [FAIL] {node_id}")
            seen.add(node_id)

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
        print("✅ 过滤完成！高保真 clash.yaml 已就绪。")
