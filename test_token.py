import os
from github import Github, Auth

token = os.getenv("MY_GITO_TOKEN")
print(token)
print(f"当前读取到的 Token 后缀: {str(token)[-10:]}...")

try:
    auth = Auth.Token(token)
    g = Github(auth=auth)
    user = g.get_user().login
    print(f"✅ 认证成功！当前用户: {user}")
except Exception as e:
    print(f"❌ 认证失败: {e}")