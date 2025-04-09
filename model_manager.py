
from funasr import AutoModel
import atexit
from config import MODEL_SETTINGS


class ModelManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            print("⏳ 初始化语音模型（仅首次）...")
            cls._instance = AutoModel(**MODEL_SETTINGS)
            atexit.register(cls._cleanup)  # 程序退出时清理
        return cls._instance

    @classmethod
    def _cleanup(cls):
        if cls._instance:
            del cls._instance
            print("♻️ 已释放模型资源")


# 全局单例
asr_model = ModelManager()
'''
import os
import fcntl

from funasr import AutoModel

from config import MODEL_SETTINGS


class ModelManager:
    _instance = None
    _lock_file = "/tmp/model.lock"

    def __new__(cls):
        # 使用文件锁确保系统级单例
        lock_fd = os.open(cls._lock_file, os.O_CREAT)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if not cls._instance:
                print("🔄 系统级模型初始化...")
                cls._instance = AutoModel(**MODEL_SETTINGS)
        except BlockingIOError:
            print("⚠️ 模型已由其他进程加载，直接复用")
        finally:
            os.close(lock_fd)
        return cls._instance
'''