"""
tests/infrastructure/test_config.py
اختبارات البنية التحتية الشاملة لـ AgentOrchestra

تشمل:
    - TestDirectoryStructure : التحقق من هيكل المجلدات و __init__.py
    - TestConfig             : اختبار نظام الإعدادات المركزي
    - TestLogger             : اختبار نظام التسجيل الموحّد
    - TestEnvExample         : التحقق من اكتمال .env.example

تشغيل:
    pytest tests/infrastructure/ -v
"""

import os
import sys
import json
import logging
import pytest
from pathlib import Path

# إضافة جذر المشروع لمسار البحث
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))


# ─── اختبارات هيكل المجلدات ───────────────────────────────────────────────

class TestDirectoryStructure:
    """التحقق من وجود جميع المجلدات والملفات الضرورية"""

    REQUIRED_DIRS = [
        "core", "agents", "agents/templates",
        "tools", "tools/search", "tools/code",
        "tools/communication", "tools/automation",
        "tools/visual", "tools/data",
        "memory", "knowledge",
        "web", "web/routes", "web/templates",
        "web/static/css", "web/static/js", "web/static/images",
        "logs", "backups",
        "tests", "tests/infrastructure", "tests/unit", "tests/e2e",
        "scripts", "utils",
    ]

    REQUIRED_INIT_FILES = [
        "core/__init__.py", "agents/__init__.py",
        "agents/templates/__init__.py", "tools/__init__.py",
        "tools/search/__init__.py", "tools/code/__init__.py",
        "tools/communication/__init__.py", "tools/automation/__init__.py",
        "tools/visual/__init__.py", "tools/data/__init__.py",
        "memory/__init__.py", "web/__init__.py",
        "web/routes/__init__.py",
        "tests/__init__.py", "tests/infrastructure/__init__.py",
        "tests/unit/__init__.py", "tests/e2e/__init__.py",
        "scripts/__init__.py", "utils/__init__.py",
    ]

    REQUIRED_FILES = [
        "core/config.py", "utils/logger.py",
        "main.py", "requirements.txt",
        ".env.example", ".gitignore",
        "pytest.ini", "README.md",
    ]

    def test_directory_structure_exists(self):
        """التحقق من وجود جميع المجلدات المطلوبة"""
        missing = []
        for d in self.REQUIRED_DIRS:
            if not (ROOT_DIR / d).is_dir():
                missing.append(d)
        assert not missing, "مجلدات مفقودة:\n" + "\n".join(f"  - {d}" for d in missing)

    def test_init_files_exist(self):
        """التحقق من وجود __init__.py في كل حزمة Python"""
        missing = []
        for f in self.REQUIRED_INIT_FILES:
            if not (ROOT_DIR / f).is_file():
                missing.append(f)
        assert not missing, "ملفات __init__.py مفقودة:\n" + "\n".join(f"  - {f}" for f in missing)

    def test_required_files_exist(self):
        """التحقق من وجود الملفات الأساسية"""
        missing = []
        for f in self.REQUIRED_FILES:
            if not (ROOT_DIR / f).is_file():
                missing.append(f)
        assert not missing, "ملفات أساسية مفقودة:\n" + "\n".join(f"  - {f}" for f in missing)


# ─── اختبارات الإعدادات ────────────────────────────────────────────────────

class TestConfig:
    """اختبار نظام الإعدادات المركزي"""

    def test_config_imports_successfully(self):
        """التحقق من استيراد Config بدون أخطاء"""
        from core.config import Config
        assert Config is not None

    def test_config_loads_successfully(self):
        """التحقق من تحميل Config.from_env() بنجاح"""
        from core.config import Config
        config = Config.from_env()
        assert config is not None
        assert config.api is not None
        assert config.paths is not None
        assert config.execution is not None
        assert config.flask is not None
        assert config.logging is not None

    def test_config_has_required_attributes(self):
        """التحقق من وجود جميع الخصائص المطلوبة"""
        from core.config import Config
        config = Config.from_env()

        # API
        for attr in ["groq_key", "groq_model", "groq_max_tokens", "groq_timeout",
                     "gemini_key", "gemini_model", "anthropic_key",
                     "github_token", "telegram_bot_token"]:
            assert hasattr(config.api, attr), f"APIConfig مفقود: {attr}"

        # Paths
        for attr in ["base_dir", "logs_dir", "memory_dir", "knowledge_dir", "backups_dir"]:
            assert hasattr(config.paths, attr), f"PathsConfig مفقود: {attr}"

        # Execution
        for attr in ["max_workers", "worker_timeout", "max_retries", "critic_max_rounds"]:
            assert hasattr(config.execution, attr), f"ExecutionConfig مفقود: {attr}"

    def test_config_default_values(self):
        """التحقق من القيم الافتراضية الآمنة"""
        from core.config import Config
        config = Config.from_env()
        assert config.api.groq_model == "llama-3.3-70b-versatile"
        assert config.api.gemini_model == "gemini-2.0-flash"
        assert config.execution.max_workers == 7
        assert config.execution.max_retries == 3
        assert config.execution.critic_max_rounds == 5
        assert config.flask.port == 5000

    def test_config_paths_are_path_objects(self):
        """التحقق من أن المسارات من نوع Path"""
        from core.config import Config
        config = Config.from_env()
        assert isinstance(config.paths.base_dir, Path)
        assert isinstance(config.paths.logs_dir, Path)
        assert isinstance(config.paths.memory_dir, Path)

    def test_config_to_dict_no_secrets(self):
        """التحقق من تصدير الإعدادات دون الأسرار"""
        from core.config import Config
        config = Config.from_env()
        d = config.to_dict()
        assert isinstance(d, dict)
        assert "api" in d
        assert "paths" in d
        assert "execution" in d
        # التأكد أن المفاتيح الحساسة غير موجودة
        assert "groq_key" not in d["api"]
        assert "gemini_key" not in d["api"]
        assert "anthropic_key" not in d["api"]
        # التأكد من وجود مؤشرات الحالة فقط
        assert "has_groq" in d["api"]
        assert "has_gemini" in d["api"]

    def test_config_directories_created(self):
        """التحقق من إنشاء المجلدات الضرورية تلقائياً"""
        from core.config import Config
        config = Config.from_env()
        assert config.paths.logs_dir.exists()
        assert config.paths.memory_dir.exists()
        assert config.paths.backups_dir.exists()

    def test_get_config_singleton(self):
        """التحقق من أن get_config() يُرجع نفس النسخة (Singleton)"""
        from core.config import get_config
        c1 = get_config()
        c2 = get_config()
        assert c1 is c2


# ─── اختبارات Logger ───────────────────────────────────────────────────────

class TestLogger:
    """اختبار نظام التسجيل الموحّد"""

    def test_logger_imports_successfully(self):
        """التحقق من استيراد setup_logger بدون أخطاء"""
        from utils.logger import setup_logger, get_logger
        assert setup_logger is not None
        assert get_logger is not None

    def test_logger_writes_to_file(self, tmp_path):
        """التحقق من كتابة Logger في ملف - معيار القبول الرئيسي"""
        from utils.logger import setup_logger
        log_dir = tmp_path / "test_logs"
        log_dir.mkdir()

        logger = setup_logger("test_write_infra", logs_dir=log_dir)
        test_message = "اختبار كتابة السجل في ملف"
        logger.info(test_message)

        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0, "لم يُنشأ أي ملف سجل"

        content = log_files[0].read_text(encoding="utf-8")
        assert test_message in content, f"الرسالة غير موجودة في السجل: {content[:200]}"

    def test_logger_levels_are_respected(self, tmp_path):
        """التحقق من أن مستويات Logging تعمل بشكل صحيح"""
        from utils.logger import setup_logger
        log_dir = tmp_path / "level_logs"
        log_dir.mkdir()

        logger = setup_logger("test_level_infra", level=logging.DEBUG, logs_dir=log_dir)
        assert logger.level == logging.DEBUG

    def test_logger_returns_same_instance(self, tmp_path):
        """التحقق من Singleton pattern للـ Logger"""
        from utils.logger import setup_logger
        log_dir = tmp_path / "singleton_logs"
        log_dir.mkdir()

        logger1 = setup_logger("singleton_test_infra", logs_dir=log_dir)
        logger2 = setup_logger("singleton_test_infra", logs_dir=log_dir)
        assert logger1 is logger2

    def test_logger_json_format(self, tmp_path):
        """التحقق من تنسيق JSON للسجلات البنيوية"""
        from utils.logger import setup_logger
        log_dir = tmp_path / "json_logs"
        log_dir.mkdir()

        logger = setup_logger("test_json_infra", logs_dir=log_dir, json_format=True)
        logger.info("رسالة JSON اختبارية")

        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0

        first_line = log_files[0].read_text(encoding="utf-8").strip().split("\n")[0]
        parsed = json.loads(first_line)
        assert "message" in parsed
        assert "timestamp" in parsed
        assert "level" in parsed
        assert parsed["level"] == "INFO"

    def test_error_log_created(self, tmp_path):
        """التحقق من إنشاء ملف سجل الأخطاء المستقل"""
        from utils.logger import setup_logger
        log_dir = tmp_path / "error_logs"
        log_dir.mkdir()

        logger = setup_logger("test_error_infra", logs_dir=log_dir)
        logger.error("خطأ اختباري")

        error_log = log_dir / "errors.log"
        assert error_log.exists(), "ملف errors.log غير موجود"
        content = error_log.read_text(encoding="utf-8")
        assert "خطأ اختباري" in content


# ─── اختبار .env.example ──────────────────────────────────────────────────

class TestEnvExample:
    """التحقق من اكتمال ملف .env.example"""

    REQUIRED_VARS = [
        "GROQ_API_KEY", "GROQ_MODEL", "GROQ_MAX_TOKENS",
        "GEMINI_API_KEY", "GEMINI_MODEL",
        "ANTHROPIC_API_KEY", "CLAUDE_MODEL",
        "GITHUB_TOKEN",
        "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
        "GMAIL_ADDRESS", "GMAIL_APP_PASSWORD",
        "FLASK_SECRET_KEY", "FLASK_PORT",
        "LOG_LEVEL", "MAX_WORKERS", "WORKER_TIMEOUT",
    ]

    def test_env_example_exists(self):
        """التحقق من وجود .env.example"""
        assert (ROOT_DIR / ".env.example").exists(), ".env.example غير موجود"

    def test_env_example_contains_required_vars(self):
        """التحقق من وجود جميع المتغيرات في .env.example"""
        content = (ROOT_DIR / ".env.example").read_text(encoding="utf-8")
        missing = [v for v in self.REQUIRED_VARS if v not in content]
        assert not missing, f"متغيرات مفقودة من .env.example: {missing}"

    def test_env_example_no_real_secrets(self):
        """التحقق من عدم وجود مفاتيح حقيقية في .env.example"""
        content = (ROOT_DIR / ".env.example").read_text(encoding="utf-8")
        # التأكد أن القيم تبدأ بـ your_ أو فارغة
        import re
        # البحث عن أي قيمة تبدو حقيقية (تسلسل حروف وأرقام طويل بعد =)
        suspicious = re.findall(
            r'^(?:GROQ|GEMINI|ANTHROPIC|GITHUB|TELEGRAM|GMAIL)_\w+=([^#\n]+)',
            content, re.MULTILINE
        )
        for val in suspicious:
            val = val.strip()
            if val and not val.startswith("your_") and len(val) > 30:
                pytest.fail(f".env.example يحتوي على قيمة مشبوهة: {val[:20]}...")
