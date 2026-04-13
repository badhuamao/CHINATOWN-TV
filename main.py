import requests
import yaml
import os

def fetch_and_extract_nodes(url):
    """
    专门对付这种 .yaml 结尾的链接，把里面的节点强行剥离出来
    """
    extracted_proxies = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            # 尝试把内容当作 YAML 解析
            data = yaml.safe_load(resp.text)
            if isinstance(data, dict) and 'proxies' in data:
                print(f"📦 从 {url[-15:]} 中剥离出 {len(data['proxies'])} 个节点")
                return data['proxies']
    except Exception as e:
        print(f"❌ 剥离失败: {url}, 错误: {e}")
    return extracted_proxies

def parse_and_convert():
    clash_config = {
        "proxies": [],
        "proxy-groups": [
            {"name": "🚀 自动选择", "type": "url-test", "proxies": [], "url": "http://www.gstatic.com/generate_204", "interval": 300},
            {"name": "🔰 全部节点", "type": "select", "proxies": []}
        ],
        "rules": ["MATCH,🚀 自动选择"]
    }
    
    seen_names = set()

    # 处理 urls.txt 里的链接
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            for line in f:
                target_url = line.strip()
                if not target_url: continue
                
                # 如果是 .yaml 结尾或者内容是配置文件
                remote_proxies = fetch_and_extract_nodes(target_url)
                for p in remote_proxies:
                    # 防止重名导致 Clash 报错
                    original_name = p.get('name', 'Unknown')
                    if original_name not in seen_names:
                        clash_config["proxies"].append(p)
                        seen_names.add(original_name)

    # 填充策略组
    if clash_config["proxies"]:
        p_names = [p["name"] for p in clash_config["proxies"]]
        clash_config["proxy-groups"][0]["proxies"] = p_names
        clash_config["proxy-groups"][1]["proxies"] = p_names
        return yaml.dump(clash_config, allow_unicode=True, sort_keys=False)
    return None

if __name__ == "__main__":
    result = parse_and_convert()
    if result:
        with open("clash.yaml", "w", encoding="utf-8") as f:
            f.write(result)
