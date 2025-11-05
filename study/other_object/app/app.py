from flask import Flask
import requests

app = Flask(__name__)

@app.route("/get-ip")
def get_public_ip():
    try:
        # 使用公开公网IP查询服务
        ip = requests.get("https://ifconfig.me/ip").text.strip()
        return {
            "success": True,
            "public_ip": ip,
            "message": "该 IP 可用于添加到高德 Key 的 IP 白名单"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    app.run()
