from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template("tell me a joke about {topic}")
# 通过invoke生成提示词模版
result = prompt_template.invoke({"topic":"cats"})

print(result)