"""
AgentOrchestra - حزمة الذاكرة
Memory Package: multi-layer memory system.

طبقات الذاكرة:
    - Episodic  : global_memory.db + project_memory.db
    - Procedural: procedural_memory.db (دروس مستفادة)
    - Semantic  : knowledge_base.md (قواعد ثابتة)
    - Working   : في الـ runtime فقط (آخر 20 رسالة)

المكونات المستقبلية (تُضاف في المرحلة 3):
    - memory_manager.py : إدارة الذاكرة
    - rag_engine.py     : استرجاع بالكلمات المفتاحية
    - procedural_memory.py: دروس مستفادة
"""
