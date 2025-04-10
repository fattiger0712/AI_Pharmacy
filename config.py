'''
# 系统配置
DEEPSEEK_API_KEY = "sk-e5d64761d7954d77b5bbdbb5f06ad802"  # DeepSeek API密钥
HOTWORDS_PATH = "hotwords.txt"         # 热词文件路径
MODEL_SETTINGS = {
    "model": "damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    "model_dir":"C:/Users/lenovo/.cache/modelscope/hub/damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    "disable_update": True,  # 新增此行
    "vad_model": "fsmn-vad",
    "punc_model": "ct-punc-c",
    "device": "cpu",
    "quantize": True,
}
WHISPER_MODEL = "base"                  # tiny/base/small/medium
ENABLE_T2S_CONVERSION = True            # 启用繁简转换

# 硬件模拟配置
SIMULATE_HARDWARE = True               # 无树莓派时启用模拟模式

# 设置模型缓存路径
MODEL_CACHE_DIR = "C:/Users/lenovo/.cache/modelscope/hub/damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"

MEDICINE_DB = "medicine_db.json"
'''
import os

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-e5d64761d7954d77b5bbdbb5f06ad802"  # 替换为你的API密钥

# 语音模型配置
MODEL_SETTINGS = {
    "model": "speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",  # 树莓派优化模型
    "model_dir": os.path.expanduser("~/.cache/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"),
    "vad_model": "fsmn-vad",
    "punc_model": "ct-punc",
    "device": "cpu",
    "quantize": True
}

# 系统参数
ENABLE_T2S_CONVERSION = True
SIMULATE_HARDWARE = False  # 树莓派上设为False

# ReSpeaker设备配置（通过arecord -l查询实际索引）
AUDIO_DEVICE = {
    "input_index": 2,    # 通常ReSpeaker输入设备索引为2
    "output_index": 3    # 若需音频输出可设置为3或其他
}


HOTWORDS_PATH = "hotwords.txt"         # 热词文件路径
