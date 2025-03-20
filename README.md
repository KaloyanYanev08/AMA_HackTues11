# AMA - Advanced Management Assistant

## Overview
AMA (Advanced Management Assistant) е уеб приложение, използващо Flask, което помага на потребителите да управляват седмичния си график и да постигат месечните си цели. Приложението работи с локално хостван AI модел, който дава предложения за поддържане на балансиран начин на живот.

## Функционалност
- **Потребителска Автентикация**: Регистрация и вход на потребители с помоща на сесии.
- **Управление на седмичен график**: Използва локално хостван AI модел за анализиране и оптимизиране на седмични графици въз основа на потребителските предпочитания.
- **Проследяване на месечни цели**
- **База данни**: Използва SQLite с SQLAlchemy за съхранение на потребителски данни, графици и цели.
- **Responsive уеб интерфейс**: Създаден с Tailwind CSS и DaisyUI за модерно и удобно за мобилни устройства потребителски интерфейс.

## Инсталация

### Изисквания
- Python 3.10+
- pip
- Ollama

### Стъпки за инсталация и стартиране
1. Клонирайте хранилището:
   ```bash
   git clone https://github.com/KaloyanYanev08/AMA_HackTues11.git
   cd AMA_HackTues11
   ```
2. Инсталирайте зависимостите:
   ```bash
   pip install -r requirements.txt
   ```
3. Изтеглете AI модела:
   ```bash
   ollama pull deepseek-r1:14b
   ```
4. Настройте конфигурацията в `config.py`:
   ```python
   ollama_model = "deepseek-r1:14b"
   ```
4. Стартирайте приложението:
   ```bash
   python main.py
   ```
5. Достъпете го на `http://127.0.0.1:5000`.

## Файлова структура
- `main.py`: Входна точка на приложението.
- `config.py`: Конфигурация за Flask, SQLAlchemy и Ollama.
- `models.py`: Модели на бази данни за потребители, дейности и цели.
- `routes.py`: Маршрути и логика на приложението.
- `helpers.py`: Помощни функции.
- `ai_client.py`: Управлява комуникацията с AI модела.
- `templates/`: HTML темплейти за уеб интерфейса.
- `static/`: Статични файлове като CSS и изображения.

## Използвани технологии
- Python
- Flask
- Ollama (default AI модел е deepseek-r1:14b)
- SQLite
- Tailwind CSS
- DaisyUI

## License
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.