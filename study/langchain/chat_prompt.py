# from langchain_core.prompts import ChatPromptTemplate
#
# prompt_template = ChatPromptTemplate.from_messages([
#     ("system","you are a helpful assistant"),
#     ("user","Tell me a joke about {topic}")
# ])
# result = prompt_template.invoke({"topic":"cats"})
# print(result)



# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
#
# prompt = ChatPromptTemplate.from_messages([

#     SystemMessage(content="你是一个儿童健康顾问")
# ])
# chat_history = []
#
# # 用户新的提问
# user_input = "那他老是哭闹怎么办？"
#
# # 构造新的 Prompt 模板
# prompt = ChatPromptTemplate.from_messages(
#     [SystemMessage(content="你是一个儿童健康顾问")] + chat_history + [HumanMessage(content=user_input)]
# )
#
# # 用你自己封装好的 Qwen 模型调用
# response = qwen.invoke(prompt)
#
# # 记录新对话
# chat_history.append(HumanMessage(content=user_input))
# chat_history.append(AIMessage(content=response.content))
