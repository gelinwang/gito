import os
from openai import OpenAI

# 1. 初始化客户端 (这里可以替换为 DeepSeek, OpenAI 或其他兼容接口)
client = OpenAI(
    api_key="sk-501cb2cd4c5046939d59af326b244474",
    base_url="https://api.deepseek.com"
)


def audit_code(file_content):
    # 2. 模拟 Gito 的专家级 Prompt
    system_prompt = """
    你是一个资深代码安全专家。请分析以下代码中的'高信心'、'高影响力'问题。
    重点关注：SQL注入、内存泄漏、严重逻辑错误、可维护性极差的模式。

    请严格按照以下 JSON 格式输出结果，不要包含任何额外文字：
    [
        {"line": 行号, "issue": "问题简述", "severity": "HIGH/MEDIUM", "suggestion": "修复建议"}
    ]
    """

    user_prompt = f"请评审以下代码内容：\n\n{file_content}"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False # 代码审计建议一次性返回，不建议流式
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


# 3. 模拟一个包含 Bug 的代码文件进行测试
test_code = """
def get_user_data(user_id):
    # 模拟一个明显的 SQL 注入漏洞
    query = "SELECT * FROM users WHERE id = " + user_id
    db.execute(query) 

def process_list(items):
    # 模拟一个潜在的空指针/索引错误
    print(items[10]) 
"""

if __name__ == "__main__":
    print("🚀 正在启动 AI 代码审计...")
    result = audit_code(test_code)
    print("\n--- 审计结果 ---")
    print(result)
    print("this is test")
    print("this is two")
    print("this is three")
    print("this is four")
    print("this is five")
    print("this is six")