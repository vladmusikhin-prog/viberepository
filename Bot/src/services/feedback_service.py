class FeedbackService:
    def __init__(self, user_repo) -> None:
        self.user_repo = user_repo

    def record_feedback(self, user_id: int, reaction: str) -> None:
        if reaction == "helpful":
            self.user_repo.increment_helpful(user_id)
