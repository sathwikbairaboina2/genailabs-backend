from app.assistant.prompts import (
    prompt_template_genaerator,
    intent_analysis_prompt,
    prompt_template_summarize,
    prompt_template_compare,
)
from app.core.langgrapgh import llm
from langchain_core.output_parsers import StrOutputParser

extract_intent_chain = intent_analysis_prompt | llm | StrOutputParser()
generatorLLMchain = prompt_template_genaerator | llm | StrOutputParser()
summarize_chain = prompt_template_summarize | llm | StrOutputParser()
compare_chain = prompt_template_compare | llm | StrOutputParser()
