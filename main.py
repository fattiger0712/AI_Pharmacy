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
import cn2an
from audio_utils import SpeechRecognizer
from funasr_utils import SpeechRecognizer
from deepseek_api import MedicineAdvisor

def main():
    va = SpeechRecognizer()
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
        bmi = tizhong / (shengao ** 2)*10000
        va.speak(f"您的BMI是：{bmi}")
        if bmi < 18.5:
            va.speak(" 您的BMI 属于体重过轻，存在健康风险:如免疫力下降,骨质疏松,女性月经紊乱或闭经,贫血等."
                     "建议:增加热量摄入,选择高蛋白,高能量的食物,如瘦肉,鱼类,豆类,坚果,全脂乳制品等."
                     "少食多餐:每天可安排5-6餐,避免一次性摄入过多导致胃部不适."
                     "补充营养素:必要时可在医生指导下服用复合维生素或矿物质补充剂.定期监测:关注体重变化,避免过度节食或运动.")
        elif 18.5 <= bmi < 24:
            va.speak("您的BMI属于正常范围，体重与身高匹配，患慢性病的风险较低。"
                     "建议：保持均衡饮食：摄入充足的蔬菜、水果、全谷物、优质蛋白和健康脂肪。"
                     "规律运动：每周至少150分钟中等强度有氧运动（如快走、游泳）或75分钟高强度运动（如跑步、跳绳）。"
                     "维持健康生活方式：保证充足睡眠，避免熬夜，减少压力。")
        elif 24 <= bmi < 28:
            va.speak("您的BMI属于超重范围，存在健康风险：如高血压、高血脂、2型糖尿病、心血管疾病风险增加。"
                     "建议：控制热量摄入：减少高糖、高脂肪食物，增加膳食纤维摄入（如蔬菜、水果、全谷物）。"
                     "增加运动量：结合有氧运动和力量训练，每周至少150分钟中等强度运动。"
                     "行为改变：记录饮食和运动，避免久坐，定时定量进餐。")
        elif bmi >= 28 :
            va.speak("BMI属于肥胖范围，存在健康风险：严重增加慢性病风险，可能导致睡眠呼吸暂停、关节疾病等。"
                     "建议：医学评估：咨询医生或营养师，制定个性化减重计划。"
                     "饮食干预：采用低热量饮食（每日减少500-750千卡），控制碳水化合物和脂肪摄入。"
                     "强化运动：每周至少200分钟中等强度运动，结合抗阻训练（如举重、深蹲）。"
                     "必要时药物治疗：在医生指导下使用减肥药物或考虑减重手术。")
        break

if __name__ == "__main__":
    main()