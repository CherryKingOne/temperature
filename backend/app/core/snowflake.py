from __future__ import annotations

import threading
import time

# 起始时间：2024-01-01 00:00:00 UTC（毫秒）
EPOCH_MS = 1704067200000

TIMESTAMP_BITS = 41
WORKER_ID_BITS = 10
SEQUENCE_BITS = 12

MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
SEQUENCE_MASK = (1 << SEQUENCE_BITS) - 1

WORKER_ID_SHIFT = SEQUENCE_BITS
TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS


class SnowflakeGenerator:
    """雪花 ID 生成器。

    结构（64 位）：1 位符号位 + 41 位毫秒时间戳 + 10 位机器号 + 12 位序列号。
    同一毫秒内单机最多生成 4096 个 ID，ID 随时间单调递增。
    """

    def __init__(self, worker_id: int = 1, epoch_ms: int = EPOCH_MS) -> None:
        if not 0 <= worker_id <= MAX_WORKER_ID:
            raise ValueError(f"worker_id 必须在 0 ~ {MAX_WORKER_ID} 之间")
        self._worker_id = worker_id
        self._epoch_ms = epoch_ms
        self._sequence = 0
        self._last_timestamp = -1
        self._lock = threading.Lock()

    def next_id(self) -> int:
        """生成下一个雪花 ID。"""
        with self._lock:
            timestamp = int(time.time() * 1000)
            if timestamp < self._last_timestamp:
                # 时钟回拨：沿用上一次的时间戳，靠序列号保证不重复
                timestamp = self._last_timestamp

            if timestamp == self._last_timestamp:
                self._sequence = (self._sequence + 1) & SEQUENCE_MASK
                if self._sequence == 0:
                    # 当前毫秒序列耗尽，等待下一毫秒
                    while timestamp <= self._last_timestamp:
                        timestamp = int(time.time() * 1000)
            else:
                self._sequence = 0

            self._last_timestamp = timestamp
            return (
                ((timestamp - self._epoch_ms) << TIMESTAMP_SHIFT)
                | (self._worker_id << WORKER_ID_SHIFT)
                | self._sequence
            )

    def parse(self, snowflake_id: int) -> dict[str, int]:
        """解析雪花 ID 的各组成部分（排查问题时使用）。"""
        return {
            "timestamp_ms": (snowflake_id >> TIMESTAMP_SHIFT) + self._epoch_ms,
            "worker_id": (snowflake_id >> WORKER_ID_SHIFT) & MAX_WORKER_ID,
            "sequence": snowflake_id & SEQUENCE_MASK,
        }


_generator: SnowflakeGenerator | None = None
_generator_lock = threading.Lock()


def get_snowflake() -> SnowflakeGenerator:
    """全局唯一的 ID 生成器（进程内单例）。"""
    global _generator
    if _generator is None:
        with _generator_lock:
            if _generator is None:
                from app.core.config import get_settings

                _generator = SnowflakeGenerator(worker_id=get_settings().snowflake_worker_id)
    return _generator


def next_id() -> int:
    """生成一个雪花 ID。"""
    return get_snowflake().next_id()
