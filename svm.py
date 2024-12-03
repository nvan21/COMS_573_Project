from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import accuracy_score
from scipy.stats import uniform

from torch.utils.data import DataLoader
import torch
import numpy as np

from model import BaseModel


class SVM(BaseModel):
    def __init__(self):
        super().__init__()
        self.param_distributions = {
            "C": uniform(
                0.1, 100
            ),  # C parameter: uniform distribution between 0.1 and 100
            "gamma": uniform(
                0.01, 1
            ),  # gamma parameter: uniform distribution between 0.01 and 1
            "kernel": ["linear", "rbf", "poly", "sigmoid"],  # kernel choices
        }

    def model_init(self):
        self.grid_search = RandomizedSearchCV(
            SVC(),
            param_distributions=self.param_distributions,
            cv=5,
            n_iter=10,
            scoring="accuracy",
            verbose=2,
            random_state=42,
            n_jobs=1,
        )
        self.model: SVC = None

    def train(self, train_loader: DataLoader, validate_loader: DataLoader):
        X_train, y_train = self._loader_to_numpy(loader=train_loader)
        X_validate, y_validate = self._loader_to_numpy(loader=validate_loader)

        X = np.vstack((X_train, X_validate))
        y = np.hstack((y_train, y_validate))

        # Find the best model hyperparameters
        self.grid_search.fit(X=X, y=y)

        # Select the best model
        self.model = self.grid_search.best_estimator_

    def eval(self, test_loader: DataLoader):
        # Predict on the test set
        X_test, y_test = self._loader_to_numpy(loader=test_loader)
        y_test_pred = self.model.predict(X=X_test)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        print(f"Test accuracy with best model: {test_accuracy}")

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
