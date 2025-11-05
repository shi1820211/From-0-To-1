import random
import torch
from d2l import torch as d2l

# 生成数据集
def synthetic_data(w, b, num_examples):  #@save
    """生成y=Xw+b+噪声"""
    X = torch.normal(0, 1, (num_examples, len(w)))
    # 使用torch.normal随机生成均值为0，标准差为1，形状为(num_examples, len(w))的符合正态分布的随机数组
    y = torch.matmul(X, w) + b
    # 使用torch.matmul做矩阵乘法
    y += torch.normal(0, 0.01, y.shape)
    # y=y+torch.normal(0, 0.01, y.shape)，在原来y的基础上，增加一个形状为y，均值为0，标准差为0.01符合正态分布的噪点
    return X, y.reshape((-1, 1))
#返回x以及重塑后形状的y，其中（-1,1）表示n行，1列，当n为-1是，会根据形状自动调整
true_w = torch.tensor([2, -3.4])
true_b = 4.2
features, labels = synthetic_data(true_w, true_b, 1000)
