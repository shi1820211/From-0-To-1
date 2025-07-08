import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# ============ 1. 数据准备 ============ #
iris = load_iris()
X = iris.data  # 特征
y = iris.target  # 标签

# 为简单起见，只保留前两个类别（0和1）
X = X[y != 2]
y = y[y != 2]

# 数据标准化
scaler = StandardScaler()
X = scaler.fit_transform(X)

# 转换为 Tensor
X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)  # [N] → [N, 1]

# 划分训练与测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ============ 2. 定义 MLP 模型结构 ============ #
class MLP(nn.Module):
    def __init__(self, input_size, hidden_sizes, output_size):
        super(MLP, self).__init__()

        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_sizes[0]),  # 输入层 → 第1隐藏层
            nn.ReLU(),                               # 非线性激活
            nn.Linear(hidden_sizes[0], hidden_sizes[1]),  # 第1 → 第2隐藏层
            nn.ReLU(),
            nn.Linear(hidden_sizes[1], output_size),      # 第2隐藏层 → 输出层
            nn.Sigmoid()  # 输出为二分类概率
        )

    def forward(self, x):
        return self.model(x)

# 实例化模型
model = MLP(input_size=4, hidden_sizes=[16, 8], output_size=1)

# ============ 3. 定义损失函数与优化器 ============ #
criterion = nn.BCELoss()  # 二分类交叉熵
optimizer = optim.Adam(model.parameters(), lr=0.01)

# ============ 4. 训练模型 ============ #
epochs = 100
for epoch in range(epochs):
    model.train()

    # 前向传播
    outputs = model(X_train)
    loss = criterion(outputs, y_train)

    # 反向传播与优化
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch+1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# ============ 5. 测试模型 ============ #
model.eval()
with torch.no_grad():
    test_outputs = model(X_test)
    predicted = (test_outputs > 0.5).float()
    acc = accuracy_score(y_test, predicted)
    print(f"\nTest Accuracy: {acc * 100:.2f}%")
