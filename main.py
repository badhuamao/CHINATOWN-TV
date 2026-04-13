import requests
import yaml
import re

# 目标 Raw 链接
TARGET_URL = "https://raw.githubusercontent.com/Supprise0901/Fetch/refs/heads/main/Superspeed.yaml"

def convert():
    try:
        print(f"📡 正在尝试获取: {TARGET_URL}")
        resp = requests.get(TARGET_URL, timeout=15)
        if resp.status_code != 200:
            print("❌ 访问失败，请检查网络链接")
            return
        
        content = resp.text
        proxies = []

        # 尝试逻辑 A: 如果它本身就是 YAML 格式
        try:
            raw_data = yaml.safe_load(content)
            if isinstance(raw_data, dict) and 'proxies' in raw_data:
                proxies = raw_data['proxies']
        except:
            pass

        # 尝试逻辑 B: 如果 A 失败了，强行正则匹配里面的 hy2:// 链接
        if not proxies:
            hy2_links = re.findall(r'hy2://([^@\s]+)@([^:\s/]+):(\d+)', content)
            for pwd, host, port in hy2_links:
                proxies.append({
                    "name": f"🚀_{host[:5]}_{port}",
                    "type": "hysteria2",
                    "server": host,
                    "port": int(port),
                    "password": pwd,
                    "ssl": True,
                    "skip-cert-verify": True
                })

        if not proxies:
            print("❌ 节点提取失败，文件中似乎没有有效节点数据")
            return

        # 重新封装成电视 Clash 标准格式
        names = [p['name'] for p in proxies]
        clash_config = {
            "proxies": proxies,
            "proxy-groups": [
                {"name": "🚀 自动选择", "type": "url-test", "proxies": names, "url": "http://www.gstatic.com/generate_204", "interval": 300},
                {"name": "🔰 全部节点", "type": "select", "proxies": names}
            ],
            "rules": ["MATCH,🚀 自动选择"]
        }

        with open("clash.yaml", "w", encoding="utf-8") as f:
            yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)
        print(f"✅ 转换成功！共生成 {len(proxies)} 个节点")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    convert()
