import requests
import re
import os
import yaml
from urllib.parse import urlparse, parse_qs, unquote

def parse_hy2_url(url):
    """
    万能解析：能处理标准的，也能处理带一大堆后缀参数的复杂 Hy2 链接
    """
    try:
        url = unquote(url.strip())
        p = urlparse(url)
        if p.scheme != 'hy2': return None
        
        # 提取核心信息
        password = p.username
        host = p.hostname
        port = p.port
        
        # 提取参数 (SNI, Insecure 等)
        params = parse_qs(p.query)
        sni = params.get('sni', [host])[0]
        insecure = params.get('insecure', ['1'])[0] # 默认允许不安全证书
        
        # 提取备注名 (URL 后的 # 部分)
        name_suffix = unquote(p.fragment) if p.fragment else f"{host[:5]}_{port}"
        
        return {
            "name": f"✨_{name_suffix}",
            "type": "hysteria2",
            "server": host,
            "port": int(port),
            "password": password,
            "sni": sni,
            "ssl": True,
            "skip-cert-verify": True if insecure in ['1', 'true'] else False,
            "up": "100 Mbps",
            "down": "100 Mbps"
        }
    except Exception as e:
        print(f"解析失败: {url}, 错误: {e}")
        return None

def parse_and_convert():
    clash_config = {
        "proxies": [],
        "proxy-groups": [
            {"name": "🚀 自动选择", "type": "url-test", "proxies": [], "url": "http://www.gstatic.com/generate_204", "interval": 300},
            {"name": "🔰 全部节点", "type": "select", "proxies": []}
        ],
        "rules": ["MATCH,🚀 自动选择"]
    }
    seen = set()

    # 1. 核心：优先处理 urls.txt (你的宝贝链接)
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                node = parse_hy2_url(line)
                if node and node['server'] not in seen:
                    clash_config["proxies"].append(node)
                    seen.add(node['server'])

    # 2. 辅助：自动打捞 GitHub (只作为补充)
    # ... (这里保留你之前的 search_github 逻辑)
    # ... 但对搜到的结果同样调用 parse_hy2_url

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
