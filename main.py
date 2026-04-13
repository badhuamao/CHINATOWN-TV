import requests
import yaml
import re

# 针对你提供的链接进行专项转换
TARGET_URL = "https://raw.githubusercontent.com/Supprise0901/Fetch/refs/heads/main/Superspeed.yaml"

def convert():
    try:
        print(f"📡 开始抓取源文件...")
        resp = requests.get(TARGET_URL, timeout=15)
        if resp.status_code != 200:
            print("❌ 无法访问源文件，请检查链接")
            return
        
        # 提取 proxies 部分
        content = resp.text
        proxies = []
        
        # 尝试标准 YAML 解析
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict) and 'proxies' in data:
                proxies = data['proxies']
        except:
            pass
            
        # 如果 YAML 解析失败，启动正则强制提取 (保底方案)
        if not proxies:
            print("⚠️ YAML 结构异常，启动强制提取模式...")
            # 匹配 Hysteria2 的关键参数
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
            print("❌ 没捞到任何节点")
            return

        # 封装成电视端能识别的完整 Clash 格式
        final_config = {
            "proxies": proxies,
            "proxy-groups": [
                {"name": "🚀 自动选择", "type": "url-test", "proxies": [p['name'] for p in proxies], "url": "http://www.gstatic.com/generate_204", "interval": 300},
                {"name": "🔰 全部节点", "type": "select", "proxies": [p['name'] for p in proxies]}
            ],
            "rules": ["MATCH,🚀 自动选择"]
        }

        with open("clash.yaml", "w", encoding="utf-8") as f:
            yaml.dump(final_config, f, allow_unicode=True, sort_keys=False)
        print(f"✅ 炼金成功！共提取 {len(proxies)} 个节点")

    except Exception as e:
        print(f"🔥 运行崩溃: {e}")

if __name__ == "__main__":
    convert()
