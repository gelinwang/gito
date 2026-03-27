import subprocess


def get_git_diff():
    try:
        # 修改点：显式指定 encoding='utf-8'，并添加 errors='ignore'
        result = subprocess.run(
            ['git', 'diff', '--staged', '--unified=3'],
            capture_output=True,
            text=True,
            encoding='utf-8',  # 强制使用 UTF-8
            errors='ignore',  # 忽略无法解码的字符
            check=True
        )

        diff_text = result.stdout

        if not diff_text.strip():
            return "No changes staged for commit."

        return diff_text
    except subprocess.CalledProcessError as e:
        return f"Error running git diff: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


if __name__ == "__main__":
    print("--- 当前 Git 暂存区差异 ---")
    print(get_git_diff())
