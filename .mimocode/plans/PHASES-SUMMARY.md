# EVOID v2 — Phase Summary

## Phase 1: Core Runtime ✅

**هفته ۱-۲: هسته رانتایم — IOP Native**

### فایل‌های ساخته شده:

| فایل | توضیح | اصل IOP |
|------|-------|---------|
| `evoid/core/intent.py` | تعریف Intent + registry | `@dataclass(frozen=True)` — فقط داده |
| `evoid/core/resolver.py` | Intent → PipelineConfig | `resolve_pipeline()` — تابع خالص |
| `evoid/core/pipeline.py` | اجرای pipeline | `execute()` — تابع خالص |
| `evoid/core/context.py` | محیط اجرای Intent | `@dataclass` — فقط داده |
| `evoid/core/processor.py` | پروتکل پردازنده | `Processor = Callable` — type alias |
| `evoid/core/runtime.py` | نقطه ورود اصلی | `execute()` — تابع خالص |
| `evoid/core/message_bus.py` | ارتباط بین سرویس‌ها | `publish()`, `subscribe()` — توابع |
| `evoid/core/service.py` | کلاس Service | `@dataclass` + توابع `start()`, `call()` |

### اصول رعایت شده:
- Intent = داده خالص (frozen dataclass)
- Processor = تابع (Callable type alias)
- Pipeline = ترکیب توابع (tuple of strings)
- Registry = dict (نه کلاس)
- Context = داده (نه کلاس با behavior)
- Runtime = توابع (نه کلاس)

---

## Phase 2: Contracts + Engines ✅

**هفته ۳-۴: قراردادها و پیاده‌سازی‌ها**

### فایل‌های ساخته شده:

| فایل | توضیح |
|------|-------|
| `evoid/contracts/schema.py` | پروتکل اعتبارسنجی |
| `evoid/contracts/storage.py` | پروتکل ذخیره‌سازی |
| `evoid/contracts/cache.py` | پروتکل کش |
| `evoid/contracts/serializer.py` | پروتکل سریالایزر |
| `evoid/contracts/adapter.py` | پروتکل اداپتور |
| `evoid/engines/schema/native.py` | اعتبارسنجی با dataclass |
| `evoid/engines/storage/memory.py` | ذخیره‌سازی حافظه |
| `evoid/engines/storage/sqlite.py` | ذخیره‌سازی SQLite |
| `evoid/engines/cache/memory.py` | کش LRU با TTL |
| `evoid/engines/serializer/json_engine.py` | سریالایزر JSON |
| `evoid/engines/di/native.py` | تزریق وابستگی ساده |
| `evoid/engines/logger/structlog.py` | لاگ stdlib |
| `evoid/engines/logger/loguru.py` | لاگ Loguru زیبا |
| `evoid/engines/metrics/simple.py` | معیارها و تایمرها |
| `evoid/engines/auth/simple.py` | احراز هویت ساده |
| `evoid/engines/plugin/registry.py` | ثبت پلاگین |
| `evoid/engines/plugin/loader.py` | بارگذاری پلاگین |

### اصول رعایت شده:
- Engine = توابع (نه کلاس)
- Contract = Protocol type (نه behavior)
- Plugin = registry dict (نه کلاس)

---

## Phase 3: Configuration ✅

**هفته ۵: سیستم پیکربندی**

### فایل‌های ساخته شده:

| فایل | توضیح |
|------|-------|
| `evoid/config/loader.py` | بارگذار TOML |
| `evoid/config/deps.py` | نقشه وابستگی‌ها |
| `evoid/config/sync.py` | همگام‌سازی uv |

### نحوه کار:
```toml
# evoid.toml
[service]
name = "my-api"

[engines]
schema = "pydantic"
storage = "redis"
cache = "redis"
logger = "loguru"

[runtime]
adapter = "asgi"
port = 8000
```

```bash
evoid sync  # uv.add packages بر اساس config
```

### اصول رعایت شده:
- Config = dataclass (فقط داده)
- Loader = تابع (نه کلاس)
- Deps map = dict (نقشه وابستگی‌ها)

---

## Phase 4: Adapters + Web Syntax ✅

**هفته ۶-۷: اداپتورها و سینتکس‌ها**

### اداپتورهای ساخته شده:

| اداپتور | فایل | کاربرد |
|---------|------|--------|
| ASGI | `evoid/adapters/asgi.py` | HTTP (Starlette/Uvicorn) |
| CLI | `evoid/adapters/cli.py` | خط فرمان |
| Telegram | `evoid/adapters/telegram.py` | ربات تلگرام (aiogram) |
| Robyn | `evoid/adapters/robyn.py` | وب سرور سریع |
| WebSocket | `evoid/adapters/websocket.py` | ارتباط real-time |

### سینتکس‌های وب (۳ استایل):

| سینتکس | فایل | مخاطب |
|--------|------|-------|
| @route | `evoid/web/route.py` | کاربران FastAPI |
| @controller | `evoid/web/controller.py` | کاربران NestJS/TypeScript |
| IOP | `evoid/web/iop_style.py` | کاربران حرفه‌ای IOP |

### نحوه خودکارسازی Intent:
```
@get("/users/{id}")              # FastAPI style
    ↓
Intent("GET:/users/{id}")       # خودکار ساخته میشه
    ↓
register(intent)                 # ثبت در سیستم
    ↓
register_processor(name, fn)    # ثبت handler
    ↓
آماده اجرا
```

### CLI بروزرسانی شده:
```bash
evoid version
evoid sync [config]        # نصب وابستگی‌ها
evoid run [config]         # اجرا با config
evoid serve [host] [port]  # اجرای سریع
evoid list-intents         # لیست intents
evoid list-processors      # لیست processors
evoid exec <intent>        # اجرای intent
```

### مثال‌های ساخته شده:

| مثال | فایل | توضیح |
|------|------|-------|
| 01_minimal | `examples/01_minimal/` | IOP پایه |
| 02_services | `examples/02_services/` | ارتباط بین سرویس‌ها |
| 03_full_stack | `examples/03_full_stack/` | تمام اجزا با هم |
| 04_web_api | `examples/04_web_api/` | ASGI web API |
| 05_telegram_bot | `examples/05_telegram_bot/` | ربات تلگرام |
| 06_robyn_api | `examples/06_robyn_api/` | Robyn web API |
| 07_websocket | `examples/07_websocket/` | WebSocket |
| 08_plugins | `examples/08_plugins/` | سیستم پلاگین |
| 09_fastapi_style | `examples/09_fastapi_style/` | سینتکس FastAPI |
| 10_nestjs_style | `examples/10_nestjs_style/` | سینتکس NestJS |
| 11_iop_style | `examples/11_iop_style/` | سینتکس IOP |

---

## Phase 5-7: باقی‌مانده

### Phase 5: Processors (هفته ۸)
پردازنده‌های آماده برای استفاده:

| پردازنده | فایل | کاربرد |
|---------|------|--------|
| intent_extractor | `processors/intent_extractor.py` | استخراج Intent از request |
| schema_validator | `processors/schema_validator.py` | اعتبارسنجی با schema engine |
| auth_checker | `processors/auth_checker.py` | بررسی احراز هویت |
| rate_limiter | `processors/rate_limiter.py` | محدودیت نرخ |
| circuit_breaker | `processors/circuit_breaker.py` | قطع‌کن مدار |
| logger_processor | `processors/logger_processor.py` | لاگ اجرای pipeline |

### Phase 6: Examples + Docs (هفته ۹)
- تکمیل مثال‌ها
- بروزرسانی مستندات
- تست‌های یکپارچگی

### Phase 7: Cleanup (هفته ۱۰)
- حذف کدهای باقی‌مانده v1
- بروزرسانی pyproject.toml
- تست نهایی

---

## وضعیت فعلی

```
Phase 1: Core Runtime        ✅ کامل
Phase 2: Contracts + Engines ✅ کامل
Phase 3: Configuration       ✅ کامل
Phase 4: Adapters + Syntax   ✅ کامل
Phase 5: Processors          ⏳ باقی‌مانده
Phase 6: Examples + Docs     ⏳ باقی‌مانده
Phase 7: Cleanup             ⏳ باقی‌مانده
```

**فایل‌های فعلی:**
```
evoid/
├── core/           8 فایل
├── contracts/      5 فایل
├── engines/        14 فایل
├── adapters/       5 فایل
├── web/            3 فایل
└── config/         3 فایل

evoid_cli/          1 فایل
examples/           11 مثال
```

**تست شده:** همه مثال‌ها با موفقیت اجرا شدن ✓
