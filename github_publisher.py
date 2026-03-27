from github import Github, Auth
import os

# 建议把 Token 放在环境变量里，不要直接写在代码里
GITHUB_TOKEN = os.getenv("MY_GITO_TOKEN")
REPO_NAME = "gelinwang/gito"  # 例如 "zhangsan/test-repo"
PR_NUMBER = 1  # 你正在测试的 PR 编号

def publish_review(issues):
    """
    将 DeepSeek 的 issue 列表提交为 GitHub PR Review
    issues 格式: [{'file': 'main.py', 'line': 10, 'issue': '...', 'suggestion': '...'}]
    """
    # 检查 Token 是否成功获取
    if not GITHUB_TOKEN:
        print("❌ 错误：未能获取环境变量 MY_GITO_TOKEN，请检查系统设置。")
        return

    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(PR_NUMBER)

    # 获取当前 PR 的最新 Commit ID (Review 必须关联到具体的 commit)
    latest_commit = pr.get_commits().reversed[0]

    comments = []
    for issue in issues:
        # 构造 GitHub 要求的评论格式
        comments.append({
            "path": issue['file'],
            "line": int(issue['line']),
            "body": f"⚠️ **AI 审计发现问题**\n\n**描述**: {issue['issue']}\n**建议**: {issue['suggestion']}"
        })

    if not comments:
        print("✅ 没有发现需要评论的问题。")
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
            "file": "git_manager.py",
            "line": 5,
            "issue": "硬编码测试",
            "suggestion": "请使用环境变量"
        }
    ]
    publish_review(test_issues)
