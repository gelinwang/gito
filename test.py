import os
from github import Github, Auth

GITHUB_TOKEN = os.getenv("MY_GITO_TOKEN")
REPO_NAME = "gelinwang/gito"
PR_NUMBER = 1


def debug_connection():
    try:
        g = Github(auth=Auth.Token(GITHUB_TOKEN))

        # 步骤 1: 检查能否获取用户信息
        user = g.get_user().login
        print(f"✅ 登录成功，用户为: {user}")

        # 步骤 2: 检查能否访问仓库
        repo = g.get_repo(REPO_NAME)
        print(f"✅ 成功找到仓库: {REPO_NAME}")

        # 步骤 3: 检查能否访问 PR
        pr = repo.get_pull(PR_NUMBER)
        print(f"✅ 成功找到 PR #{PR_NUMBER}: {pr.title}")

    except Exception as e:
        print(f"❌ 出错了: {e}")


if __name__ == "__main__":
    debug_connection()