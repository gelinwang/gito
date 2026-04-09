import requests
from github import Github, Auth
import os
import re

# 建议把 Token 放在环境变量里，不要直接写在代码里
GITHUB_TOKEN = os.getenv("MY_GITO_TOKEN")
REPO_NAME = "gelinwang/gito"  # 例如 "zhangsan/test-repo"
PR_NUMBER = 9  # 你正在测试的 PR 编号


# 实现从git diff的输出中找到每一行改动对应的 GitHub API position
def get_diff_position(diff_output, target_file, target_line):
    lines = diff_output.split('\n')
    found_file = False
    current_new_line = 0
    # GitHub 的 position 是从 diff 中第一个 @@ 之后的第一行开始算，初始为 0
    # 在进入第一个 hunk 后，第一行内容会让它变为 1
    absolute_position = 0

    for line in lines:
        # 修正：使用 line[6:] 并 strip，确保匹配文件名准确
        if line.startswith('+++ b/'):
            if line[6:].strip() == target_file:
                found_file = True
                continue
            else:
                found_file = False
                continue

        if not found_file:
            continue

        # 记录在当前文件内的绝对偏移
        absolute_position += 1

        if line.startswith('@@'):
            import re
            match = re.match(r'^@@ -\d+,\d+ \+(\d+),\d+ @@', line)
            if match:
                current_new_line = int(match.group(1))
                # 注意：@@ 这一行本身不计入 position 统计，但我们要记录它之后的位置
                # 这里不需要重置 absolute_position，因为 position 在一个文件的 diff 中是累加的
            continue

        # 检查是否匹配到目标行
        if line.startswith('+') or line.startswith(' '):
            if current_new_line == target_line:
                # 找到了目标行，返回相对于第一个 hunk header 的偏移量
                # GitHub 的 position 计数包含 @@ 之后的所有行（+ - 和空格）
                return absolute_position - 1
            current_new_line += 1
        elif line.startswith('-'):
            # 删除行增加 position 计数，但不增加新文件的行号计数
            pass

    return None


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

    try:
        repo = g.get_repo(REPO_NAME)
        # 打印一下，确认仓库是否连接成功
        print(f"✅ 成功连接仓库: {repo.full_name}")

        pr = repo.get_pull(PR_NUMBER)
        if pr is None:
            print(f"❌ 错误：在仓库里找不到编号为 {PR_NUMBER} 的 PR")
            return

        print(f"✅ 成功获取 PR: {pr.title}")
    except Exception as e:
        print(f"❌ 访问 GitHub 时发生错误: {e}")
        return

    # 只有确保 pr 不是 None，才执行下面的 patch_url
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
        try:
            target_line = int(issue['line'])
        except (ValueError, TypeError):
            continue

        pos = get_diff_position(raw_diff, issue['file'], target_line)

        if pos is not None:  # 明确判断是否拿到了 position
            comments.append({
                "path": issue['file'],
                "position": pos,
                "body": f"### 🤖 Gito AI 审计建议\n**问题**: {issue['issue']}\n**建议**: {issue['suggestion']}"
            })
            print(f"📍 找到行号对齐：{issue['file']} Line {target_line} -> Position {pos}")
        else:
            # 如果没对齐，我们直接跳过，不要把它放进 comments 列表
            print(f"⚠️ 跳过：{issue['file']} Line {target_line} 不在 Diff 范围内")

    if not comments:
        print("✅ 没发现有效的、在修改范围内的评论。")
        return

    # 打印一下即将发送的评论数量，确保不是空的
    print(f"即将提交 {len(comments)} 条有效评论...")

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
            "line": 2,
            "issue": "硬编码测试",
            "suggestion": "请使用环境变量"
        }
    ]
    publish_review(test_issues)
