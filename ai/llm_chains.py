from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional, List, Dict, Any

from core.config import settings # Import settings to get AI_MODEL_NAME and OPENAI_API_KEY
from api.schemas.ai import TaskSuggestionResponse # Import the schema for output parsing
from dotenv import load_dotenv
load_dotenv()

# 1. Initialize the LLM
# We use ChatOpenAI, which is compatible with many OpenAI-like APIs (e.g., local models, other providers)
# It automatically picks up OPENAI_API_KEY from environment variables or settings.
llm = ChatOpenAI(model=settings.ai_model_name, temperature=0.7) # Adjust temperature for creativity/consistency

# 2. Define the Pydantic Output Parser
# This parser will ensure the LLM's output conforms to our TaskSuggestionResponse schema
parser = PydanticOutputParser(pydantic_object=TaskSuggestionResponse)

# 3. Define the Prompt Template
# This prompt guides the LLM on its role, the input it will receive, and the desired output format.
task_suggestion_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Bạn là một trợ lý AI thông minh chuyên về quản lý tác vụ. "
            "Nhiệm vụ của bạn là phân tích tiêu đề và mô tả của một tác vụ mới, "
            "sau đó đưa ra các gợi ý về danh mục, dự án, thẻ, mức độ ưu tiên, "
            "điểm khẩn cấp và điểm tầm quan trọng. "
            "Bạn cũng sẽ nhận được ngữ cảnh từ các tác vụ tương tự mà người dùng đã thực hiện trước đây. "
            "Hãy sử dụng ngữ cảnh này để đưa ra các gợi ý phù hợp nhất. "
            "Nếu bạn không thể gợi ý một thuộc tính cụ thể, hãy trả về giá trị null cho thuộc tính đó. "
            "Độ khẩn cấp và tầm quan trọng nên được đánh giá từ 0.0 đến 1.0. "
            "Mức độ ưu tiên từ 1 (cao nhất) đến 10 (thấp nhất). "
            "Trả lời bằng tiếng Việt và chỉ trả về một đối tượng JSON tuân thủ schema sau:\n{format_instructions}"
        ),
        (
            "human",
            "Tiêu đề tác vụ mới: {title}\n"
            "Mô tả tác vụ mới: {description}\n"
            "Các tác vụ tương tự đã hoàn thành của người dùng (để tham khảo ngữ cảnh):\n{similar_tasks_context}\n\n"
            "Danh sách các ID danh mục hiện có của người dùng (để gợi ý category_id và project_id chính xác):\n{available_categories_projects_context}\n\n"
            "Hãy đưa ra gợi ý của bạn:"
        ),
    ]
)

# 4. Create the LangChain chain
# This chain combines the prompt, LLM, and parser.
# RunnablePassthrough allows us to pass input variables directly to the prompt.
task_suggestion_chain = (
    {
        "title": RunnablePassthrough(),
        "description": RunnablePassthrough(),
        "similar_tasks_context": RunnablePassthrough(),
        "available_categories_projects_context": RunnablePassthrough(),
        "format_instructions": lambda x: parser.get_format_instructions(),
    }
    | task_suggestion_prompt
    | llm
    | parser
)

# You can also create a simpler chain for direct use if you prefer
# def get_task_suggestion_chain():
#     return (
#         task_suggestion_prompt
#         | llm
#         | parser
#     )
