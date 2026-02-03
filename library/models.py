"""
Модели для тестов: Pydantic v2, 4 уровня сложности.
Question: из JSON (difficulty optional → BASIC).
CurrentTestState: toggle-ответы, таймер, результаты, история ответов.
"""
import time
from typing import List, Set, Optional, Dict
from pydantic import BaseModel, Field, field_validator

from .enum import Difficulty


class Question(BaseModel):
    """Вопрос из библиотеки."""
    question: str = Field(..., min_length=1, max_length=2000)
    options: List[str] = Field(..., min_length=3, max_length=6)
    correct_answers: Set[int] = Field(..., min_length=1)
    difficulty: Difficulty = Difficulty.BASIC  # Default для JSON без поля

    @field_validator('correct_answers', mode='after')
    @classmethod
    def validate_correct(cls, v, info):
        """Валидация правильных ответов (1-based индексы)."""
        options = info.data.get('options', [])
        max_opt = len(options)
        if any(i < 1 or i > max_opt for i in v):
            raise ValueError(f'correct_answers: индексы должны быть в диапазоне 1..{max_opt}')
        return v


class CurrentTestState(BaseModel):
    """Состояние текущего теста с полной историей."""
    questions: List[Question]
    current_index: int = 0
    selected_answers: Set[int] = Field(default_factory=set)
    answers_history: Dict[int, Set[int]] = Field(default_factory=dict)  # {question_idx: {selected}}
    start_time: float = Field(default_factory=time.time)
    timer_task: Optional[object] = None  # asyncio.Task
    
    # Данные пользователя
    full_name: str = ""
    position: str = ""
    department: str = ""
    specialization: str = ""
    difficulty: Difficulty = Difficulty.BASIC
    
    # Результаты
    correct_count: int = 0
    total_questions: int = 0
    percentage: float = 0.0
    grade: str = ""
    elapsed_time: str = ""
    
    model_config = {"arbitrary_types_allowed": True}  # Для asyncio.Task

    @field_validator('current_index', mode='after')
    @classmethod
    def validate_index(cls, v, info):
        """Валидация индекса текущего вопроса."""
        questions = info.data.get('questions', [])
        if questions and v >= len(questions):
            raise ValueError(f'current_index {v} выходит за пределы вопросов ({len(questions)})')
        return v
    
    def save_current_answer(self):
        """Сохранить текущий выбранный ответ в историю."""
        self.answers_history[self.current_index] = self.selected_answers.copy()
    
    def load_answer(self, question_index: int):
        """Загрузить ранее выбранный ответ из истории."""
        self.selected_answers = self.answers_history.get(question_index, set()).copy()
    
    def calculate_results(self):
        """Подсчет результатов теста."""
        self.total_questions = len(self.questions)
        self.correct_count = 0
        
        for idx, question in enumerate(self.questions):
            user_answer = self.answers_history.get(idx, set())
            if user_answer == question.correct_answers:
                self.correct_count += 1
        
        self.percentage = (self.correct_count / self.total_questions * 100) if self.total_questions > 0 else 0.0
        
        # Определение оценки
        if self.percentage >= 80:
            self.grade = "отлично"
        elif self.percentage >= 70:
            self.grade = "хорошо"
        elif self.percentage >= 60:
            self.grade = "удовлетворительно"
        else:
            self.grade = "неудовлетворительно"
        
        # Расчет времени
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.elapsed_time = f"{minutes:02d}:{seconds:02d}"
