import re


def parse_diff(diff_text):
    """
    将原始 Diff 文本解析为更易读的格式：文件名、行号、内容
    """
    lines = diff_text.split('\n')
    parsed_results = []
    current_file = ""
    new_line_num = 0

    for line in lines:
        # 提取文件名
        if line.startswith('+++ b/'):
            current_file = line[6:]
            continue

        # 提取行号起始点 (例如 @@ -1,4 +10,5 @@)
        chunks = re.match(r'^@@ \-\d+,\d+ \+(\d+),\d+ @@', line)
        if chunks:
            new_line_num = int(chunks.group(1))
            continue

        # 提取实际代码行
        if line.startswith('+') and not line.startswith('+++'):
            parsed_results.append({
                "file": current_file,
                "line": new_line_num,
                "content": line[1:].strip()  # 去掉开头的 + 号
            })
            new_line_num += 1
        elif line.startswith(' '):  # 未修改的上下文行
            new_line_num += 1

    return parsed_results


# 测试清洗效果
if __name__ == "__main__":
    test_diff = """
diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,3 +1,4 @@
 def start():
-    print("old")
+    user_input = input("Enter name: ")
+    print(user_input)
    """
    print("--- 清洗后的数据 ---")
    for item in parse_diff(test_diff):
        print(f"文件: {item['file']} | 行号: {item['line']} | 内容: {item['content']}")
