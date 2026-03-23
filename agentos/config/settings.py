PROJECT_ID = "p001"
PROJECT_TYPE = "tiktok_video"

ENABLED_ROLES = [
    "coordinator_agent",
    "research_agent",
    "content_agent",
    "ops_agent",
    "data_agent",
]

WORKFLOW_SEQUENCE = [
    "research_agent",
    "content_agent",
    "ops_agent",
]

LOG_ENABLED = True

# =====================================
# Model Providers
# =====================================
SUPPORTED_PROVIDERS = [
    "deepseek",
    "gpt",
    "claude",
    "doubao",
    "qwen",
    "kimi",
    "hunyuan",
    "gemini",
    "custom_cn_1",
]

# =====================================
# Enable Switches
# 当前只启用 DeepSeek + Claude
# =====================================
ENABLE_DEEPSEEK = True
ENABLE_GPT = False
ENABLE_CLAUDE = False
ENABLE_DOUBAO = False
ENABLE_QWEN = False
ENABLE_KIMI = False
ENABLE_HUNYUAN = False
ENABLE_GEMINI = False
ENABLE_CUSTOM_CN_1 = False

DEFAULT_PROVIDER = "deepseek"

# =====================================
# API Keys
# 这里填你自己的，不要贴出来
# =====================================
DEEPSEEK_API_KEY = "sk-beb0478c12fc44989e38fd4234bca523"
GPT_API_KEY = ""
CLAUDE_API_KEY = "sk-1EtRec2OceWO85DGQGmmKWWkORuHsKh3M3nWLrn1Zz8FMtDD"
DOUBAO_API_KEY = ""
QWEN_API_KEY = ""
KIMI_API_KEY = ""
HUNYUAN_API_KEY = ""
GEMINI_API_KEY = ""
CUSTOM_CN_1_API_KEY = ""

# =====================================
# Base URLs
# =====================================
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
GPT_BASE_URL = "https://api.openai.com/v1"
CLAUDE_BASE_URL = "https://renrenai.chat"
DOUBAO_BASE_URL = ""
QWEN_BASE_URL = ""
KIMI_BASE_URL = ""
HUNYUAN_BASE_URL = ""
GEMINI_BASE_URL = "https://vip.yyds168.net/v1"
CUSTOM_CN_1_BASE_URL = ""

# =====================================
# Model Names
# =====================================
MODEL_NAME_MAP = {
    "deepseek": "deepseek-chat",
    "gpt": "gpt-5.4",
    "claude": "claude-sonnet-4-5-20250929",
    "doubao": "doubao-seed",
    "qwen": "qwen-max",
    "kimi": "kimi-k2.5",
    "hunyuan": "hunyuan-turbos-latest",
    "gemini": "gemini-3.0-pro",
    "custom_cn_1": "custom-model",
}

# =====================================
# Task -> Provider Chain
# 先按成本和质量来
# =====================================
FALLBACK_CHAINS = {
    "research": ["deepseek", "claude"],
    "content": ["claude", "deepseek"],
    "execution": ["claude", "deepseek"],
    "data": ["deepseek", "claude"],
    "default": ["deepseek", "claude"],
}

# =====================================
# Retry / Timeout
# =====================================
LLM_MAX_RETRIES = 2
LLM_TIMEOUT_SECONDS = 60

# =====================================
# Debug
# 可用于强制测试 fallback
# 例如填 "deepseek" 就会强制 deepseek 失败，切到 claude
# =====================================
DEBUG_FORCE_FAIL_PROVIDER = ""
