"""
Загрузка вопросов из JSON файлов специализаций.
Фильтр по уровню сложности + fallback + random shuffle.
"""
import json
import logging
import random
from pathlib import Path
from typing import List

from config.settings import settings
from .models import Question
from .enum import Difficulty

logger = logging.getLogger(__name__)


def load_questions_for_specialization(
    specialization: str,
    difficulty: Difficulty,
    user_id: int | None = None
) -> List[Question]:
    """
    Загружает вопросы для специализации/сложности.
    
    Args:
        specialization: Название специализации (oupds, aliment, и т.д.)
        difficulty: Уровень сложности
        user_id: ID пользователя для seed (optional)
    
    Returns:
        Список объектов Question
    """
    # Путь к JSON файлу
    json_path = settings.questions_dir / f"{specialization}.json"
    
    if not json_path.exists():
        logger.error(f"❌ Файл вопросов не найден: {json_path}")
        return []
    
    try:
        with json_path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except (json.JSONDecodeError, PermissionError) as e:
        logger.error(f"❌ Ошибка чтения JSON {specialization}: {e}")
        return []
    
    if not isinstance(raw_data, list):
        logger.error(f"❌ Неверный формат JSON {specialization}: ожидается список")
        return []
    
    # Парсинг вопросов
    questions = []
    for idx, item in enumerate(raw_data):
        try:
            opts = item.get("options", [])
            if not isinstance(opts, list) or len(opts) < 3:
                logger.warning(f"⚠️ Пропуск вопроса {specialization}:{idx} - недостаточно вариантов")
                continue
            
            # Парсинг правильных ответов (строка "1,3,4" -> set{1,3,4})
            correct_str = item.get("correct_answers", "")
            correct = set()
            for x in correct_str.split(","):
                x = x.strip()
                if x.isdigit():
                    correct.add(int(x))
            
            if not correct:
                logger.warning(f"⚠️ Пропуск вопроса {specialization}:{idx} - нет правильных ответов")
                continue
            
            q = Question(
                question=item["question"],
                options=opts,
                correct_answers=correct,
                difficulty=difficulty  # Все вопросы получают выбранную сложность
            )
            questions.append(q)
            
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"⚠️ Пропуск вопроса {specialization}:{idx}: {e}")
            continue
    
    if not questions:
        logger.error(f"❌ Не удалось загрузить вопросы для {specialization}")
        return []
    
    # Количество вопросов для данного уровня сложности
    target_count = settings.difficulty_questions.get(difficulty.value, 30)
    
    # Random shuffle с user_seed для честности
    if user_id:
        random.seed(user_id)
    random.shuffle(questions)
    random.seed()  # Сброс seed
    
    # Выбор нужного количества вопросов
    if len(questions) < target_count:
        logger.warning(
            f"⚠️ Мало вопросов {specialization}: {len(questions)} < {target_count}. "
            f"Используем все доступные."
        )
        selected = questions
    else:
        selected = questions[:target_count]
    
    logger.info(
        f"✅ Загружено {len(selected)} вопросов для {specialization} "
        f"({difficulty.value})"
    )
    
    return selected
