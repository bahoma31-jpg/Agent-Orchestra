"""
utils/logger.py - نظام التسجيل الموحّد لـ AgentOrchestra

يوفر:
    - setup_logger()  : إنشاء Logger مع Console + File + Error handlers
    - get_logger()    : استرجاع logger موجود أو إنشاء جديد
    - JsonFormatter   : تنسيق JSON للسجلات البنيوية
    - Singleton pattern: نفس الـ Logger لكل اسم
    - تدوير يومي للملفات مع حفظ 30 يوم

الاستخدام:
    from utils.logger import setup_logger
    logger = setup_logger(__name__)
    logger.info("النظام جاهز")
    logger.error("خطأ في التنفيذ", exc_info=True)
"""

import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# المسار الافتراضي للسجلات
_DEFAULT_LOGS_DIR = Path(__file__).parent.parent / "logs"

# سجل داخلي لتطبيق Singleton pattern
_loggers: dict = {}


class JsonFormatter(logging.Formatter):
    """
    مُنسِّق JSON للسجلات البنيوية (Structured Logging).
    يُنتج كل سجل كـ JSON سطر واحد لسهولة التحليل الآلي.

    مثال مخرج:
        {"timestamp": "2026-03-04T14:00:00Z", "name": "orchestrator",
         "level": "INFO", "message": "تم استلام المهمة", ...}
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        return json.dumps(log_data, ensure_ascii=False)


class StandardFormatter(logging.Formatter):
    """
    مُنسِّق نصي قياسي مع دعم Unicode.
    """

    FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        super().__init__(fmt=self.FORMAT, datefmt=self.DATE_FORMAT)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    logs_dir: Optional[Path] = None,
    json_format: bool = False,
) -> logging.Logger:
    """
    إنشاء أو استرجاع Logger موحّد لمكوّن معين.

    يُنشئ ثلاثة handlers:
        1. Console (StreamHandler)          : عرض في Terminal
        2. Daily Rotating File              : logs/{name}.log (30 يوم)
        3. Error File (RotatingFileHandler) : logs/errors.log (10MB)

    Args:
        name      : اسم اللوغر (يُفضَّل استخدام __name__)
        level     : مستوى التسجيل (DEBUG=10, INFO=20, WARNING=30, ERROR=40)
        logs_dir  : مجلد السجلات (افتراضي: logs/ في جذر المشروع)
        json_format: إذا True، يستخدم تنسيق JSON بدلاً من النص العادي

    Returns:
        logging.Logger: لوغر مُعدَّد جاهز للاستخدام

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("بدء التشغيل")
        >>> logger = setup_logger("orchestrator", level=logging.DEBUG)
    """
    global _loggers

    # Singleton: إعادة نفس اللوغر إذا كان موجوداً مسبقاً
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # تجنب تكرار السجلات في root logger

    # تجنب إضافة handlers مكررة
    if logger.handlers:
        _loggers[name] = logger
        return logger

    # تحديد مجلد السجلات وإنشاؤه إذا لم يكن موجوداً
    log_dir = logs_dir or _DEFAULT_LOGS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    # اختيار المُنسِّق
    formatter = JsonFormatter() if json_format else StandardFormatter()

    # ── Handler 1: Console ──────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── Handler 2: ملف يومي دوّار ───────────────────────────
    log_file = log_dir / f"{name}.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
        utc=False,
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"
    logger.addHandler(file_handler)

    # ── Handler 3: ملف الأخطاء المستقل ──────────────────────
    error_file = log_dir / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    _loggers[name] = logger
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    استرجاع logger موجود أو إنشاء جديد بإعدادات افتراضية.

    Args:
        name: اسم اللوغر

    Returns:
        logging.Logger
    """
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)


def reset_loggers():
    """
    إعادة تعيين جميع الـ loggers (مفيد في الاختبارات).
    """
    global _loggers
    for logger in _loggers.values():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    _loggers.clear()


# لوغر النظام الرئيسي - يُستخدم عند تشغيل utils مباشرة
system_logger = setup_logger(
    "agent_orchestra",
    logs_dir=_DEFAULT_LOGS_DIR,
)
