import time
import random
import threading

# 16 位十进制 ID = 13 位毫秒时间戳 + 3 位序列号
# 每毫秒最多 1000 个 ID，足够单机使用
_lock = threading.Lock()
_last_ts = 0
_seq = 0


def generate_snowflake_id() -> int:
    """生成 16 位十进制的简化雪花 ID（毫秒时间戳 + 3 位序列号）"""
    global _last_ts, _seq
    with _lock:
        ts = int(time.time() * 1000)
        if ts == _last_ts:
            _seq = (_seq + 1) % 1000
            if _seq == 0:
                # 同一毫秒序列耗尽，等待到下一毫秒
                while ts <= _last_ts:
                    ts = int(time.time() * 1000)
        else:
            _seq = random.randint(0, 999)
        _last_ts = ts
        return ts * 1000 + _seq
