from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json


class VoskRecognizer:
    def __init__(self):
        self.model = Model("models/vosk-model-cn-0.22")
        self.sample_rate = 16000
        self.device = sd.default.device[0]  # 默认录音设备

    def listen(self, timeout=5):
        """实时语音识别"""
        rec = KaldiRecognizer(self.model, self.sample_rate)
        rec.SetWords(True)  # 返回词级时间戳

        print("\n请描述症状（5秒内）：")
        with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype="int16"
        ) as stream:
            for _ in range(int(timeout * self.sample_rate / 8000)):
                data = stream.read(8000)
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    return result.get("text", "")

        # 获取最终结果
        result = json.loads(rec.FinalResult())
        return result.get("text", "")