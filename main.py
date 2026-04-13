import requests
import re
import os
import yaml

# --- 核心提取函数 ---
def fetch_from_url(url):
    proxies = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        print(f"📡 正在处理: {url[:50]}...")
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return []
        
        content = resp.text
        # 模式 A: 对方本身就是 Clash YAML 格式
        if 'proxies:' in content:
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict) and 'proxies' in data:
                    return data['proxies']
            except: pass
        
        # 模式 B: 散装的 hy2:// 链接
        hy2_raw = re.findall(r'hy2://([^@\s]+)@([^:\s/]+):(\d+)', content)
        for pwd, host, port in hy2_raw:
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
    all_proxies = []
    seen_ids = set()

    # 1. 处理你的 urls.txt (最高优先级，包含那几个 YAML 链接)
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            for line in f:
                target = line.strip()
                if not target: continue
                new_nodes = fetch_from_url(target)
                for n in new_nodes:
                    uid = f"{n.get('server')}:{n.get('port')}"
                    if uid not in seen_ids:
                        all_proxies.append(n)
                        seen_ids.add(uid)

    # 2. 如果你想保留之前的 GitHub 自动打捞，可以在这里调用之前的 search 函数
    # sources = search_github() 
    # for s in sources: ... (逻辑同上，append 到 all_proxies)

    if not all_proxies:
        print("❌ 没捞到任何节点，检查下链接活不活着")
        return None

    # 3. 组装最终配置文件
    names = [p['name'] for p in all_proxies]
    config = {
        "proxies": all_proxies,
        "proxy-groups": [
            {"name": "🚀 自动选择", "type": "url-test", "proxies": names, "url": "http://www.gstatic.com/generate_204", "interval": 300},
            {"name": "🔰 全部节点", "type": "select", "proxies": names}
        ],
        "rules": ["MATCH,🚀 自动选择"]
    }
    return yaml.dump(config, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    # 修正了 image_bb4009.png 里的缩进报错
    final_yaml = parse_and_convert()
    if final_yaml:
        with open("clash.yaml", "w", encoding="utf-8") as f:
            f.write(final_yaml)
        print("✅ 炼金成功！clash.yaml 已刷新。")
