"""
StockVision AI - LSTM Model (PyTorch)

Lightweight 2-layer stacked LSTM for time-series stock price forecasting.
Architecture sized for typical stock data volumes (~300-500 sequences).
Uses CUDA acceleration when available (e.g. RTX 5070 Ti).
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import logging
import os
from typing import Optional

logger = logging.getLogger("stockvision.ml.lstm")


class PyTorchLSTM(nn.Module):
    """Lightweight 2-layer LSTM sized for stock data volumes."""

    def __init__(self, input_size, hidden_sizes=None, output_size=1, dropout=0.1):
        super(PyTorchLSTM, self).__init__()

        if hidden_sizes is None:
            hidden_sizes = [64, 32]

        self.lstm1 = nn.LSTM(input_size, hidden_sizes[0], batch_first=True)
        self.drop1 = nn.Dropout(dropout)

        self.lstm2 = nn.LSTM(hidden_sizes[0], hidden_sizes[1], batch_first=True)
        self.drop2 = nn.Dropout(dropout)

        self.fc1 = nn.Linear(hidden_sizes[1], 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, output_size)

        # Xavier initialization for stable training
        self._init_weights()

    def _init_weights(self):
        """Apply Xavier initialization to LSTM and Linear layers."""
        for name, param in self.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                # Set forget gate bias to 1 for better gradient flow
                n = param.size(0)
                param.data[n // 4:n // 2].fill_(1.0)

    def forward(self, x):
        # x shape: (batch, seq_len, features)
        out, _ = self.lstm1(x)
        out = self.drop1(out)

        out, _ = self.lstm2(out)
        out = self.drop2(out)

        # Take the output from the last time step
        out = out[:, -1, :]

        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        return out


class LSTMModel:
    """LSTM neural network for time-series stock price forecasting using PyTorch."""

    def __init__(
        self,
        lookback: int = 60,
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001,
    ):
        self.lookback = lookback
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.model = None
        self.history = {"loss": [], "val_loss": []}
        self.name = "lstm"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def build_model(self, input_shape: tuple) -> None:
        """
        Build the PyTorch LSTM architecture.
        input_shape: (seq_len, features)
        """
        features = input_shape[1]
        self.model = PyTorchLSTM(input_size=features).to(self.device)
        param_count = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        logger.info("Built PyTorch LSTM on %s (%d trainable params)", self.device, param_count)

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
    ) -> dict:
        if self.model is None:
            self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate, weight_decay=1e-5)

        # Cosine annealing LR scheduler for smooth convergence
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=self.epochs, eta_min=1e-6)

        # Convert to tensors
        X_t = torch.tensor(X_train, dtype=torch.float32).to(self.device)
        y_t = torch.tensor(y_train, dtype=torch.float32).view(-1, 1).to(self.device)

        if X_val is not None and y_val is not None:
            X_v = torch.tensor(X_val, dtype=torch.float32).to(self.device)
            y_v = torch.tensor(y_val, dtype=torch.float32).view(-1, 1).to(self.device)
            has_val = True
        else:
            has_val = False

        from torch.utils.data import TensorDataset, DataLoader
        dataset = TensorDataset(X_t, y_t)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        logger.info(
            "Training LSTM: epochs=%d, batch=%d, samples=%d, lr=%.4f",
            self.epochs, self.batch_size, len(X_train), self.learning_rate
        )

        best_val_loss = float('inf')
        patience_counter = 0
        patience = 15
        best_model_state = None

        self.history = {"loss": [], "val_loss": []}

        for epoch in range(self.epochs):
            self.model.train()
            epoch_loss = 0.0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()

                # Gradient clipping to prevent exploding gradients
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

                optimizer.step()
                epoch_loss += loss.item() * batch_X.size(0)

            epoch_loss /= len(X_train)
            self.history["loss"].append(round(epoch_loss, 6))

            # Step the LR scheduler
            scheduler.step()

            if has_val:
                self.model.eval()
                with torch.no_grad():
                    val_outputs = self.model(X_v)
                    val_loss = criterion(val_outputs, y_v).item()
                self.history["val_loss"].append(round(val_loss, 6))

                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                    best_model_state = {k: v.clone() for k, v in self.model.state_dict().items()}
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        logger.info(f"Early stopping at epoch {epoch+1}")
                        if best_model_state:
                            self.model.load_state_dict(best_model_state)
                        break

        # Restore best weights if using early stopping
        if has_val and best_model_state:
            self.model.load_state_dict(best_model_state)

        result = {
            "model_type": self.name,
            "status": "trained",
            "epochs_run": len(self.history["loss"]),
            "training_loss": self.history["loss"],
        }
        if has_val:
            result["validation_loss"] = self.history["val_loss"]

        return result

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        self.model.eval()
        with torch.no_grad():
            X_t = torch.tensor(X, dtype=torch.float32).to(self.device)
            outputs = self.model(X_t)
            return outputs.cpu().numpy().flatten()

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        y_pred = self.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        mask = y_test != 0
        mape = float(np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100) if mask.any() else None

        metrics = {
            "model_type": self.name,
            "rmse": rmse,
            "mae": mae,
            "mape": mape,
            "r2_score": r2,
        }
        logger.info("LSTM metrics: RMSE=%.4f, MAE=%.4f, R²=%.4f", rmse, mae, r2)
        return metrics

    def save(self, path: str) -> None:
        if self.model is None:
            raise ValueError("No model to save")
        # Ensure path ends with .pt for PyTorch, but handle caller sending .keras
        save_path = path
        if save_path.endswith('.keras'):
            save_path = save_path[:-6] + '.pt'

        # Save both state_dict and input dimensions (so we can rebuild it)
        checkpoint = {
            'input_size': self.model.lstm1.input_size,
            'state_dict': self.model.state_dict()
        }
        torch.save(checkpoint, save_path)
        logger.info("LSTM model saved to %s", save_path)

    def load(self, path: str) -> None:
        load_path = path
        if load_path.endswith('.keras'):
            load_path = load_path[:-6] + '.pt'

        if not os.path.exists(load_path):
             # Fallback if someone passed .pt directly
            if os.path.exists(path):
                load_path = path
            else:
                raise FileNotFoundError(f"Model file not found at {load_path}")

        checkpoint = torch.load(load_path, map_location=self.device, weights_only=True)
        self.build_model(input_shape=(self.lookback, checkpoint['input_size']))
        self.model.load_state_dict(checkpoint['state_dict'])
        self.model.eval()
        logger.info("LSTM model loaded from %s", load_path)
