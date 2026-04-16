class SettingsService:
    def __init__(self, user_repo) -> None:
        self.user_repo = user_repo

    def render_settings(self, user_id: int) -> str:
        user = self.user_repo.get_or_create(user_id)
        categories = ", ".join(user.categories) if user.categories else "Не выбраны"
        live_status = "🟢 Включены" if user.is_live_enabled else "🔴 Выключены"
        return (
            "⚙️ Настройки\n"
            f"🎯 Категории: {categories}\n"
            f"🔔 Статус сигналов: {live_status}\n\n"
            "📊 Твоя статистика\n"
            f"📥 Получено сигналов: {user.signals_received}\n"
            f"👍 Отмечено полезными: {user.helpful_count}"
        )
