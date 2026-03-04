"""
main.py - نقطة الدخول الرئيسية لـ AgentOrchestra
Main Entry Point for the AgentOrchestra System.

الاستخدام:
    python main.py                  # تشغيل النظام الكامل
    python main.py --check-config   # التحقق من الإعدادات
    python main.py --version        # عرض الإصدار
    python main.py --log-level DEBUG # تشغيل مع debug logging
"""

import sys
import argparse
import warnings
from pathlib import Path

# إضافة الجذر لمسار البحث
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from utils.logger import setup_logger

# إعداد اللوغر الرئيسي
logger = setup_logger("main", logs_dir=ROOT_DIR / "logs")

VERSION = "1.0.0"
APP_NAME = "AgentOrchestra"


def check_config() -> bool:
    """
    التحقق من صحة الإعدادات وطباعة تقرير واضح.

    Returns:
        bool: True إذا نجح التحقق من الإعدادات الأساسية
    """
    try:
        from core.config import Config

        print(f"\n{'='*55}")
        print(f"  {APP_NAME} v{VERSION}  |  فحص الإعدادات")
        print(f"{'='*55}")

        config = Config.from_env()

        # محاولة التحقق الكامل
        warnings.filterwarnings("always", category=UserWarning)
        validation_ok = False
        try:
            config.validate()
            validation_ok = True
            print("✅ جميع الإعدادات الأساسية صحيحة")
        except UserWarning as w:
            print(f"⚠️  تحذير: {w}")
            validation_ok = True  # تحذير لا يُوقف التشغيل
        except ValueError as e:
            print(f"❌ أخطاء في الإعدادات:\n{e}")
            validation_ok = False

        # طباعة الملخص دائماً
        d = config.to_dict()
        print(f"\n📋 ملخص الإعدادات:")
        print(f"  ├─ نموذج Groq     : {d['api']['groq_model']}")
        print(f"  ├─ نموذج Gemini   : {d['api']['gemini_model']}")
        print(f"  ├─ Groq API Key   : {'✅ موجود' if d['api']['has_groq'] else '❌ مفقود'}")
        print(f"  ├─ Gemini API Key : {'✅ موجود' if d['api']['has_gemini'] else '❌ مفقود'}")
        print(f"  ├─ GitHub Token   : {'✅ موجود' if d['api']['has_github'] else '⚠️  غير محدد'}")
        print(f"  ├─ Telegram Bot   : {'✅ موجود' if d['api']['has_telegram'] else '⚠️  غير محدد'}")
        print(f"  ├─ Workers        : {d['execution']['max_workers']} وكلاء متزامنون")
        print(f"  ├─ Worker Timeout : {d['execution']['worker_timeout']}s ({d['execution']['worker_timeout']//60} دقيقة)")
        print(f"  ├─ Flask Server   : http://{d['flask']['host']}:{d['flask']['port']}")
        print(f"  └─ Logs Dir       : {d['paths']['logs_dir']}")
        print(f"{'='*55}\n")

        if validation_ok:
            logger.info(f"✅ Config check passed | {APP_NAME} v{VERSION}")
        return validation_ok

    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        print("   تأكد من تثبيت المكتبات: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        logger.error(f"Config check failed: {e}", exc_info=True)
        return False


def run_app():
    """
    تشغيل النظام الكامل.
    في المرحلة الحالية يتحقق من الإعدادات ويُظهر رسالة الجاهزية.
    Flask + Orchestrator سيُضافان في المرحلة 2.
    """
    logger.info("=" * 55)
    logger.info(f"  بدء تشغيل {APP_NAME} v{VERSION}")
    logger.info("=" * 55)

    if not check_config():
        logger.error("فشل التحقق من الإعدادات. أوقف التشغيل.")
        sys.exit(1)

    print(f"🚀 {APP_NAME} جاهز للتشغيل!")
    print("   المرحلة القادمة: بناء Orchestrator + Flask UI")
    logger.info("Infrastructure phase complete. Ready for Phase 2: Orchestrator + Flask.")


def main():
    """نقطة الدخول الرئيسية مع تحليل المعاملات من سطر الأوامر"""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - نظام وكيل ذكي هرمي متعدد المستويات",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  python main.py                  تشغيل النظام
  python main.py --check-config   فحص الإعدادات فقط
  python main.py --version        عرض الإصدار
  python main.py --log-level DEBUG تشغيل مع تسجيل تفصيلي
        """,
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="التحقق من صحة الإعدادات والخروج",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} v{VERSION}",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="مستوى التسجيل (افتراضي: INFO)",
    )

    args = parser.parse_args()

    if args.check_config:
        success = check_config()
        sys.exit(0 if success else 1)

    run_app()


if __name__ == "__main__":
    main()
