# import os
# from typing import List
# from langchain_anthropic import ChatAnthropic
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# # Optional: Load .env file
# from dotenv import load_dotenv

# load_dotenv()

# # Load key from environment
# anthropic_key = os.getenv("ANTHROPIC_API_KEY")

# if not anthropic_key:
#     raise EnvironmentError("ANTHROPIC_API_KEY is not set in environment variables.")

# # Initialize Claude model
# llm = ChatAnthropic(
#     model="claude-3-sonnet-20240229", temperature=0.7, anthropic_api_key=anthropic_key
# )

# # Prompt template
# prompt = ChatPromptTemplate.from_template(
#     """You are a linguistic expert in Scandinavian names. 
# The user provides a possibly incorrect or poorly transliterated full name and the country of origin.

# Input:
# Full Name: {full_name}
# Country: {country}

# Task:
# - Provide a list of 3-5 corrected or more likely variations of the full name, considering the naming conventions in the country.
# - Only return the list as a Python array of strings.

# Example Output:
# ["Nöke", "Nöik", "Naeik"]

# Now respond with the output array only."""
# )

# # Chain
# chain = prompt | llm | StrOutputParser()


# def suggest_names(full_name: str, country: str) -> List[str]:
#     output = chain.invoke({"full_name": full_name, "country": country})
#     try:
#         return eval(output.strip())
#     except Exception:
#         return [output.strip()]

