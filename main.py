from git_manager import get_git_diff
from diff_parser import parse_diff
from gito_core import audit_code
from github_publisher import publish_review, GITHUB_TOKEN, PR_NUMBER
import json


def run_smart_review():
    # 1. 获取本地 Git 的原始 Diff
    print("1. 正在获取本地增量代码...")
    diff_raw = get_git_diff()
    if diff_raw == "No staged changes":
        print("💡 没有检测到暂存代码（请先执行 git add）。")
        return

    # 2. 调用清洗器：将原始 Diff 变成带行号的结构化列表
    print("2. 正在解析 Diff...")
    parsed_diff = parse_diff(diff_raw)

    # 3. 构造发送给 DeepSeek 的文本（把清洗后的结果拼接成字符串）
    # 这样 AI 就能看到：File: app.py, Line: 10, Code: xxxx
    formatted_input = "\n".join([
        f"File: {i['file']}, Line: {i['line']}, Code: {i['content']}"
        for i in parsed_diff
    ])

    # 4. 请求 DeepSeek 审计
    print("3.DeepSeek 正在精准审计增量代码...")

    # 【修正处】我们将返回的结果统一命名为 review_output
    review_output = audit_code(formatted_input)

    # 5. 尝试将 AI 返回的 JSON 字符串解析为 Python 对象
    print("4. 正在解析 AI 报告并推送到 GitHub...")
    try:
        # 1. 清理并解析 JSON
        clean_json = review_output.replace("```json", "").replace("```", "").strip()
        raw_issues = json.loads(clean_json)

        # --- 调试：打印 AI 原始给出的第一个问题，看看键名到底是什么 ---
        if raw_issues:
            print(f"DEBUG: AI 原始返回的第一个问题内容: {raw_issues[0]}")
        # -------------------------------------------------------

        standardized_issues = []
        for issue in raw_issues:
            # 1. 尝试获取文件名，如果 AI 没给，默认设为 test2.py (或者你当前测试的文件名)
            f = issue.get('file') or issue.get('path') or issue.get('filename') or "test2.py"

            # 2. 确保行号存在
            l = issue.get('line') or issue.get('row')

            # 3. 提取建议
            iss = issue.get('issue') or issue.get('description')
            sug = issue.get('suggestion') or issue.get('fix')

            if l:  # 只要有行号，我们就认为它是有效的
                standardized_issues.append({
                    "file": f.strip().replace("./", ""),
                    "line": l,
                    "issue": iss or "代码风险",
                    "suggestion": sug or "建议优化此行代码"
                })

        print(f"DEBUG: 转换后有效的问题数量 = {len(standardized_issues)}")

        if standardized_issues and GITHUB_TOKEN:
            print(f"🚀 正在推送到 GitHub PR #{PR_NUMBER}...")
            publish_review(standardized_issues)
        else:
            print("💡 未发现有效问题（可能是键名无法匹配或 AI 未发现风险）。")

    except Exception as e:
        print(f"❌ 解析失败: {e}")
        print("AI 原始输出:", review_output)


if __name__ == "__main__":
    run_smart_review()

