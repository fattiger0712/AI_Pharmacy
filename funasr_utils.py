import threading
import time

import pyaudio
import wave
import numpy as np
from funasr import AutoModel
from config import MODEL_SETTINGS, HOTWORDS_PATH
from model_manager import asr_model

'''
# 定义全局变量和锁
_model_cache = None
_model_lock = threading.Lock()
_model_ready = threading.Event()

def _preload_model():
    global _model_cache
    with _model_lock:
        if _model_cache is None:
            print("⏳ 开始预加载语音识别模型...")
            _model_cache = AutoModel(**MODEL_SETTINGS)
            _model_ready.set()  # 标记模型就绪
            print("✅ 模型预加载完成")

# 启动预加载线程
threading.Thread(target=_preload_model, daemon=True).start()


class SpeechRecognizer:
    def __init__(self):
        # 等待模型加载完成
        print("🕒 等待模型初始化...")
        _model_ready.wait()  # 阻塞直到模型就绪

        global _model_cache
        self.model = _model_cache
        print("🎉 语音识别器准备就绪")
'''
class SpeechRecognizer:
    def __init__(self):
        self.model = asr_model  # 直接使用预加载模型
        print("🎉 语音识别器准备就绪")
        # 硬件适配参数
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.silence_threshold = 600  # 笔记本麦克风建议600-800
        self.min_recording_sec = 0.8
        self.max_silent_sec = 3.5

        # 初始化FunASR模型
        self.model = AutoModel(
            model=MODEL_SETTINGS["model"],
            disable_update=True,
            vad_model=MODEL_SETTINGS["vad_model"],
            punc_model=MODEL_SETTINGS["punc_model"],
            device=MODEL_SETTINGS["device"],
            quantize=True  # 启用8位量化加速
        )

    def _record_audio(self, timeout=5):
        pa = pyaudio.PyAudio()

        # 显式指定笔记本内置麦克风
        input_device_index = None
        for i in range(pa.get_device_count()):
            dev_info = pa.get_device_info_by_index(i)
            if "麦克风" in dev_info["name"] and dev_info["maxInputChannels"] > 0:
                input_device_index = i
                break

        stream = pa.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=self.chunk_size
        )

        frames = []
        silent_frames = 0
        max_silent_sec = 3  # 允许的最大静音时间(1.5)

        print("\n请描述症状（5秒内）：")
        for _ in range(int(self.sample_rate / self.chunk_size * timeout)):
            data = stream.read(self.chunk_size)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # 实时静音检测
            if np.abs(audio_data).mean() < self.silence_threshold:
                silent_frames += 1
                if silent_frames > (max_silent_sec * self.sample_rate / self.chunk_size):
                    break
            else:
                silent_frames = 0
                frames.append(data)

        # 保存临时音频文件
        wav_path = "temp_recording.wav"
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(pa.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

        stream.stop_stream()
        stream.close()
        pa.terminate()
        return wav_path

    def recognize(self):
        """执行语音识别"""
        try:
            audio_path = self._record_audio()
            result = self.model.generate(
                input=audio_path,
                hotwords=HOTWORDS_PATH  # 加载热词文件
            )
            return result[0]['text'].strip()
        except Exception as e:
            print(f"语音识别错误: {str(e)}")
            return ""