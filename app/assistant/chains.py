from app.assistant.prompts import prompt_template_qa, intent_analysis_prompt
from app.core.langgrapgh import llm
from langchain_core.output_parsers import StrOutputParser

extract_intent_chain = intent_analysis_prompt | llm | StrOutputParser()
generatorLLMchain = prompt_template_qa | llm | StrOutputParser()
