# agentos_mvp/core/settings.py

# 项目ID和类型配置
PROJECT_ID = "p001"
PROJECT_TYPE = "tiktok_video"

# 启用的角色
ENABLED_ROLES = [
    "coordinator_agent",
    "research_agent",
    "content_agent",
    "ops_agent",
    "data_agent",
]

# 模型提供者配置
MODEL_CONFIG = {
    "deepseek": {
        "api_url": "https://api.deepseek.com/anthropic",  # 使用 DeepSeek 的 Anthropic API
        "headers": {"Authorization": "Bearer sk-beb0478c12fc44989e38fd4234bca523"}  # 填写您的 DeepSeek API 密钥
    },
    "gpt": {
        "api_url": "https://api.openai.com/v1/completions",
        "headers": {"Authorization": "Bearer YOUR_GPT_API_KEY"}
    },
    "claude": {
        "api_url": "https://renrenai.chat/v1/messages",
        "headers": {"Authorization": "Bearer sk-1EtRec2OceWO85DGQGmmKWWkORuHsKh3M3nWLrn1Zz8FMtDD"}
    },
    "doubao": {
        "api_url": "https://doubao-api.com/generate",
        "headers": {"Authorization": "Bearer YOUR_DOUBAO_API_KEY"}
    },
    "qwen": {
        "api_url": "https://qwen-api.com/generate",
        "headers": {"Authorization": "Bearer YOUR_QWEN_API_KEY"}
    },
    "kimi": {
        "api_url": "https://kimi-api.com/generate",
        "headers": {"Authorization": "Bearer YOUR_KIMI_API_KEY"}
    },
    "hunyuan": {
        "api_url": "https://hunyuan-api.com/generate",
        "headers": {"Authorization": "Bearer YOUR_HUNYUAN_API_KEY"}
    },
    "gemini": {
        "api_url": "https://gemini-api.com/generate",
        "headers": {"Authorization": "Bearer YOUR_GEMINI_API_KEY"}
    },
    "custom_cn_1": {
        "api_url": "https://custom-api.com/generate",
        "headers": {"Authorization": "Bearer YOUR_CUSTOM_CN_1_API_KEY"}
    },
}

# 启用的模型提供者
ENABLE_DEEPSEEK = True
ENABLE_GPT = False
ENABLE_CLAUDE = True
ENABLE_DOUBAO = False
ENABLE_QWEN = False
ENABLE_KIMI = False
ENABLE_HUNYUAN = False
ENABLE_GEMINI = False
ENABLE_CUSTOM_CN_1 = False

# 默认使用的模型
DEFAULT_PROVIDER = "deepseek"

# 模型映射
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

# 任务到模型的链路配置
FALLBACK_CHAINS = {
    "research": ["deepseek", "claude"],
    "content": ["claude", "deepseek"],
    "execution": ["claude", "deepseek"],
    "data": ["deepseek", "claude"],
    "default": ["deepseek", "claude"],
}

# 重试和超时配置
LLM_MAX_RETRIES = 2
LLM_TIMEOUT_SECONDS = 60

# Debug选项，强制失败某个模型
DEBUG_FORCE_FAIL_PROVIDER = ""
