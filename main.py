from git_manager import get_git_diff
from diff_parser import parse_diff
from gito_core import audit_code
import json


def run_smart_review():
    # 1. 获取本地 Git 的原始 Diff
    diff_raw = get_git_diff()
    if diff_raw == "No staged changes":
        print("💡 没有检测到暂存代码（请先执行 git add）。")
        return

    # 2. 调用清洗器：将原始 Diff 变成带行号的结构化列表
    parsed_diff = parse_diff(diff_raw)

    # 3. 构造发送给 DeepSeek 的文本（把清洗后的结果拼接成字符串）
    # 这样 AI 就能看到：File: app.py, Line: 10, Code: xxxx
    formatted_input = "\n".join([
        f"File: {i['file']}, Line: {i['line']}, Code: {i['content']}"
        for i in parsed_diff
    ])

    # 4. 请求 DeepSeek 审计
    print("🚀 DeepSeek 正在精准审计增量代码...")

    # 【修正处】我们将返回的结果统一命名为 review_output
    review_output = audit_code(formatted_input)

    # 5. 尝试将 AI 返回的 JSON 字符串解析为 Python 对象
    try:
        # 去掉可能存在的 Markdown 代码块标记 (如 ```json ... ```)
        clean_json = review_output.replace("```json", "").replace("```", "").strip()
        issues = json.loads(clean_json)

        print(f"\n✅ 审计完成，发现 {len(issues)} 个潜在问题：")
        for issue in issues:
            print(f"⚠️ [{issue['severity']}] 行 {issue['line']}: {issue['issue']}")
            print(f"   💡 建议: {issue['suggestion']}\n")
    except Exception as e:
        # 如果解析失败（比如 AI 没按格式返回），则打印原始文本
        print("\n--- AI 原始报告（解析 JSON 失败） ---")
        print(review_output)
        print(f"DEBUG Error: {e}")


if __name__ == "__main__":
    run_smart_review()

