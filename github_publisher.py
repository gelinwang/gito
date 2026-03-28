import requests
from github import Github, Auth
import os
import re

# 建议把 Token 放在环境变量里，不要直接写在代码里
GITHUB_TOKEN = os.getenv("MY_GITO_TOKEN")
REPO_NAME = "gelinwang/gito"  # 例如 "zhangsan/test-repo"
PR_NUMBER = 2  # 你正在测试的 PR 编号


# 实现从git diff的输出中找到每一行改动对应的 GitHub API position
def get_diff_position(diff_output, target_file, target_line):
    """
    根据给定的文件和真实行号，找到对应的 GitHub Diff Position
    """
    lines = diff_output.split('\n')
    found_file = False
    new_line_counter = 0
    position = 0  # GitHub API 要求的 Position (从 hunk header 后的第一行算 1)

    for line in lines:
        if line.startswith('+++ b/') and line[5:] == target_file:
            found_file = True
            continue

        if found_file:
            if line.startswith('@@'):
                # 提取 hunk header: @@ -old_start,old_count +new_start,new_count @@
                import re
                match = re.match(r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@', line)
                if match:
                    new_line_counter = int(match.group(3))  # 新文件的起始行号
                    position = 0  # 重置 hunk 计数器
                    continue

            elif line.startswith('+') and not line.startswith('+++'):
                # 找到加号（新增或修改的行）
                position += 1
                if new_line_counter == target_line:
                    return position  # 成功匹配！
                new_line_counter += 1

            elif line.startswith(' '):
                # 上下文行（未改动）
                position += 1
                new_line_counter += 1

            elif line.startswith('-'):
                # 减号（删除的行），不增加真实行号，但增加 position
                position += 1

    return None  # 未找到匹配的 position


def publish_review(issues):
    """
    将 DeepSeek 的 issue 列表提交为 GitHub PR Review
    issues 格式: [{'file': 'main.py', 'line': 10, 'issue': '...', 'suggestion': '...'}]
    """
    # 检查 Token 是否成功获取
    if not GITHUB_TOKEN:
        print("❌ 错误：未能获取环境变量 MY_GITO_TOKEN，请检查系统设置。")
        return

    # 初始化 Github 客户端
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(PR_NUMBER)

    # --- 关键点：获取该 PR 真实的 Diff 内容用于行号对齐 ---
    # 通过 pr.patch_url 获取 GitHub 生成的补丁文件链接
    print(f"正在从 {pr.patch_url} 获取 Diff 内容...")
    response = requests.get(pr.patch_url)
    if response.status_code != 200:
        print("❌ 无法获取 PR 的 Diff 内容")
        return
    raw_diff = response.text

    # 获取当前 PR 的最新 Commit ID (Review 必须关联到具体的 commit)
    latest_commit = pr.get_commits().reversed[0]
    comments = []

    for issue in issues:
        # 1. 尝试把真实行号翻译成 GitHub Position
        pos = get_diff_position(raw_diff, issue['file'], int(issue['line']))

        # 构造 GitHub 要求的评论格式
        if pos:
            comments.append({
                "path": issue['file'],
                "position": pos,  # 注意：这里必须用 position 而不是 line
                "body": f"### 🤖 Gito AI 审计建议\n**问题**: {issue['issue']}\n**建议**: {issue['suggestion']}"
            })
            print(f"📍 找到行号对齐：{issue['file']} Line {issue['line']} -> Position {pos}")
        else:
            print(f"⚠️ 忽略：{issue['file']} 的第 {issue['line']} 行不在本次 PR 修改范围内。")

    if not comments:
        print("✅ 没发现有效的、在修改范围内的评论。")
        return

    # 一次性提交所有评论
    try:
        pr.create_review(
            commit=latest_commit,
            body="🤖 Gito Python 复现版：AI 自动代码审计报告",
            event="COMMENT",  # 或者使用 "REQUEST_CHANGES" 如果问题很严重
            comments=comments
        )
        print(f"🎉 成功在 PR #{PR_NUMBER} 中发布了 {len(comments)} 条评论！")
    except Exception as e:
        print(f"❌ 发布失败: {e}")


if __name__ == "__main__":
    # 测试数据
    test_issues = [
        {
            "file": "test2.py",
            "line": 3,
            "issue": "硬编码测试",
            "suggestion": "请使用环境变量"
        }
    ]
    publish_review(test_issues)
