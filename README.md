# 🎼 AgentOrchestra

> نظام وكيل ذكي هرمي متعدد المستويات للتطوير والأتمتة  
> Hierarchical Multi-Agent System for Development & Automation

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Phase](https://img.shields.io/badge/Phase-1%20Infrastructure-orange)]()

---

## 📋 نظرة عامة

**AgentOrchestra** نظام ذكاء اصطناعي هرمي يستقبل أي مهمة معقدة، يُحلّلها، يُخطّط لها، ثم يُنشئ وكلاء متخصصين ديناميكياً لتنفيذها، ويُتحقق من جودتها عبر وكيل ناقد.

```
المستخدم → المدير (Orchestrator) → الوكلاء الفرعيون (Workers) → الناقد (Critic) → النتيجة
```

---

## 🚀 البدء السريع

### 1. المتطلبات
- Python 3.10+
- Windows 10/11 (مُوصى به) أو Linux/macOS

### 2. تثبيت المكتبات

```bash
git clone https://github.com/bahoma31-jpg/Agent-Orchestra.git
cd Agent-Orchestra
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة

```bash
cp .env.example .env
# افتح .env وأضف مفاتيح API الخاصة بك
```

### 4. التحقق من الإعدادات

```bash
python main.py --check-config
```

المخرج المتوقع:
```
=======================================================
  AgentOrchestra v1.0.0  |  فحص الإعدادات
=======================================================
✅ جميع الإعدادات الأساسية صحيحة

📋 ملخص الإعدادات:
  ├─ نموذج Groq     : llama-3.3-70b-versatile
  ├─ نموذج Gemini   : gemini-2.0-flash
  ├─ Groq API Key   : ✅ موجود
  ...
```

### 5. تشغيل الاختبارات

```bash
pytest tests/infrastructure/ -v
```

---

## 📁 هيكل المشروع

```
agent_orchestra/
├── core/               # النواة الأساسية (config، orchestrator...)
├── agents/             # قوالب الوكلاء الديناميكيين
├── tools/              # الأدوات (بحث، كود، تواصل، أتمتة...)
├── memory/             # نظام الذاكرة متعدد الطبقات
├── knowledge/          # قاعدة المعرفة والقواعد
├── web/                # واجهة Flask + SocketIO
├── tests/              # الاختبارات (unit, integration, e2e)
├── scripts/            # سكربتات الصيانة والتثبيت
├── utils/              # أدوات مساعدة (logger...)
├── logs/               # السجلات (تُنشأ تلقائياً)
├── backups/            # النسخ الاحتياطية
├── .env.example        # مثال لمتغيرات البيئة
├── requirements.txt    # المكتبات المطلوبة
├── pytest.ini          # إعدادات الاختبارات
└── main.py             # نقطة الدخول الرئيسية
```

---

## ⚙️ المتطلبات الرئيسية (API Keys)

| الخدمة | الاستخدام | الإلزامية |
|--------|-----------|----------|
| **Groq** | Orchestrator + Worker Agents | ✅ إلزامي |
| **Google Gemini** | Critic Agent + Vision | ✅ إلزامي |
| **Anthropic Claude** | Critic Agent (بديل) | ⚠️ مُوصى |
| **GitHub Token** | أداة GitHub | ⚠️ مُوصى |
| **Telegram Bot** | الإشعارات | اختياري |
| **Gmail App Password** | إرسال الإيميلات | اختياري |

---

## 🗺️ خارطة التطوير

| المرحلة | الوصف | الحالة |
|---------|-------|--------|
| **1. Infrastructure** | هيكل المجلدات، Config، Logger | ✅ مكتملة |
| **2. Core Agents** | Orchestrator، Workers، Critic | 🔄 قادمة |
| **3. Memory System** | SQLite، RAG، Procedural Memory | ⏳ مخططة |
| **4. Flask UI** | Chat، Dashboard، SocketIO | ⏳ مخططة |
| **5. Testing & Security** | Unit، E2E، Input Sanitization | ⏳ مخططة |
| **6. Deployment** | NSSM Service، Notifications | ⏳ مخططة |

---

## 🧪 الاختبارات

```bash
# اختبارات البنية التحتية (المرحلة 1)
pytest tests/infrastructure/ -v

# جميع الاختبارات
pytest -v

# مع تقرير التغطية
pytest --cov=. --cov-report=html
```

---

## 📄 الترخيص

MIT License - للاستخدام الشخصي والتجاري.

---

*بُني بـ ❤️ لأتمتة كل شيء | AgentOrchestra v1.0.0*
