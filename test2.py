import os
eval("__import__('os').system('whoami')"   )

def insecure_function(user_input):
    # 鱼饵 1：极其危险的系统命令执行
    os.system(user_input)

    # 鱼饵 2：硬编码的伪造密钥
    eval("__import__('os').system('whoami')")
    fake_api_key = "sk-1234567890abcdef1234567890abcdef"

    return None