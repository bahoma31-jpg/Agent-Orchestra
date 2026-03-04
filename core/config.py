"""
core/config.py - مدير الإعدادات المركزي لـ AgentOrchestra

يحتوي على جميع إعدادات التطبيق مع قيم افتراضية آمنة.
جميع القيم تُقرأ من .env عبر python-dotenv.

الاستخدام:
    from core.config import Config
    config = Config.from_env()
    config.validate()
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv اختياري عند الاختبار


@dataclass
class APIConfig:
    """إعدادات واجهات برمجة التطبيقات (API)"""

    # ── Groq ──────────────────────────────────────────────────
    groq_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str = field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    groq_max_tokens: int = field(default_factory=lambda: int(os.getenv("GROQ_MAX_TOKENS", "8000")))
    groq_timeout: int = field(default_factory=lambda: int(os.getenv("GROQ_TIMEOUT", "60")))

    # ── Google Gemini ─────────────────────────────────────────
    gemini_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
    gemini_pro_model: str = field(default_factory=lambda: os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"))

    # ── Anthropic Claude ──────────────────────────────────────
    anthropic_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    claude_model: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219"))

    # ── GitHub ────────────────────────────────────────────────
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))

    # ── Telegram ──────────────────────────────────────────────
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    # ── Gmail ─────────────────────────────────────────────────
    gmail_address: str = field(default_factory=lambda: os.getenv("GMAIL_ADDRESS", ""))
    gmail_app_password: str = field(default_factory=lambda: os.getenv("GMAIL_APP_PASSWORD", ""))

    # ── SerpAPI (اختياري) ─────────────────────────────────────
    serp_api_key: str = field(default_factory=lambda: os.getenv("SERP_API_KEY", ""))


@dataclass
class PathsConfig:
    """مسارات المشروع - جميعها نسبية إلى BASE_DIR"""

    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def logs_dir(self) -> Path:
        """مجلد السجلات"""
        return self.base_dir / "logs"

    @property
    def memory_dir(self) -> Path:
        """مجلد الذاكرة"""
        return self.base_dir / "memory"

    @property
    def knowledge_dir(self) -> Path:
        """مجلد قاعدة المعرفة"""
        return self.base_dir / "knowledge"

    @property
    def backups_dir(self) -> Path:
        """مجلد النسخ الاحتياطية"""
        return self.base_dir / "backups"

    @property
    def web_dir(self) -> Path:
        """مجلد واجهة الويب"""
        return self.base_dir / "web"

    @property
    def tests_dir(self) -> Path:
        """مجلد الاختبارات"""
        return self.base_dir / "tests"


@dataclass
class ExecutionConfig:
    """إعدادات التنفيذ والأداء"""

    max_workers: int = field(default_factory=lambda: int(os.getenv("MAX_WORKERS", "7")))
    worker_timeout: int = field(default_factory=lambda: int(os.getenv("WORKER_TIMEOUT", "1800")))  # 30 دقيقة
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    critic_max_rounds: int = field(default_factory=lambda: int(os.getenv("CRITIC_MAX_ROUNDS", "5")))
    infinite_loop_threshold: int = field(default_factory=lambda: int(os.getenv("INFINITE_LOOP_THRESHOLD", "3")))


@dataclass
class FlaskConfig:
    """إعدادات خادم Flask"""

    host: str = field(default_factory=lambda: os.getenv("FLASK_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("FLASK_PORT", "5000")))
    debug: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "false").lower() == "true")
    secret_key: str = field(default_factory=lambda: os.getenv("FLASK_SECRET_KEY", "change-me-in-production"))


@dataclass
class LoggingConfig:
    """إعدادات نظام التسجيل"""

    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    max_bytes: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_BYTES", "10485760")))  # 10 MB
    backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "30")))
    json_format: bool = field(default_factory=lambda: os.getenv("LOG_JSON_FORMAT", "false").lower() == "true")


class Config:
    """
    مدير الإعدادات المركزي لـ AgentOrchestra.

    يجمع جميع الإعدادات في مكان واحد مع:
    - دعم التحميل من .env
    - التحقق الشامل (validate)
    - التصدير لـ dict دون الأسرار

    مثال:
        config = Config.from_env()
        config.validate()
        print(config.api.groq_model)
    """

    def __init__(self):
        self.api = APIConfig()
        self.paths = PathsConfig()
        self.execution = ExecutionConfig()
        self.flask = FlaskConfig()
        self.logging = LoggingConfig()
        self._ensure_directories()

    def _ensure_directories(self):
        """إنشاء المجلدات الضرورية إذا لم تكن موجودة"""
        dirs = [
            self.paths.logs_dir,
            self.paths.memory_dir,
            self.paths.backups_dir,
            self.paths.knowledge_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def validate(self) -> bool:
        """
        التحقق من صحة جميع الإعدادات الضرورية.

        يُرجع True إذا نجح التحقق.
        يُطلق ValueError عند وجود أخطاء.
        يُطلق UserWarning عند وجود تحذيرات (مثل المفاتيح الافتراضية).
        """
        errors = []

        # التحقق من مفاتيح API الرئيسية
        if not self.api.groq_key:
            errors.append("GROQ_API_KEY مطلوب ولم يُحدَّد في .env")

        if not self.api.gemini_key:
            errors.append("GEMINI_API_KEY مطلوب ولم يُحدَّد في .env")

        # التحقق من المجلدات
        if not self.paths.base_dir.exists():
            errors.append(f"BASE_DIR غير موجود: {self.paths.base_dir}")

        # تحذيرات (لا تُوقف التشغيل)
        if self.flask.secret_key == "change-me-in-production":
            import warnings
            warnings.warn(
                "⚠️ FLASK_SECRET_KEY يستخدم القيمة الافتراضية. يُرجى تغييرها في .env قبل النشر.",
                UserWarning,
                stacklevel=2,
            )

        if errors:
            raise ValueError(
                "أخطاء في إعدادات AgentOrchestra:\n" +
                "\n".join(f"  ❌ {e}" for e in errors)
            )

        return True

    @classmethod
    def from_env(cls) -> "Config":
        """تحميل الإعدادات من .env وإنشاء نسخة Config"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        return cls()

    def to_dict(self) -> dict:
        """تصدير الإعدادات لصيغة dict دون الأسرار (آمن للطباعة والـ Logging)"""
        return {
            "api": {
                "groq_model": self.api.groq_model,
                "groq_max_tokens": self.api.groq_max_tokens,
                "gemini_model": self.api.gemini_model,
                "gemini_pro_model": self.api.gemini_pro_model,
                "claude_model": self.api.claude_model,
                "has_groq": bool(self.api.groq_key),
                "has_gemini": bool(self.api.gemini_key),
                "has_anthropic": bool(self.api.anthropic_key),
                "has_github": bool(self.api.github_token),
                "has_telegram": bool(self.api.telegram_bot_token),
                "has_gmail": bool(self.api.gmail_address),
            },
            "paths": {
                "base_dir": str(self.paths.base_dir),
                "logs_dir": str(self.paths.logs_dir),
                "memory_dir": str(self.paths.memory_dir),
                "knowledge_dir": str(self.paths.knowledge_dir),
                "backups_dir": str(self.paths.backups_dir),
            },
            "execution": {
                "max_workers": self.execution.max_workers,
                "worker_timeout": self.execution.worker_timeout,
                "max_retries": self.execution.max_retries,
                "critic_max_rounds": self.execution.critic_max_rounds,
            },
            "flask": {
                "host": self.flask.host,
                "port": self.flask.port,
                "debug": self.flask.debug,
            },
            "logging": {
                "level": self.logging.level,
                "json_format": self.logging.json_format,
            },
        }

    def __repr__(self) -> str:
        return (
            f"Config(groq_model={self.api.groq_model!r}, "
            f"max_workers={self.execution.max_workers}, "
            f"flask={self.flask.host}:{self.flask.port})"
        )


# نسخة عامة للاستيراد المباشر (lazy-loaded)
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """استرجاع نسخة Config المشتركة (Singleton)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.from_env()
    return _config_instance
