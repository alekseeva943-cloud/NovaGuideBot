# =========================================
# FILE: ai_service.py
# PATH: /NovaGuideBot/ai_service.py
#
# ОТВЕЧАЕТ ЗА:
# - работу с OpenAI API
# - загрузку prompt-файлов
# - чтение knowledge.txt
# - поиск релевантного контекста
# - генерацию AI-ответов
#
# ВАЖНО:
# Prompt-файлы вынесены отдельно
# в папку /prompts
#
# Это позволяет:
# - легко менять поведение AI
# - не смешивать prompts и код
# - удобно тестировать AI personality
# =========================================


import re
from dotenv import load_dotenv
load_dotenv()
from openai import AsyncOpenAI

# =========================================
# КОНСТАНТЫ
# =========================================

MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.7
MAX_PARAGRAPHS = 3  # ⚡ Уменьшил с 5 до 3 для скорости
KNOWLEDGE_FILE = "knowledge.txt"
SYSTEM_PROMPT_FILE = "prompts/system.txt"
NO_INFO_FILE = "prompts/no_info.txt"

# КЕШ ДЛЯ БАЗЫ
_cached_knowledge = None
_cached_paragraphs = None  # ⚡ КЕШ ДЛЯ АБЗАЦЕВ

client = AsyncOpenAI()

def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def load_knowledge_base() -> str:
    global _cached_knowledge
    if _cached_knowledge is None:
        _cached_knowledge = load_text_file(KNOWLEDGE_FILE)
        print(f"✅ База загружена: {len(_cached_knowledge)} символов")
    return _cached_knowledge

def get_paragraphs():
    """Кешируем абзацы, чтобы не разбивать каждый раз"""
    global _cached_paragraphs
    if _cached_paragraphs is None:
        knowledge = load_knowledge_base()
        _cached_paragraphs = [p.strip() for p in knowledge.split("\n\n") if p.strip()]
    return _cached_paragraphs

def build_context(question: str, knowledge_text: str) -> str:
    """Быстрый поиск по кешированным абзацам"""
    paragraphs = get_paragraphs()
    
    if not paragraphs:
        return ""
    
    # Очень быстрый поиск ключевых слов
    question_lower = question.lower()
    question_words = set(re.findall(r"\w+", question_lower))
    
    # Если вопрос очень короткий (2-3 слова) - ищем прямое совпадение
    if len(question_words) <= 3:
        for p in paragraphs[:50]:  # Проверяем первые 50 абзацев
            if any(word in p.lower() for word in question_words):
                return p
    
    # Обычный поиск с рейтингом
    scored = []
    for p in paragraphs:
        p_lower = p.lower()
        score = sum(1 for w in question_words if w in p_lower)
        if score > 0:
            scored.append((score, p))
    
    if not scored:
        return "\n\n".join(paragraphs[:MAX_PARAGRAPHS])
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join([p for _, p in scored[:MAX_PARAGRAPHS]])

def fix_typos_and_smart_answer(question: str, answer: str, user_name: str) -> str:
    """🔧 УМНЫЙ ПОСТОБРАБОТЧИК: исправляет глупые ответы бота"""
    
    # Словарь типичных ошибок и опечаток
    typo_map = {
        "организующий": "организация",
        "орг": "организация",
        "какой организующий": "какая организация",
        "ты кто такой": "ты кто",
    }
    
    # Если ответ "нет информации", но вопрос про организацию - даём умный ответ
    question_lower = question.lower()
    
    # Проверяем, не спросил ли пользователь про самого бота
    if any(word in question_lower for word in ["ты кто", "кто ты", "ты такой", "твоя роль"]):
        return f"""Привет, {user_name}! 👋

Я — AI-консультант этой организации. 

Моя задача — помогать тебе с вопросами на основе документов и базы знаний компании.

Спрашивай всё, что тебя интересует! 😊"""
    
    # Если вопрос про организацию, а бот тупит
    if any(word in question_lower for word in ["организ", "компания", "фирма", "какая организация"]):
        if "нет информации" in answer.lower() or "извините" in answer.lower():
            return f"""{user_name}, я — консультант организации, документы которой загружены в мою базу знаний.

Если ты хочешь узнать о самой организации — уточни, пожалуйста, что именно тебя интересует:
- Чем занимается компания?
- Какие услуги предоставляет?
- Контактные данные?

Я постараюсь найти ответ в документах! 📄"""
    
    # Исправляем опечатки в ответе
    for wrong, correct in typo_map.items():
        if wrong in answer.lower():
            answer = answer.replace(wrong, correct)
    
    return answer

async def generate_answer(question: str, user_name: str, user_language: str, user_style: str) -> str:
    system_prompt = load_text_file(SYSTEM_PROMPT_FILE)
    no_info_prompt = load_text_file(NO_INFO_FILE)
    knowledge_text = load_knowledge_base()
    context = build_context(question, knowledge_text)
    
    # 🤖 Улучшенный system prompt
    full_system_prompt = f"""
Ты — AI-консультант по техническому регламенту Таможенного союза "О безопасности железнодорожного подвижного состава" (ТР ТС 001/2011).

❗САМОЕ ГЛАВНОЕ ПРАВИЛО:
Если пользователь пишет "Ты кто?" или "Кто ты?" — ты ОБЯЗАН ответить ТОЛЬКО так:
"Я — консультант по техническому регламенту ТР ТС 001/2011 (Безопасность железнодорожного подвижного состава). Помогаю отвечать на вопросы о требованиях к поездам, вагонам, локомотивам и их сертификации."

Важные правила:
1. ВСЕГДА обращайся по имени: {user_name}
2. Отвечай на языке: {user_language}
3. Стиль: {user_style}
4. Если вопрос про тебя самого — расскажи о своей роли
5. Если пользователь сделал опечатку — догадайся, что он имел в виду
6. Не говори "нет информации" на общие вопросы о компании

{system_prompt}
"""
    
    user_prompt = f"""
Вопрос: {question}

Контекст из базы знаний:
{context if context else "Информация не найдена в базе"}

Ответь вежливо и по делу.
"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=500  # ⚡ Ограничим длину ответа для скорости
        )
        
        answer = response.choices[0].message.content
        
        # 🔧 Применяем умный постобработчик
        answer = fix_typos_and_smart_answer(question, answer, user_name)
        
        return answer if answer else no_info_prompt
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"{user_name}, извините, произошла ошибка. Попробуйте ещё раз 🙏"

async def translate_ui_text(text: str, language: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate to {language}. Preserve emojis. Keep formatting. Return ONLY translation."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    return response.choices[0].message.content