from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from torch.utils.data import DataLoader
import torch
import numpy as np

from model import BaseModel


class KNN(BaseModel):
    def __init__(self):
        super().__init__()

    def model_init(self):
        # Hyperparameters
        param_grid = {
            "n_neighbors": [3, 5, 7, 9],  # Test different values of k
            "weights": ["uniform", "distance"],  # Uniform or distance-based weighting
            "metric": ["euclidean", "manhattan"],  # Distance metrics
        }

        self.grid_search = GridSearchCV(
            KNeighborsClassifier(),
            param_grid=param_grid,
            cv=5,
            scoring="accuracy",
            verbose=2,
        )
        self.model: KNeighborsClassifier = None

    def train(self, train_loader: DataLoader, validate_loader: DataLoader):
        X_train, y_train = self._loader_to_numpy(loader=train_loader)
        X_validate, y_validate = self._loader_to_numpy(loader=validate_loader)

        X = np.vstack((X_train, X_validate))
        y = np.hstack((y_train, y_validate))

        # Find the best model hyperparameters
        self.grid_search.fit(X=X, y=y)

        # Select the best model
        self.model = self.grid_search.best_estimator_

    def _loader_to_numpy(self, loader: DataLoader) -> tuple[np.ndarray, np.ndarray]:
        x_list, y_list = [], []

        for batch in loader:
            features, labels = batch
            x_list.append(features)
            y_list.append(labels)

        # Combine into single tensors and then convert to NumPy
        x = torch.cat(x_list).numpy()
        y = torch.cat(y_list).numpy()

        return x, y