class AdminService:
    def __init__(
        self,
        user_repo,
        signal_repo,
        admin_user_ids: tuple[int, ...],
    ) -> None:
        self.user_repo = user_repo
        self.signal_repo = signal_repo
        self._admins = set(admin_user_ids)

    def is_admin(self, user_id: int) -> bool:
        if not self._admins:
            # Safe fallback for local MVP: if not configured, allow inspection.
            return True
        return user_id in self._admins

    def render_stats(self) -> str:
        users = self.user_repo.all_users()
        active = sum(1 for u in users if u.is_live_enabled)
        total_signals_counter = sum(u.signals_received for u in users)
        return (
            "🛠 Admin stats\n"
            f"👥 Total users: {len(users)}\n"
            f"🟢 Active subscriptions: {active}\n"
            f"📬 Delivered signals (guard): {self.signal_repo.delivered_count()}\n"
            f"🗂 Signal rows stored: {self.signal_repo.signal_count()}\n"
            f"📥 Signals counter sum (N): {total_signals_counter}"
        )
