import os

LLM_MODEL_NAME="gemini-3.1-flash-lite"
TAVILY_MAX_RESULTS=4
TAVILY_SEARCH_SEPTH="advanced"
CRM_RETRY_ATTEMPT_LIMIT = 3

AUTO_TRIGGER_SEVERITIES = {"error", "critical"}   # severities that will automatically trigger the sentry loop api
COOLDOWN_MINUTES = 20  # no repeat trigger for the same error in 20 minutes window
SENTRYLOOP_INTERNAL_INVOKE_URL = "https://sentryloop-backend.vercel.app/internal/investigate"
MAX_TRIGGERS_PER_HOUR = 20
SKIP_AUTO_TRIGGER_FOR = {"sentryloop"}
INTERNAL_TRIGGER_SECRET = os.getenv("INTERNAL_TRIGGER_SECRET")