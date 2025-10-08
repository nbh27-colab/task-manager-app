
from models.features import extract_features
from models.ai.llm_chains import time_chain

import re

def estimate_time(description: str) -> int:
    try:
        llm_result = time_chain.invoke({"task_description": description})
        # Tách số đầu tiên trong chuỗi kết quả
        match = re.search(r"\d+", str(llm_result))
        if match:
            llm_minutes = int(match.group())
            if 1 <= llm_minutes <= 1440:
                return llm_minutes
        raise ValueError("LLM trả về giá trị không hợp lệ")
    except Exception:
        return -1