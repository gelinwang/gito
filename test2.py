def generate_long_string(items):
    result = "             "
    for item in items:
        # 错误：在循环中使用 + 拼接字符串
        # Python 中字符串是不可变的，每次 + 都会创建新对象，时间复杂度是 O(n^2)
        result += str(item) + ","
    return result