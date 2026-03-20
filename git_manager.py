import subprocess

def get_git_diff():
    """
    获取当前本地暂存区(staged)的代码差异。
    相当于在命令行执行 git diff --cached
    """
    try:
        # 调用git命令
        # --unified=3 表示显示改动行及其前后各3行的上下文
        result = subprocess.run(
            ['git', 'diff', '--cached', '--unified=3'],
            capture_output=True,
            text=True,
            check=True,
        )

        diff_text = result.stdout

        if not diff_text:
            return "No changes staged for commit."

        return diff_text
    except subprocess.CalledProcessError as e:
        return f"Error running git diff: {e}"

    except FileNotFoundError:
        return "Git command not found. Please ensure Git is installed."

if __name__ == "__main__":
    # 测试一下能否读取到改动
    print("--- 当前 Git 暂存区差异 ---")
    print(get_git_diff())