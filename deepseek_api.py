'''
import requests
import json
from config import DEEPSEEK_API_KEY
import re

class MedicalAdvisor:
    def __init__(self):
        with open("medicine_db.json", "r", encoding="utf-8") as f:
            self.medicines = json.load(f)

    def _build_prompt(self, symptoms):
        # 修正后的药品列表生成
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
        """获取药品推荐"""
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}

        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{
                        "role": "user",
                        "content": self._build_prompt(symptoms)
                    }],
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                timeout=10
            )

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]

                # 使用正则表达式匹配
                medicine_pattern = re.compile(r"(\w+)\s*（(.+?)）")
                medicines = []
                for line in content.split('\n'):
                    if "推荐药品：" in line:
                        matches = medicine_pattern.findall(line.split("：")[1])
                        for name, location in matches:
                            # 验证数据库匹配
                            if name in self.medicines:
                                expected_loc = self.medicines[name]['location']
                                if location != expected_loc:
                                    print(f"[警告] 位置不符：数据库[{expected_loc}] vs API返回[{location}]")
                                medicines.append({"name": name, "location": expected_loc})
                            else:
                                print(f"[错误] 未知药品：{name}")

                # 解析推荐理由
                reason = content.split("推荐理由：")[1].strip() if "推荐理由：" in content else ""

                return {
                    "medicines": medicines,
                    "reason": reason,
                    "status": "success"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
'''
'''
import json
import requests
import re
from config import DEEPSEEK_API_KEY


class MedicineAdvisor:
    def __init__(self):
        with open("medicine_db.json", "r", encoding="utf-8") as f:
            self.medicines = json.load(f)

    def _build_prompt(self, symptoms):
        # 修正后的药品列表生成
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
            "1. 必须从以上列表选择：\n"
            "\n2. 推荐格式：\n"
            "推荐药品：药品名称（精确位置）\n"
            "推荐理由：结合症状和位置说明\n"
            "示例：\n"
            "推荐药品：布洛芬缓释胶囊（第一行第三列）\n"
            "推荐理由：适用于头痛症状"
            f"\n\n当前用户症状：{symptoms}"
        )

    def get_recommendation(self, symptoms):
        """获取带位置信息的推荐"""
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        prompt = self._build_prompt(symptoms)

        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                timeout=30
            )

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return self._parse_response(content)
            return {"error": "API请求失败"}

        except Exception as e:
            return {"error": str(e)}

    def _parse_response(self, content):
        """解析API响应"""
        # 使用正则表达式提取药品和位置
        pattern = re.compile(r"(\w+)\s*（([^)]+)）")
        medicines = []

        if "推荐药品：" in content:
            med_section = content.split("推荐药品：")[1].split("\n")[0]
            matches = pattern.findall(med_section)
            for name, loc in matches:
                if name in self.medicines:
                    medicines.append({
                        "name": name,
                        "location": loc,
                        "info": self.medicines[name]
                    })

        # 提取推荐理由
        reason = content.split("推荐理由：")[1].strip() if "推荐理由：" in content else ""

        return {
            "medicines": medicines[:3],  # 最多返回3种
            "reason": reason,
            "status": "success"
        }
'''
import json
import requests
import re
import time
from requests.exceptions import Timeout
from config import DEEPSEEK_API_KEY


class MedicineAdvisor:
    def __init__(self):
        with open("medicine_db.json", "r", encoding="utf-8") as f:
            self.medicines = json.load(f)

    def _build_prompt(self, symptoms):
        med_list = "\n".join(
            [f"{name}：适用于{', '.join(info['symptoms'])}"
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
            "1. 必须从以上列表选择\n"
            "2. 推荐格式：\n"
            "推荐药品：药品名称（精确位置）\n"
            "推荐理由：结合症状和位置说明\n"
            "示例：\n"
            "推荐药品：布洛芬缓释胶囊（第一行第三列）\n"
            "推荐理由：适用于头痛症状"
            f"\n\n当前用户症状：{symptoms}"
        )

    def get_recommendation(self, symptoms):
        """获取带位置信息的推荐（含重试机制）"""
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        prompt = self._build_prompt(symptoms)

        # 重试配置
        max_retries = 3
        retry_delay = 1  # 初始延迟1秒
        timeout_config = (20, 60)  # 连接超时5秒，响应超时20秒
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 300
                    },
                    timeout=timeout_config
                )
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    return self._parse_response(content)
                else:
                    return {"error": f"API请求失败，状态码：{response.status_code}"}
            except Timeout as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避策略
                    continue
                return {
                    "error": "请求超时，请检查：\n1. 网络连接是否正常\n2. 是否开启了VPN/代理\n3. 稍后重试",
                    "status": "error"
                }
            except Exception as e:
                return {"error": str(e), "status": "error"}

    def _parse_response(self, content):
        """解析API响应"""
        pattern = re.compile(r"(\w+)\s*（([^)]+)）")
        medicines = []
        # 提取药品信息
        if "推荐药品：" in content:
            med_section = content.split("推荐药品：")[1].split("\n")[0]
            matches = pattern.findall(med_section)
            for name, loc in matches:
                if name in self.medicines:
                    medicines.append({
                        "name": name,
                        "location": loc,
                        "info": self.medicines[name]
                    })
        # 提取推荐理由
        reason = content.split("推荐理由：")[1].strip() if "推荐理由：" in content else ""
        return {
            "medicines": medicines[:3],
            "reason": reason,
            "status": "success"
        }