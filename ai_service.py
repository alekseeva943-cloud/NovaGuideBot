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
MAX_PARAGRAPHS = 3
KNOWLEDGE_FILE = "knowledge.txt"
SYSTEM_PROMPT_FILE = "prompts/system.txt"
NO_INFO_FILE = "prompts/no_info.txt"

# КЕШ ДЛЯ БАЗЫ
_cached_knowledge = None
_cached_paragraphs = None

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
    
    question_lower = question.lower()
    question_words = set(re.findall(r"\w+", question_lower))
    
    if len(question_words) <= 3:
        for p in paragraphs[:50]:
            if any(word in p.lower() for word in question_words):
                return p
    
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
    """Исправляет типичные опечатки, НЕ перебивает ответы GPT"""
    
    # Словарь типичных ошибок и опечаток
    typo_map = {
        "нмап": "Nmap",
        "метасплоит": "Metasploit",
        "виршарк": "Wireshark",
        "джон риппер": "John the Ripper",
        "гидра": "Hydra",
        "сикл инъекция": "SQL-инъекция",
        "иксэсэс": "XSS",
        "сирф": "CSRF",
    }
    
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
    
    # 🤖 System prompt — НЕ просим здороваться при каждом ответе
    full_system_prompt = f"""
{system_prompt}

ДОПОЛНИТЕЛЬНЫЕ ПРАВИЛА:
1. Обращайся к пользователю по имени, когда это уместно: {user_name}
2. Отвечай на языке: {user_language}
3. Стиль общения: {user_style}
4. НЕ здоровайся при каждом ответе. Здоровайся ТОЛЬКО в первом сообщении диалога.
5. Если пользователь сделал опечатку — догадайся, что он имел в виду.
"""
    
    user_prompt = f"""
Вопрос: {question}

Контекст из базы знаний:
{context if context else "Информация не найдена в базе"}

Ответь вежливо и по делу, без лишних приветствий.
"""
    
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
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