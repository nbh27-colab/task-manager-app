from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI  # Đã cập nhật theo cảnh báo
import os
from dotenv import load_dotenv

load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Khởi tạo LLM
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

# Prompt cho phân loại
category_prompt = PromptTemplate(
    input_variables=["task_description"],
    template="Dựa trên mô tả sau, hãy phân loại tác vụ vào một trong các danh mục: Tài chính, Kỹ thuật, Nhân sự, Cá nhân, Khác.\n\nMô tả: {task_description}\n\nDanh mục:"
)

# Prompt cho ước lượng thời gian
time_prompt = PromptTemplate(
    input_variables=["task_description"],
    template="Dựa trên mô tả sau, hãy ước lượng thời gian cần thiết để hoàn thành tác vụ (theo phút):\n\nMô tả: {task_description}\n\nThời gian ước lượng (phút):"
)

# Chain phân loại tác vụ
category_chain = category_prompt | llm
time_chain = time_prompt | llm


def classify_task(description: str) -> str:
    result = category_chain.invoke({"task_description": description})
    return result.strip() if isinstance(result, str) else str(result)


def estimate_time(description: str) -> str:
    result = time_chain.invoke({"task_description": description})
    return result.strip() if isinstance(result, str) else str(result)
