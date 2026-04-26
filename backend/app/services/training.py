"""
模型训练服务 —— 全连接神经网络分类钢管回弹程度
输出: 0=角度偏小(欠弯), 1=角度合适, 2=角度偏大(过弯)
迭代推理: 当输出为0或2时，调整角度后重新预测直到输出1
"""
from __future__ import annotations

import os
import json
import csv
import io
import math
import threading
from datetime import datetime, timezone
from typing import Optional

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    optim = None
    DataLoader = None
    TensorDataset = None
    np = None
    ML_AVAILABLE = False

ML_UNAVAILABLE_MESSAGE = "当前部署未安装机器学习依赖，训练和预测功能不可用"

MATERIALS = ["普通钢", "高强钢", "不锈钢", "铝合金"]
MATERIAL_TO_IDX = {m: i for i, m in enumerate(MATERIALS)}
NUM_MATERIALS = len(MATERIALS)

NUMERICAL_FEATURES = 3  # diameter, thickness, target_angle
INPUT_DIM = NUM_MATERIALS + NUMERICAL_FEATURES  # 4 + 3 = 7

RESULT_LABELS = {0: "角度偏小", 1: "角度合适", 2: "角度偏大"}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "springback_model.pt")


if ML_AVAILABLE:
    class SpringbackNet(nn.Module):
        """回弹分类全连接网络"""

        def __init__(self, input_dim: int = INPUT_DIM, hidden_dims: list = None, num_classes: int = 3):
            super().__init__()
            if hidden_dims is None:
                hidden_dims = [64, 32, 16]

            layers = []
            prev_dim = input_dim
            for hd in hidden_dims:
                layers.append(nn.Linear(prev_dim, hd))
                layers.append(nn.LayerNorm(hd))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(0.2))
                prev_dim = hd
            layers.append(nn.Linear(prev_dim, num_classes))

            self.net = nn.Sequential(*layers)

        def forward(self, x):
            return self.net(x)
else:
    class SpringbackNet:
        """占位模型，避免轻量部署缺少 torch 时影响其它接口启动。"""

        def __init__(self, *args, **kwargs):
            raise RuntimeError(ML_UNAVAILABLE_MESSAGE)


def encode_input(material: str, diameter: float, thickness: float, target_angle: float) -> np.ndarray:
    """将输入参数编码为模型输入向量"""
    material_onehot = np.zeros(NUM_MATERIALS, dtype=np.float32)
    if material in MATERIAL_TO_IDX:
        material_onehot[MATERIAL_TO_IDX[material]] = 1.0
    numerical = np.array([diameter / 500.0, thickness / 50.0, target_angle / 180.0], dtype=np.float32)
    return np.concatenate([material_onehot, numerical])


def encode_inputs_batch(records: list) -> torch.Tensor:
    """批量编码输入"""
    arr = np.array([encode_input(r["material"], r["diameter"], r["thickness"], r["target_angle"]) for r in records])
    return torch.tensor(arr, dtype=torch.float32)


def decode_labels(labels: list) -> torch.Tensor:
    return torch.tensor(labels, dtype=torch.long)


def parse_csv(content: str) -> list[dict]:
    """解析 CSV 数据集，返回记录列表"""
    reader = csv.DictReader(io.StringIO(content))
    records = []
    required_cols = {"material", "diameter", "thickness", "target_angle", "result"}
    for row in reader:
        if not required_cols.issubset(row.keys()):
            continue
        try:
            record = {
                "material": row["material"].strip(),
                "diameter": float(row["diameter"]),
                "thickness": float(row["thickness"]),
                "target_angle": float(row["target_angle"]),
                "result": int(float(row["result"])),
            }
            if record["material"] not in MATERIAL_TO_IDX:
                continue
            if record["result"] not in (0, 1, 2):
                continue
            records.append(record)
        except (ValueError, KeyError):
            continue
    return records


class TrainingState:
    """训练状态单例"""

    def __init__(self):
        self.model: Optional[SpringbackNet] = None
        self.is_training = False
        self.current_epoch = 0
        self.total_epochs = 0
        self.train_losses: list[float] = []
        self.val_accuracies: list[float] = []
        self.final_accuracy = 0.0
        self.confusion = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.message = ""
        self.error = ""
        self.dataset_size = 0
        self.best_loss = float("inf")
        self._records: list[dict] = []
        self._lock = threading.Lock()

    def reset(self):
        with self._lock:
            self.is_training = False
            self.current_epoch = 0
            self.train_losses = []
            self.val_accuracies = []
            self.final_accuracy = 0.0
            self.confusion = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            self.message = ""
            self.error = ""
            self.best_loss = float("inf")

    def set_records(self, records: list[dict]):
        with self._lock:
            self._records = records
            self.dataset_size = len(records)

    def get_records(self) -> list[dict]:
        with self._lock:
            return list(self._records)

    def to_dict(self) -> dict:
        with self._lock:
            return {
                "ml_available": ML_AVAILABLE,
                "is_training": self.is_training,
                "current_epoch": self.current_epoch,
                "total_epochs": self.total_epochs,
                "train_losses": self.train_losses,
                "val_accuracies": self.val_accuracies,
                "final_accuracy": self.final_accuracy,
                "confusion": self.confusion,
                "message": self.message,
                "error": self.error,
                "dataset_size": self.dataset_size,
                "model_exists": ML_AVAILABLE and self.model is not None,
            }

    def save_model(self):
        if not ML_AVAILABLE or self.model is None:
            return
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        torch.save(self.model.state_dict(), MODEL_PATH)

    def load_model(self) -> bool:
        if not ML_AVAILABLE:
            self.message = ML_UNAVAILABLE_MESSAGE
            return False
        if not os.path.exists(MODEL_PATH):
            return False
        try:
            self.model = SpringbackNet()
            self.model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu", weights_only=True))
            self.model.eval()
            return True
        except Exception:
            return False


training_state = TrainingState()
# 启动时尝试加载已有模型
training_state.load_model()


def run_training(records: list[dict], epochs: int = 80, batch_size: int = 32, lr: float = 0.001):
    """在后台线程执行训练"""
    state = training_state
    state.reset()
    state.dataset_size = len(records)

    if not ML_AVAILABLE:
        with state._lock:
            state.error = ML_UNAVAILABLE_MESSAGE
        return

    if len(records) < 10:
        with state._lock:
            state.error = "数据集过小（至少需要10条记录）"
        return

    # 划分训练集/验证集 80/20
    np.random.seed(42)
    indices = np.random.permutation(len(records))
    split = int(len(records) * 0.8)
    train_idx = indices[:split]
    val_idx = indices[split:]

    train_records = [records[i] for i in train_idx]
    val_records = [records[i] for i in val_idx]

    X_train = encode_inputs_batch(train_records)
    y_train = decode_labels([r["result"] for r in train_records])
    X_val = encode_inputs_batch(val_records)
    y_val = decode_labels([r["result"] for r in val_records])

    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    state.model = SpringbackNet()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(state.model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    state.is_training = True
    state.total_epochs = epochs

    for epoch in range(epochs):
        if not state.is_training:
            break

        # 训练
        state.model.train()
        epoch_loss = 0.0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = state.model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        avg_loss = epoch_loss / max(len(train_loader), 1)
        scheduler.step()

        # 验证
        state.model.eval()
        correct = 0
        total = 0
        cm = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                outputs = state.model(batch_x)
                _, predicted = torch.max(outputs, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
                for t, p in zip(batch_y.tolist(), predicted.tolist()):
                    cm[t][p] += 1

        val_acc = correct / max(total, 1)

        with state._lock:
            state.current_epoch = epoch + 1
            state.train_losses.append(round(avg_loss, 4))
            state.val_accuracies.append(round(val_acc, 4))
            if avg_loss < state.best_loss:
                state.best_loss = avg_loss
            state.message = f"Epoch {epoch + 1}/{epochs} - Loss: {avg_loss:.4f}, Val Acc: {val_acc:.4f}"

    # 训练完成
    with state._lock:
        state.is_training = False
        state.final_accuracy = state.val_accuracies[-1] if state.val_accuracies else 0.0
        state.confusion = cm
        state.message = f"训练完成 - 最终准确率: {state.final_accuracy * 100:.1f}%"

    state.save_model()


def start_training(records: list[dict], epochs: int = 80, batch_size: int = 32, lr: float = 0.001):
    """启动训练线程"""
    if not ML_AVAILABLE:
        with training_state._lock:
            training_state.error = ML_UNAVAILABLE_MESSAGE
        return False
    if training_state.is_training:
        return False
    thread = threading.Thread(target=run_training, args=(records, epochs, batch_size, lr))
    thread.daemon = True
    thread.start()
    return True


def predict_one(material: str, diameter: float, thickness: float, target_angle: float) -> dict:
    """单次预测"""
    state = training_state
    if not ML_AVAILABLE:
        return {"class": -1, "label": ML_UNAVAILABLE_MESSAGE, "probabilities": []}
    if state.model is None:
        return {"class": -1, "label": "模型未加载", "probabilities": []}

    x = torch.tensor(encode_input(material, diameter, thickness, target_angle), dtype=torch.float32).unsqueeze(0)
    state.model.eval()
    with torch.no_grad():
        output = state.model(x)
        probs = torch.softmax(output, dim=1).squeeze().tolist()
        pred = int(torch.argmax(output, dim=1).item())

    return {"class": pred, "label": RESULT_LABELS[pred], "probabilities": [round(p, 4) for p in probs]}


def predict_iterative(material: str, diameter: float, thickness: float, target_angle: float,
                      max_iterations: int = 20, step: float = 0.5) -> dict:
    """迭代预测 —— 当结果为0或2时自动调整角度，直到输出1"""
    state = training_state
    if not ML_AVAILABLE:
        return {"success": False, "error": ML_UNAVAILABLE_MESSAGE, "final_angle": None, "steps": []}
    if state.model is None:
        return {"success": False, "error": "模型未训练，请先导入数据集并训练", "final_angle": None, "steps": []}

    current_angle = target_angle
    steps = []
    final_class = None

    for i in range(max_iterations):
        result = predict_one(material, diameter, thickness, current_angle)
        steps.append({
            "iteration": i + 1,
            "input_angle": round(current_angle, 2),
            "predicted_class": result["class"],
            "predicted_label": result["label"],
            "probabilities": result["probabilities"],
        })

        if result["class"] == 1:
            final_class = 1
            break
        elif result["class"] == 0:
            # 角度偏小 → 增大角度
            current_angle += step * (1 + i * 0.1)
        elif result["class"] == 2:
            # 角度偏大 → 减小角度
            current_angle -= step * (1 + i * 0.1)
        else:
            break

        current_angle = max(0.0, min(180.0, current_angle))

    return {
        "success": final_class == 1,
        "original_angle": target_angle,
        "final_angle": round(current_angle, 2) if final_class == 1 else None,
        "final_class": final_class,
        "iterations": len(steps),
        "steps": steps,
        "message": f"经过{len(steps)}轮迭代，{'成功收敛到角度 ' + str(round(current_angle, 2)) + '°' if final_class == 1 else '未能在' + str(max_iterations) + '轮内收敛'}",
    }
