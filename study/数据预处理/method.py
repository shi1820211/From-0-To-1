import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 设置中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题

# 创建合适大小的画布 - 使用横向布局
fig, ax = plt.subplots(figsize=(12, 8))  # 📌 横向画布 (12x8英寸)
ax.axis("off")  # 隐藏坐标轴

# 定义流程节点 - 医学数据集检验流程
steps = [
    "自动过滤后的数据\n(Population)",
    "定义质量标准\n(AQL, RQL)",
    "抽样设计\n(随机/分层抽样)",
    "专家审核样本",
    "统计缺陷数 d",
    "判定：d ≤ c ?",  # 📌 决策节点
    "接受数据集\n(Accept)",
    "拒收/再抽样\n(Reject/Resample)"
]

# 节点位置 (x,y坐标) - 使用网格布局
positions = [
    (2, 7),  # 节点0
    (2, 5),  # 节点1
    (2, 3),  # 节点2
    (2, 1),  # 节点3
    (2, -1),  # 节点4
    (2, -3),  # 节点5 (决策节点)
    (0, -5),  # 节点6 (接受)
    (4, -5)  # 节点7 (拒收)
]

# 绘制节点
for i, (step, (x, y)) in enumerate(zip(steps, positions)):
    # 根据文本长度动态调整节点框宽度
    text_length = len(step.replace("\n", ""))  # 计算文本长度（忽略换行符）
    box_width = max(0.8, min(1.2, text_length * 0.06))  # 动态宽度计算

    # 创建圆角矩形节点
    box = mpatches.FancyBboxPatch(
        (x - box_width / 2, y - 0.2),  # x位置居中，y位置微调
        box_width, 0.4,  # 宽度动态调整，高度固定
        boxstyle="round,pad=0.1,rounding_size=0.05",  # 圆角样式
        fc="#DCE6F1" if i != 5 else "#FFE4B5",  # 决策节点使用不同颜色
        ec="black",  # 边框色
        lw=1  # 边框线宽
    )
    ax.add_patch(box)  # 将节点添加到画布

    # 添加节点文字
    ax.text(
        x, y,  # 文字位置(居中)
        step,  # 文字内容
        ha="center",  # 水平居中
        va="center",  # 垂直居中
        fontsize=10,  # 字体大小
        wrap=True  # 自动换行
    )

# 绘制连接线
connections = [
    (0, 1),  # 节点0 -> 节点1
    (1, 2),  # 节点1 -> 节点2
    (2, 3),  # 节点2 -> 节点3
    (3, 4),  # 节点3 -> 节点4
    (4, 5),  # 节点4 -> 节点5
    (5, 6),  # 节点5 -> 节点6 (接受)
    (5, 7)  # 节点5 -> 节点7 (拒收)
]

# 绘制所有连接线
for start, end in connections:
    start_x, start_y = positions[start]
    end_x, end_y = positions[end]

    # 对于分支连接，添加弯曲
    if start == 5 and end == 6:  # 决策到接受
        ax.annotate("",
                    xy=(end_x, end_y + 0.4),
                    xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle="->", lw=1.5),
                    annotation_clip=False)
        ax.text((start_x + end_x) / 2 - 0.5, (start_y + end_y) / 2, "Yes",
                fontsize=10, ha="center", va="center")

    elif start == 5 and end == 7:  # 决策到拒收
        ax.annotate("",
                    xy=(end_x, end_y + 0.4),
                    xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle="->", lw=1.5),
                    annotation_clip=False)
        ax.text((start_x + end_x) / 2 + 0.5, (start_y + end_y) / 2, "No",
                fontsize=10, ha="center", va="center")

    else:  # 直线连接
        ax.annotate("",
                    xy=(end_x, end_y + 0.4),
                    xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle="->", lw=1.5),
                    annotation_clip=False)

# 添加标题
plt.title("医学数据集接受抽样检验流程图",
          fontsize=16,  # 增大标题字体
          weight="bold",
          pad=20)  # 标题与顶部的距离

# 设置坐标轴范围，确保所有元素可见
ax.set_xlim(-1, 5)
ax.set_ylim(-6, 8)

# 使用constrained_layout自动调整布局
plt.tight_layout()

plt.show()