"""
Генерация PDF сертификатов о прохождении теста.
Production-ready с ReportLab и поддержкой русских шрифтов.
"""
import logging
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config.settings import settings
from .models import CurrentTestState

logger = logging.getLogger(__name__)


def register_fonts():
    """Регистрация русских шрифтов для PDF."""
    try:
        pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        logger.info("✅ Шрифты DejaVu загружены")
        return 'DejaVu', 'DejaVu-Bold'
    except:
        logger.warning("⚠️ Русские шрифты не найдены, используется Helvetica")
        return 'Helvetica', 'Helvetica-Bold'


async def generate_certificate(test_state: CurrentTestState, user_id: int) -> Path:
    """Генерирует PDF сертификат."""
    settings.certs_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = settings.certs_dir / f"cert_{user_id}_{timestamp}.pdf"
    
    font_regular, font_bold = register_fonts()
    
    c = canvas.Canvas(str(filename), pagesize=A4)
    width, height = A4
    
    # Заголовок
    c.setFont(font_bold, 24)
    c.setFillColor(colors.HexColor("#1a5490"))
    c.drawCentredString(width / 2, height - 100, "СЕРТИФИКАТ")
    
    c.setFont(font_regular, 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 130, "о прохождении тестирования")
    
    # Данные
    y_position = height - 200
    c.setFont(font_bold, 12)
    
    data_fields = [
        ("ФИО:", test_state.full_name),
        ("Должность:", test_state.position),
        ("Подразделение:", test_state.department),
        ("Специализация:", test_state.specialization.upper()),
        ("Уровень сложности:", test_state.difficulty.value.capitalize()),
        ("", ""),
        ("Оценка:", test_state.grade.upper()),
        ("Правильных ответов:", f"{test_state.correct_count} из {test_state.total_questions}"),
        ("Процент:", f"{test_state.percentage:.1f}%"),
        ("Время:", test_state.elapsed_time),
        ("Дата:", datetime.now().strftime("%d.%m.%Y")),
    ]
    
    for label, value in data_fields:
        if label:
            c.setFont(font_bold, 11)
            c.drawString(100, y_position, label)
            c.setFont(font_regular, 11)
            c.drawString(280, y_position, value)
        y_position -= 25
    
    c.setFont(font_regular, 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 50, f"Telegram Bot • ID: {user_id}")
    
    c.save()
    logger.info(f"✅ Сертификат: {filename}")
    return filename
