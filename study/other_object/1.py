from huggingface_hub import login, snapshot_download

# 登录Hugging Face（使用你的访问令牌）
login(token="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")  # 获取方式见下文

# 现在可以下载模型
snapshot_download(repo_id="meta-llama/Llama-2-7b-hf")