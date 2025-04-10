'''
import speech_recognition as sr
import pyttsx3
import platform
import os
from config import  ENABLE_T2S_CONVERSION, SIMULATE_HARDWARE
from opencc import OpenCC  # 确保已安装opencc==1.1.6


class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.cc = OpenCC('t2s') if ENABLE_T2S_CONVERSION else None
        self.engine = self._init_tts_engine()
        self._mic_initialized = False
        self._init_microphone()

    def _init_tts_engine(self):
        """初始化跨平台语音合成引擎"""
        engine = pyttsx3.init()

        # Windows系统配置
        if platform.system() == 'Windows':
            try:
                # 尝试加载中文语音
                engine.setProperty('voice',
                                   'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-CN_HUIHUI_11.0')
            except Exception as e:
                print(f"[警告] 中文语音加载失败: {str(e)}，将使用默认引擎")

        # Linux系统配置
        elif platform.system() == 'Linux':
            engine.setProperty('voice', 'chinese')
            engine.setProperty('rate', 160)  # 调整语速

        # 通用设置
        engine.setProperty('volume', 0.9)  # 音量范围0.0-1.0
        return engine

    def _init_microphone(self):
        """初始化麦克风设备"""
        try:
            with sr.Microphone() as source:
                print("[初始化] 正在校准环境噪音...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self._mic_initialized = True
        except Exception as e:
            if SIMULATE_HARDWARE:
                print("[模拟模式] 麦克风不可用")
            else:
                raise RuntimeError(f"麦克风初始化失败: {str(e)}")

    def listen(self, timeout=7, retries=2):
        """采集并处理语音输入"""
        for attempt in range(retries):
            try:
                if not self._mic_initialized and not SIMULATE_HARDWARE:
                    raise RuntimeError("麦克风未初始化")

                with sr.Microphone() as source:
                    print("\n[状态] 请开始说话...")
                    self.engine.say("嘟")  # 语音提示
                    self.engine.runAndWait()
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=10  # 最长录音时间
                    )
                    print("录音结束")
                    # 使用Whisper识别
                    raw_text = self.recognizer.recognize_whisper(
                        audio,
                        language="zh",
                        model=WHISPER_MODEL,
                        initial_prompt="以下是普通话医疗咨询内容"
                    ).strip()

                    # 显示原始输入
                    print(f"[原始输入] {raw_text}")

                    # 繁简转换
                    final_text = self.cc.convert(raw_text) if self.cc else raw_text
                    print(f"[处理后] {final_text}")
                    return final_text

            except sr.WaitTimeoutError:
                print("[超时] 未检测到语音输入")
                if attempt < retries - 1:
                    self.speak("没有听到您的描述，请再试一次")
            except Exception as e:
                print(f"[识别错误] {str(e)}")
                if attempt < retries - 1:
                    self.speak("识别出现问题，请重新描述")

        return ""

    def speak(self, text, async_mode=False):
        """增强版语音输出"""
        print(f"[系统回复] {text}")
        try:
            if async_mode:
                self.engine.startLoop(False)
                self.engine.say(text)
                self.engine.iterate()
                self.engine.endLoop()
            else:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            print(f"[语音输出错误] {str(e)}")

    def list_audio_devices(self):
        """列出所有音频设备（调试用）"""
        print("\n=== 可用音频设备 ===")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{index}: {name}")


if __name__ == "__main__":
    # 调试模式
    va = VoiceAssistant()
    va.list_audio_devices()

    print("\n=== 语音识别测试 ===")
    while True:
        text = va.listen()
        if text:
            va.speak(f"已收到：{text}")
            if "退出测试" in text:
                break
        else:
            va.speak("未能识别到有效输入")
'''
import platform

import pyaudio
import wave
import numpy as np
import pyttsx3
from funasr import AutoModel
from sympy.physics.units import sr

from config import MODEL_SETTINGS, AUDIO_DEVICE


class SpeechRecognizer:
    def __init__(self):
        # 初始化FunASR模型（单例模式）
        self.model = AutoModel(**MODEL_SETTINGS)
        self.engine = self._init_tts_engine()
        # 音频流配置
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            rate=16000,
            format=pyaudio.paInt16,
            channels=2,  # ReSpeaker双麦克风
            input=True,
            input_device_index=AUDIO_DEVICE["input_index"],
            frames_per_buffer=1024
        )

    def _init_tts_engine(self):
        """初始化跨平台语音合成引擎"""
        engine = pyttsx3.init()
        # Linux系统配置
        if platform.system() == 'Linux':
            engine.setProperty('voice', 'chinese')
            engine.setProperty('rate', 160)  # 调整语速

            # 通用设置
        engine.setProperty('volume', 0.9)  # 音量范围0.0-1.0
        return engine

    def record_audio(self, timeout=3):
        """带VAD的录音"""
        frames = []
        silent_count = 0
        for _ in range(int(16000 / 1024 * timeout)):
            data = self.stream.read(1024)
            audio_data = np.frombuffer(data, dtype=np.int16)
            if self.is_silence(audio_data):
                silent_count += 1
                if silent_count > 10: break
            else:
                silent_count = 0
                frames.append(data)
        return b''.join(frames)
    def speak(self, text, async_mode=False):
        """增强版语音输出"""
        print(f"[系统回复] {text}")
        try:
            if async_mode:
                self.engine.startLoop(False)
                self.engine.say(text)
                self.engine.iterate()
                self.engine.endLoop()
            else:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            print(f"[语音输出错误] {str(e)}")

    def list_audio_devices(self):
        """列出所有音频设备（调试用）"""
        print("\n=== 可用音频设备 ===")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{index}: {name}")

    @staticmethod
    def is_silence(data, threshold=2000):
        """静音检测"""
        return np.abs(data).mean() < threshold

    def recognize(self, audio_data):
        """语音识别"""
        with wave.open("temp.wav", 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        return self.model.generate(input="temp.wav")[0]['text']



if __name__ == "__main__":
    # 调试模式
    va = SpeechRecognizer()
    va.list_audio_devices()
