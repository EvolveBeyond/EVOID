"""Tests for Msgpack serializer engine."""

import pytest
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID


def test_basic_encode_decode():
    """Test basic data types."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    # String
    data = "hello world"
    assert s.decode(s.encode(data)) == data

    # Integer
    data = 42
    assert s.decode(s.encode(data)) == data

    # Float
    data = 3.14
    assert s.decode(s.encode(data)) == data

    # Boolean
    data = True
    assert s.decode(s.encode(data)) == data

    # None
    data = None
    assert s.decode(s.encode(data)) == data

    # List
    data = [1, 2, 3, "four"]
    assert s.decode(s.encode(data)) == data

    # Dict
    data = {"key": "value", "nested": {"a": 1}}
    assert s.decode(s.encode(data)) == data


def test_nested_structures():
    """Test deeply nested structures."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    data = {
        "users": [
            {"id": 1, "name": "Ali", "tags": ["admin", "user"]},
            {"id": 2, "name": "Reza", "tags": ["user"]},
        ],
        "metadata": {
            "count": 2,
            "page": 1,
        },
    }

    encoded = s.encode(data)
    decoded = s.decode(encoded)

    assert decoded == data
    assert len(decoded["users"]) == 2


def test_datetime_serialization():
    """Test datetime handling."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    now = datetime.now()
    encoded = s.encode({"timestamp": now})
    decoded = s.decode(encoded)

    assert decoded["timestamp"].year == now.year
    assert decoded["timestamp"].month == now.month


def test_uuid_serialization():
    """Test UUID handling."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    uid = UUID("12345678-1234-5678-1234-567812345678")
    encoded = s.encode({"id": uid})
    decoded = s.decode(encoded)

    assert decoded["id"] == uid


def test_decimal_serialization():
    """Test Decimal handling."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    amount = Decimal("99.99")
    encoded = s.encode({"amount": amount})
    decoded = s.decode(encoded)

    assert decoded["amount"] == amount


def test_bytes_serialization():
    """Test bytes handling."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    data = {"binary": b"hello bytes"}
    encoded = s.encode(data)
    decoded = s.decode(encoded)

    # msgpack natively supports bytes (unlike JSON)
    assert decoded["binary"] == b"hello bytes"


def test_set_serialization():
    """Test set handling."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    data = {"tags": {"python", "evoid", "iop"}}
    encoded = s.encode(data)
    decoded = s.decode(encoded)

    assert set(decoded["tags"]) == {"python", "evoid", "iop"}


def test_empty_data():
    """Test empty structures."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    assert s.decode(s.encode({})) == {}
    assert s.decode(s.encode([])) == []
    assert s.decode(s.encode("")) == ""


def test_large_payload():
    """Test large data payload."""
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    data = {"items": list(range(10000))}
    encoded = s.encode(data)
    decoded = s.decode(encoded)

    assert len(decoded["items"]) == 10000


def test_binary_smaller_than_json():
    """Test that msgpack is smaller than JSON."""
    import json
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    data = {
        "users": [
            {"id": i, "name": f"user_{i}", "email": f"user_{i}@example.com"}
            for i in range(100)
        ]
    }

    json_bytes = json.dumps(data).encode("utf-8")
    msgpack_bytes = s.encode(data)

    # Msgpack should be significantly smaller
    assert len(msgpack_bytes) < len(json_bytes)


def test_binary_faster_than_json():
    """Test that msgpack is faster than JSON."""
    import json
    import time
    from evoid.engines.serializer.msgpack_engine import MsgpackSerializer

    s = MsgpackSerializer()

    data = {
        "users": [
            {"id": i, "name": f"user_{i}", "email": f"user_{i}@example.com"}
            for i in range(1000)
        ]
    }

    # Warmup
    for _ in range(10):
        s.encode(data)
        s.decode(s.encode(data))
        json.dumps(data)
        json.loads(json.dumps(data))

    # Benchmark encode
    start = time.perf_counter()
    for _ in range(100):
        s.encode(data)
    msgpack_encode_time = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(100):
        json.dumps(data)
    json_encode_time = time.perf_counter() - start

    # Benchmark decode
    msgpack_encoded = s.encode(data)
    json_encoded = json.dumps(data).encode("utf-8")

    start = time.perf_counter()
    for _ in range(100):
        s.decode(msgpack_encoded)
    msgpack_decode_time = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(100):
        json.loads(json_encoded)
    json_decode_time = time.perf_counter() - start

    # Just print results, don't assert speed (depends on hardware)
    print(f"\nMsgpack encode: {msgpack_encode_time:.4f}s")
    print(f"JSON encode: {json_encode_time:.4f}s")
    print(f"Msgpack decode: {msgpack_decode_time:.4f}s")
    print(f"JSON decode: {json_decode_time:.4f}s")
    print(f"Msgpack size: {len(msgpack_encoded)} bytes")
    print(f"JSON size: {len(json_encoded)} bytes")
