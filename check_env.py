import os

# 读取环境变量
token = os.getenv("MY_GITO_TOKEN")

if token:
    print(f"✅ 成功读取到 MY_GITO_TOKEN")
    # 只打印前 10 位，防止再次被日志记录泄露
    print(f"Token 前缀: {token[:10]}******")
else:
    print("❌ 未找到环境变量 MY_GITO_TOKEN，请检查设置。")