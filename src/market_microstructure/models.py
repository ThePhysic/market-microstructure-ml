"""Small, fixed comparison models with fold-local preprocessing.

Factories return a fresh unfitted estimator on every call. A caller must fit
each estimator only on the training indices from an audited temporal fold.
The functions here do not read market files, select settings, or save weights.
"""

from __future__ import annotations

from collections.abc import Callable
from numbers import Integral
from typing import Any

from sklearn.base import BaseEstimator
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

MODEL_ORDER = ("majority", "logistic", "boosted")


def _validated_seed(seed: int) -> int:
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise ValueError("seed must be an integer between 0 and 2**32 - 1")
    if not 0 <= seed < 2**32:
        raise ValueError("seed must be an integer between 0 and 2**32 - 1")
    return int(seed)


def model_specifications(seed: int = 42) -> dict[str, dict[str, Any]]:
    """Return the fixed, JSON-compatible settings used by the factories.

    These are predeclared configurations, not results of a parameter search.
    No automatic validation split is used by the boosted model.
    """
    seed = _validated_seed(seed)
    return {
        "majority": {
            "class": "DummyClassifier",
            "strategy": "most_frequent",
            "random_state": seed,
            "preprocessing": {"imputer": "median", "keep_empty_features": True},
        },
        "logistic": {
            "class": "LogisticRegression",
            "C": 1.0,
            "max_iter": 1000,
            "solver": "lbfgs",
            "random_state": seed,
            "preprocessing": {
                "imputer": "median",
                "keep_empty_features": True,
                "scaler": "StandardScaler",
            },
        },
        "boosted": {
            "class": "HistGradientBoostingClassifier",
            "learning_rate": 0.1,
            "max_iter": 100,
            "max_leaf_nodes": 7,
            "max_depth": 3,
            "min_samples_leaf": 30,
            "l2_regularization": 1.0,
            "early_stopping": False,
            "random_state": seed,
            "preprocessing": {"imputer": "median", "keep_empty_features": True},
        },
    }


def model_factories(seed: int = 42) -> dict[str, Callable[[], BaseEstimator]]:
    """Return independent B0/B1/B2 pipelines in a stable order.

    Imputation and scaling are deliberately inside the estimator Pipeline.
    Logistic regression needs at least two training classes; callers should
    report an infeasible training fold instead of silently swapping models.
    """
    seed = _validated_seed(seed)

    def majority() -> Pipeline:
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
                ("classifier", DummyClassifier(strategy="most_frequent", random_state=seed)),
            ]
        )

    def logistic() -> Pipeline:
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        C=1.0,
                        max_iter=1000,
                        solver="lbfgs",
                        random_state=seed,
                    ),
                ),
            ]
        )

    def boosted() -> Pipeline:
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
                (
                    "classifier",
                    HistGradientBoostingClassifier(
                        learning_rate=0.1,
                        max_iter=100,
                        max_leaf_nodes=7,
                        max_depth=3,
                        min_samples_leaf=30,
                        l2_regularization=1.0,
                        early_stopping=False,
                        random_state=seed,
                    ),
                ),
            ]
        )

    return {"majority": majority, "logistic": logistic, "boosted": boosted}
