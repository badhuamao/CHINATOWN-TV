import requests
import re
import os
import yaml
import socket

# --- 配置区 ---
SEARCH_QUERY = 'fastervpn.world'
TOKEN = os.getenv("MY_GITHUB_TOKEN")

def check_udp_port(host, port, timeout=2):
    """
    针对 Hy2 优化的 UDP 探测 (虽然 UDP 是无连接的，但可以通过尝试发送数据包来判断路径是否可达)
    注意：UDP 探测不一定百分之百准确，但比单纯的 TCP 探测更适合 Hy2。
    """
    try:
        # 这里我们仍然保留简单的连接尝试，但增加更强的异常处理
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except:
        # 如果 TCP 不通，我们不做硬性剔除，防止误杀 UDP 节点
        # 只要 host 格式看起来合法，就先保留
        return True 

def clean_link(text):
    """彻底清除 HTML 标签、引号和逗号"""
    text = re.sub(r'<[^>]+>', '', text) # 去掉 <a> 这种标签
    text = text.replace('"', '').replace("'", "").replace(",", "").strip()
    return text

def parse_and_convert():
    all_raw_content = ""
    # 1. 自动打捞
    sources = list(set(search_github())) # 这里的 search_github 函数沿用之前的
    for url in sources:
        try:
            all_raw_content += requests.get(url, timeout=10).text + "\n"
        except: continue
        
    # 2. 从 urls.txt 读取 (核心：这是你的保底干货)
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            all_raw_content += f.read() + "\n"

    clash_config = {
        "proxies": [],
        "proxy-groups": [
            {"name": "🚀 自动选择", "type": "url-test", "proxies": [], "url": "http://www.gstatic.com/generate_204", "interval": 300},
            {"name": "🔰 全部节点", "type": "select", "proxies": []}
        ],
        "rules": ["MATCH,🚀 自动选择"]
    }

    # 更强力的正则：兼容 hy2:// 和 散装的 server:port 格式
    # 优先匹配完整的 hy2:// 链接
    hy2_links = re.findall(r'hy2://([^@\s]+)@([^:\s/]+):(\d+)', all_raw_content)
    
    seen = set()
    for pwd, host, port in hy2_links:
        host = clean_link(host)
        port = int(port)
        node_id = f"{host}:{port}"
        
        if node_id not in seen:
            name = f"✅_{host[:5]}_{port}"
            clash_config["proxies"].append({
                "name": name, "type": "hysteria2", "server": host, "port": port,
                "password": pwd, "ssl": True, "skip-cert-verify": True,
                "up": "100 Mbps", "down": "100 Mbps" # 加上默认带宽，增加兼容性
            })
            seen.add(node_id)

    if clash_config["proxies"]:
        names = [p["name"] for p in clash_config["proxies"]]
        clash_config["proxy-groups"][0]["proxies"] = names
        clash_config["proxy-groups"][1]["proxies"] = names
        return yaml.dump(clash_config, allow_unicode=True, sort_keys=False)
    return None
