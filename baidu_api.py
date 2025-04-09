import json
import requests
from baidu_auth import BaiduAuth
from config import BAIDU_MODEL, MEDICINE_DB


class MedicineAdvisor:
    def __init__(self):
        with open(MEDICINE_DB, "r", encoding="utf-8") as f:
            self.medicines = json.load(f)

    def _build_messages(self, symptoms):
        """构造符合百度格式的prompt"""
        med_list = "\n".join(
            [f"{name}：适用于{', '.join(info['symptoms'])}"  # 添加缺失的闭合括号
             for name, info in self.medicines.items()]
        )

        return (
                "你是一名药房智能导购员，请根据症状推荐药品并明确说明取货位置：\n"
                f"药品列表：\n{med_list}\n"
                f"用户症状：{symptoms}\n"
                "推荐要求：\n"
                "1. 最多推荐3种最相关药品\n"
                "2. 必须包含药品位置信息\n"
                "严格按以下规则推荐药品：\n"
                "1. 必须从以下列表选择：\n"
                + "\n".join([f"- {name}（位置：{info['location']}）"
                             for name, info in self.medicines.items()]) +
                "\n2. 推荐格式：\n"
                "推荐药品：药品名称（精确位置）\n"
                "推荐理由：结合症状和位置说明\n"
                "示例：\n"
                "推荐药品：布洛芬缓释胶囊（第一行第三列）\n"
                "推荐理由：适用于头痛症状"
                f"\n\n当前用户症状：{symptoms}"
        )

    def get_recommendation(self, symptoms):
        try:
            access_token = BaiduAuth.get_access_token()
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"

            headers = {"Content-Type": "application/json"}
            payload = {
                "messages": self._build_messages(symptoms),
                "temperature": 0.3,
                "stream": False
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return self._parse_response(response.json())
            else:
                return {
                    "status": "api_error",
                    "message": f"HTTP {response.status_code}",
                    "medicines": []
                }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "medicines": []
            }

    def _parse_response(self, data):
        """解析百度API响应"""
        content = data.get("result", "")

        medicines = []
        reason = ""

        # 解析推荐药品
        if "推荐药品：" in content:
            med_line = content.split("推荐药品：")[1].split("\n")[0]
            for item in med_line.split(", "):
                if "（" in item and "）" in item:
                    name, loc = item.split("（", 1)
                    loc = loc.replace("）", "")
                    if name.strip() in self.medicines:
                        medicines.append({
                            "name": name.strip(),
                            "location": loc.strip(),
                            "info": self.medicines[name.strip()]
                        })

        # 解析推荐理由
        if "推荐理由：" in content:
            reason = content.split("推荐理由：")[1].split("\n")[0].strip()

        return {
            "status": "success" if medicines else "no_match",
            "medicines": medicines[:3],  # 最多返回3种
            "reason": reason
        }



