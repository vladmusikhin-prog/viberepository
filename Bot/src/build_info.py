from __future__ import annotations

import os

# Bump when onboarding/delivery behavior changes materially (for support checks).
FEATURE_TAG = "multi_category_v1"


def get_build_id() -> str:
    for key in ("RAILWAY_GIT_COMMIT_SHA", "GIT_COMMIT", "BUILD_SHA"):
        value = (os.getenv(key) or "").strip()
        if value:
            return value[:7]
    return "local"
