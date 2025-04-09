'''
from audio_utils import VoiceAssistant
from deepseek_api import MedicalAdvisor

import time


def main():
    va = VoiceAssistant()
    advisor = MedicalAdvisor()

    va.speak("欢迎使用智能药房助手")
    va.speak("请在嘟的一声之后描述您的症状或留言，例如头痛、腹泻等")
    while True:
        # 症状采集
        symptoms = va.listen()

        if not symptoms:
            va.speak("未能识别到症状，请靠近麦克风重新描述")
            continue

        # 获取推荐
        result = advisor.get_recommendation(symptoms)

        # 处理推荐结果
        if result["status"] == "success":
            med_list = "、".join(result["medicines"])
            response = f"建议考虑：{med_list}。推荐理由：{result['reason']}"
        else:
            response = "暂时无法提供建议，请咨询专业医师"

        # 语音+文字输出
        print(f"\n=== 推荐结果 ===\n{response}")
        va.speak(response)

        if result["status"] == "success":
            response = "为您推荐以下药品：\n"
            for med in result["medicines"]:
                response += f"{med['name']}，位于{med['location']}；"
            response += f"推荐理由：{result['reason']}"

            # 控制台显示带格式的结果
            print("\n=== 推荐结果 ===")
            for med in result["medicines"]:
                print(f"药品：{med['name']}")
                print(f"位置：{med['location']}")
            print(f"理由：{result['reason']}\n")

            va.speak(response)


        # 继续咨询判断
        va.speak("需要继续咨询吗？请说'需要'或'不需要'")
        choice = va.listen().lower()

        if any(word in choice for word in ["不需要", "不用", "结束"]):
            va.speak("感谢使用，祝您早日康复！")
            break
        elif "需要" not in choice:
            va.speak("未识别到有效指令，服务将自动结束")
            break


if __name__ == "__main__":
    main()
'''
import os

import cn2an

from audio_utils import VoiceAssistant
from funasr_utils import SpeechRecognizer
from deepseek_api import MedicineAdvisor
#from baidu_api import MedicineAdvisor
import time


def main():
    va = VoiceAssistant()
    recognizer = SpeechRecognizer()
    advisor = MedicineAdvisor()
    va.speak("欢迎使用智能药房助手")
    va.speak("请在嘟的一声之后描述您的症状或留言，例如头痛、腹泻等")

    while True:
        # 语音输入
        va.speak("请留言嘟")
        symptoms = recognizer.recognize()
        if not symptoms:
            va.speak("未能识别到症状，请靠近麦克风重新描述")
            continue

        print(f"\n识别结果：{symptoms}")

        # 获取推荐
        result = advisor.get_recommendation(symptoms)
        print(f"\n推理结果：{result}")
        # 处理推荐结果
        if result["status"] == "success":
            response = "为您推荐以下药品：\n"
            for med in result["medicines"]:
                response += f"{med['name']}，位于{med['location']}；"
            response += f"推荐理由：{result['reason']}"
            va.speak(response)

        # 继续咨询判断
        va.speak("需要继续咨询吗？请说'需要'或'不需要'")
        va.speak("请留言嘟")
        choice = recognizer.recognize()

        if any(word in choice for word in ["不需要", "不用", "结束"]):
            va.speak("感谢使用，祝您早日康复！")
            break
        elif "需要" not in choice:
            va.speak("未识别到有效指令，服务将自动结束")
            break
    while True:
        va.speak("请问您需要了解您的BMI吗？请说'需要'或'不需要'")
        choice = recognizer.recognize()
        if any(word in choice for word in ["不需要", "不用", "结束"]):
            va.speak("好的！欢迎下次光临！")
            break
        elif "需要" not in choice:
            va.speak("未识别到有效指令，服务将自动结束")
        va.speak("请告诉我您的体重，单位千克")

        while True:
            va.speak("请留言嘟")
            symptoms = recognizer.recognize()
            if not symptoms:
                va.speak("未能识别到声音，请靠近麦克风重新描述")
                continue
            elif symptoms:
                print(f"\n识别结果：{symptoms}")
                symptoms = symptoms.strip("。！？千克厘米")  # 去除结尾标点
                symptoms = cn2an.cn2an(symptoms,"smart")
                tizhong = symptoms
                break
        va.speak("请告诉我您的身高，单位厘米")
        while True:
            va.speak("请留言嘟")
            symptoms = recognizer.recognize()
            if not symptoms:
                va.speak("未能识别到声音，请靠近麦克风重新描述")
                continue
            elif symptoms:
                print(f"\n识别结果：{symptoms}")
                symptoms = symptoms.strip("。！？千克厘米")  # 去除结尾标点
                symptoms = cn2an.cn2an(symptoms,"smart")
                shengao = symptoms
                break
        BMI = tizhong / (shengao ** 2)*10000
        va.speak(f"您的BMI是：{BMI}")
        if BMI < 18.5:
            va.speak()
        elif BMI >= 18.5 and BMI < 24:
            va.speak()
        elif BMI >= 24 and BMI < 28:
            va.speak()
        elif BMI >= 28 :
            va.speak()

        break

if __name__ == "__main__":
    main()