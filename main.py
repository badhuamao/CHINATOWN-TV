import requests
import yaml

# 你的目标 Raw 链接
TARGET_URL = "https://raw.githubusercontent.com/Supprise0901/Fetch/refs/heads/main/Superspeed.yaml"

def convert():
    try:
        print(f"正在获取节点: {TARGET_URL}")
        resp = requests.get(TARGET_URL, timeout=15)
        if resp.status_code != 200:
            print("下载失败，请检查网络或链接")
            return
        
        # 解析原始 YAML
        raw_data = yaml.safe_load(resp.text)
        if not raw_data or 'proxies' not in raw_data:
            print("原始文件中没有找到 proxies 节点")
            return

        # 重新封装成标准 Clash 订阅格式
        proxies = raw_data['proxies']
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
        print(f"✅ 转换成功！共提取 {len(proxies)} 个节点")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    convert()
