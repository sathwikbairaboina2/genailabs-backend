from logging import getLogger
import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

logger = getLogger(__name__)

load_dotenv()

anthropic_key = os.getenv("ANTHROPIC_API_KEY")

if not anthropic_key:
    logger.warning(
        "ANTHROPIC_API_KEY is not set. Anthropic-related features will be disabled."
    )

llm = ChatAnthropic(
    model="claude-3-sonnet-20240229", temperature=0.7, anthropic_api_key=anthropic_key
)
