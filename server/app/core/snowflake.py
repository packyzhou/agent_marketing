import time

def generate_snowflake_id() -> int:
    """简化的雪花算法ID生成器"""
    timestamp = int(time.time() * 1000)
    return timestamp << 22
