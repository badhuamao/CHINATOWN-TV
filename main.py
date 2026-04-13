import requests
import re
import os
import yaml

# --- 核心提取逻辑 ---
def fetch_nodes_from_anywhere(line):
    line = line.strip()
    if not line: return []
    proxies = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(line, headers=headers, timeout=10)
        if resp.status_code != 200: return []
        content = resp.text

        # 逻辑 A: 如果是 YAML 格式 (针对你那几个链接)
        if line.endswith('.yaml') or 'proxies:' in content:
            data = yaml.safe_load(content)
            if isinstance(data, dict) and 'proxies' in data:
                return data['proxies']

        # 逻辑 B: 如果是普通文本，正则匹配 hy2://
        found_hy2 = re.findall(r'hy2://([^@]+)@([^:]+):(\d+)', content)
        for pwd, host, port in found_hy2:
            proxies.append({
                "name": f"🚀_{host[:5]}_{port}",
                "type": "hysteria2",
                "server": host,
                "port": int(port),
                "password": pwd,
                "ssl": True,
                "skip-cert-verify": True
            })
    except: pass
    return proxies

def parse_and_convert():
    final_proxies = []
    seen_nodes = set()

    # 1. 自动打捞部分 (保留原有功能)
    # ... (这里调用之前的 search_github 函数获取 sources)
    # for url in sources:
    #     final_proxies.extend(fetch_nodes_from_anywhere(url))

    # 2. 重点：处理你的 urls.txt
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            for line in f:
                nodes = fetch_nodes_from_anywhere(line)
                for n in nodes:
                    # 使用 server+port 作为唯一标识去重
                    uid = f"{n.get('server')}:{n.get('port')}"
                    if uid not in seen_nodes:
                        final_proxies.append(n)
                        seen_nodes.add(uid)

    # 3. 构建标准 Clash 结构
    clash_config = {
        "proxies": final_proxies,
        "proxy-groups": [
            {"name": "🚀 自动选择", "type": "url-test", "proxies": [p['name'] for p in final_proxies], "url": "http://www.gstatic.com/generate_204", "interval": 300},
            {"name": "🔰 全部节点", "type": "select", "proxies": [p['name'] for p in final_proxies]}
        ],
        "rules": ["MATCH,🚀 自动选择"]
    }
    
    return yaml.dump(clash_config, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    # 执行并写入 clash.yaml
