# Quantitative research and simulation

HISTORICAL RESEARCH — hypothetical execution only

Experiment: pilot-5b363cb7828541a9

## Research

```json
{
  "schema_version": 1,
  "stage": "pilot",
  "config": {
    "schema_version": 1,
    "stage": "pilot",
    "dates": [
      "2021-01-01",
      "2021-02-01",
      "2021-03-01",
      "2021-04-01",
      "2021-05-01",
      "2021-06-01",
      "2021-07-01",
      "2021-08-01",
      "2021-09-01",
      "2021-10-01",
      "2021-11-01",
      "2021-12-01",
      "2022-01-01",
      "2022-02-01",
      "2022-03-01",
      "2022-04-01",
      "2022-05-01",
      "2022-06-01",
      "2022-07-01",
      "2022-08-01",
      "2022-09-01",
      "2022-10-01",
      "2022-11-01",
      "2022-12-01",
      "2023-01-01",
      "2023-02-01",
      "2023-03-01",
      "2023-04-01",
      "2023-05-01",
      "2023-06-01",
      "2023-07-01",
      "2023-08-01",
      "2023-09-01",
      "2023-10-01",
      "2023-11-01",
      "2023-12-01",
      "2024-01-01",
      "2024-02-01",
      "2024-03-01",
      "2024-04-01",
      "2024-05-01",
      "2024-06-01",
      "2024-07-01",
      "2024-08-01",
      "2024-09-01",
      "2024-10-01",
      "2024-11-01",
      "2024-12-01"
    ],
    "initial_train_dates": 12,
    "development_dates": [
      "2022-01-01",
      "2022-02-01",
      "2022-03-01",
      "2022-04-01",
      "2022-05-01",
      "2022-06-01",
      "2022-07-01",
      "2022-08-01",
      "2022-09-01",
      "2022-10-01",
      "2022-11-01",
      "2022-12-01"
    ],
    "final_dates": [
      "2023-01-01",
      "2023-02-01",
      "2023-03-01",
      "2023-04-01",
      "2023-05-01",
      "2023-06-01",
      "2023-07-01",
      "2023-08-01",
      "2023-09-01",
      "2023-10-01",
      "2023-11-01",
      "2023-12-01",
      "2024-01-01",
      "2024-02-01",
      "2024-03-01",
      "2024-04-01",
      "2024-05-01",
      "2024-06-01",
      "2024-07-01",
      "2024-08-01",
      "2024-09-01",
      "2024-10-01",
      "2024-11-01",
      "2024-12-01"
    ],
    "exchange": "bitstamp",
    "symbol": "BTCUSD",
    "horizon_events": 10,
    "threshold_ticks": 1.0,
    "tick_size": 0.01,
    "trailing_window": 20,
    "seed": 42,
    "practical_delta": 0.01,
    "confidence": 0.95,
    "block_length_dates": 3,
    "precision_half_width": 0.015,
    "min_final_blocks": 8,
    "n_resamples": 2000,
    "protocol_sha256": "31c4eec155c2c644779d698f20f6c56993b82e5edba241f95934fa6d045f2022",
    "frozen_source_revision": "88815b429685dd7bd29ac841a6cb245e54e86426",
    "final_scoring_authorized": false,
    "precision_gate_status": "pending",
    "target_position": "0.001",
    "max_holding_events": 10,
    "inference_delay_us": 0
  },
  "coverage": {
    "expected_dates": [
      "2021-01-01",
      "2021-02-01",
      "2021-03-01",
      "2021-04-01",
      "2021-05-01",
      "2021-06-01",
      "2021-07-01",
      "2021-08-01",
      "2021-09-01",
      "2021-10-01",
      "2021-11-01",
      "2021-12-01",
      "2022-01-01",
      "2022-02-01",
      "2022-03-01",
      "2022-04-01",
      "2022-05-01",
      "2022-06-01",
      "2022-07-01",
      "2022-08-01",
      "2022-09-01",
      "2022-10-01",
      "2022-11-01",
      "2022-12-01",
      "2023-01-01",
      "2023-02-01",
      "2023-03-01",
      "2023-04-01",
      "2023-05-01",
      "2023-06-01",
      "2023-07-01",
      "2023-08-01",
      "2023-09-01",
      "2023-10-01",
      "2023-11-01",
      "2023-12-01",
      "2024-01-01",
      "2024-02-01",
      "2024-03-01",
      "2024-04-01",
      "2024-05-01",
      "2024-06-01",
      "2024-07-01",
      "2024-08-01",
      "2024-09-01",
      "2024-10-01",
      "2024-11-01",
      "2024-12-01"
    ],
    "observed_dates": [
      "2021-01-01",
      "2021-02-01",
      "2021-03-01",
      "2021-04-01",
      "2021-05-01",
      "2021-06-01",
      "2021-07-01",
      "2021-08-01",
      "2021-09-01",
      "2021-10-01",
      "2021-11-01",
      "2021-12-01",
      "2022-01-01",
      "2022-02-01",
      "2022-03-01",
      "2022-04-01",
      "2022-05-01",
      "2022-06-01",
      "2022-07-01",
      "2022-08-01",
      "2022-09-01",
      "2022-10-01",
      "2022-11-01",
      "2022-12-01",
      "2023-01-01",
      "2023-02-01",
      "2023-03-01",
      "2023-04-01",
      "2023-05-01",
      "2023-06-01",
      "2023-07-01",
      "2023-08-01",
      "2023-09-01",
      "2023-10-01",
      "2023-11-01",
      "2023-12-01",
      "2024-01-01",
      "2024-02-01",
      "2024-03-01",
      "2024-04-01",
      "2024-05-01",
      "2024-06-01",
      "2024-07-01",
      "2024-08-01",
      "2024-09-01",
      "2024-10-01",
      "2024-11-01",
      "2024-12-01"
    ],
    "labelled_dates": [
      "2021-01-01",
      "2021-02-01",
      "2021-03-01",
      "2021-04-01",
      "2021-05-01",
      "2021-06-01",
      "2021-07-01",
      "2021-08-01",
      "2021-09-01",
      "2021-10-01",
      "2021-11-01",
      "2021-12-01",
      "2022-01-01",
      "2022-02-01",
      "2022-03-01",
      "2022-04-01",
      "2022-05-01",
      "2022-06-01",
      "2022-07-01",
      "2022-08-01",
      "2022-09-01",
      "2022-10-01",
      "2022-11-01",
      "2022-12-01"
    ],
    "reserved_final_dates": [
      "2023-01-01",
      "2023-02-01",
      "2023-03-01",
      "2023-04-01",
      "2023-05-01",
      "2023-06-01",
      "2023-07-01",
      "2023-08-01",
      "2023-09-01",
      "2023-10-01",
      "2023-11-01",
      "2023-12-01",
      "2024-01-01",
      "2024-02-01",
      "2024-03-01",
      "2024-04-01",
      "2024-05-01",
      "2024-06-01",
      "2024-07-01",
      "2024-08-01",
      "2024-09-01",
      "2024-10-01",
      "2024-11-01",
      "2024-12-01"
    ]
  },
  "feature_columns": {
    "history_logistic": [
      "mid_change_1_ticks",
      "mid_change_window_ticks",
      "mid_volatility_ticks"
    ],
    "book_models": [
      "spread_ticks",
      "level1_imbalance",
      "depth5_imbalance",
      "bid_depth5",
      "ask_depth5",
      "mid_change_1_ticks",
      "mid_change_window_ticks",
      "mid_volatility_ticks",
      "spread_change_1_ticks",
      "imbalance_change_1"
    ]
  },
  "model_specifications": {
    "majority": {
      "class": "DummyClassifier",
      "strategy": "most_frequent",
      "random_state": 42,
      "preprocessing": {
        "imputer": "median",
        "keep_empty_features": true
      }
    },
    "logistic": {
      "class": "LogisticRegression",
      "C": 1.0,
      "max_iter": 1000,
      "solver": "lbfgs",
      "random_state": 42,
      "preprocessing": {
        "imputer": "median",
        "keep_empty_features": true,
        "scaler": "StandardScaler"
      }
    },
    "boosted": {
      "class": "HistGradientBoostingClassifier",
      "learning_rate": 0.1,
      "max_iter": 100,
      "max_leaf_nodes": 7,
      "max_depth": 3,
      "min_samples_leaf": 30,
      "l2_regularization": 1.0,
      "early_stopping": false,
      "random_state": 42,
      "preprocessing": {
        "imputer": "median",
        "keep_empty_features": true
      }
    }
  },
  "quality": {
    "input_rows": 294074,
    "retained_samples": 288314,
    "excluded_samples": 5760,
    "exclusions": {
      "insufficient_history": 3840,
      "future_unavailable": 1920
    },
    "segments": 192,
    "horizon_events": 10,
    "threshold_ticks": 1.0,
    "tick_size": 0.01,
    "trailing_window": 20,
    "zero_l1_denominator_states": 0,
    "zero_depth_denominator_states": 0,
    "zero_denominator_policy": "Use zero imbalance when both opposing sizes/depths are zero.",
    "information_time": "receive_time_us; ties retain ascending source_order",
    "volatility_definition": "Population std(ddof=0) of the last trailing_window one-state mid-price changes in ticks.",
    "feature_columns": [
      "spread_ticks",
      "level1_imbalance",
      "depth5_imbalance",
      "bid_depth5",
      "ask_depth5",
      "mid_change_1_ticks",
      "mid_change_window_ticks",
      "mid_volatility_ticks",
      "spread_change_1_ticks",
      "imbalance_change_1"
    ],
    "target_arithmetic": "exact Decimal quote-grid integers; midpoint changes in integer half-ticks",
    "threshold_half_ticks": "2.0",
    "target_boundary_policy": "Exact equality at either threshold is unchanged.",
    "target_class_support": {
      "-1": 133665,
      "0": 19609,
      "1": 135040
    },
    "causal_execution_decisions": 290234,
    "execution_tail_policy": "Emit decisions after warm-up including all last-horizon states; future target availability only restricts training and classification metrics."
  },
  "development": {
    "schedule": "expanding earlier-date development fits",
    "folds": [
      {
        "name": "development_01",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01"
        ],
        "test_dates": [
          "2022-01-01"
        ],
        "train_count": 159611,
        "test_count": 9630,
        "execution_decision_count": 9710,
        "purged_count": 0,
        "audit": {
          "name": "development_01",
          "train_rows": 159611,
          "test_rows": 9630,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01"
          ],
          "test_dates": [
            "2022-01-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1640995209980260,
          "max_train_label_end_us": 1638393299575927,
          "first_evaluation_order": 1927433,
          "max_train_label_end_order": 1909547,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "73b62ba4c3555d441cfb5180841eb0f8946effff1b172b2ccbb0f40d1a2a1a16",
          "test_index_sha256": "19817cccada4ddab554fa71dee5e9c179269325807221a645c73a9864a3d9d36",
          "train_feature_order_sha256": "1f4b564e77962c7f00a0ae86f85f29af0fbfb9fb9ab97da339ad48570a2be1c5",
          "test_feature_order_sha256": "94bb9a1df0b06f424f6c53252e63ab5109588808c6b1df0b0e457891acc78952"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.22897918371057177,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.5231568016614746,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 4159
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 433
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5231568016614746,
                "recall": 1.0,
                "f1": 0.6869375511317153,
                "support": 5038
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                4159
              ],
              [
                0,
                0,
                433
              ],
              [
                0,
                0,
                5038
              ]
            ],
            "support": 9630,
            "correct": 5038,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.33922514267769976,
            "balanced_accuracy": 0.3542886199213142,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3542886199213142,
            "accuracy": 0.5256490134994808,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.49393723252496435,
                "recall": 0.33301274344794424,
                "f1": 0.3978170328881229,
                "support": 4159
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 433
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5386756519191327,
                "recall": 0.7298531163159984,
                "f1": 0.6198583951449764,
                "support": 5038
              }
            ],
            "confusion_matrix": [
              [
                1385,
                0,
                2774
              ],
              [
                58,
                0,
                375
              ],
              [
                1361,
                0,
                3677
              ]
            ],
            "support": 9630,
            "correct": 5062,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.34048779489237724,
            "balanced_accuracy": 0.35257991956354195,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.35257991956354195,
            "accuracy": 0.49179646936656285,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.45342155667769457,
                "recall": 0.6261120461649435,
                "f1": 0.5259543526560291,
                "support": 4159
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.2857142857142857,
                "recall": 0.009237875288683603,
                "f1": 0.017897091722595078,
                "support": 433
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.549444874774077,
                "recall": 0.4223898372369988,
                "f1": 0.47761194029850745,
                "support": 5038
              }
            ],
            "confusion_matrix": [
              [
                2604,
                0,
                1555
              ],
              [
                239,
                4,
                190
              ],
              [
                2900,
                10,
                2128
              ]
            ],
            "support": 9630,
            "correct": 4736,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3428650692234496,
            "balanced_accuracy": 0.3595292909417798,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3595292909417798,
            "accuracy": 0.5044652128764279,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4606931530008453,
                "recall": 0.6552055782640057,
                "f1": 0.5409966249751836,
                "support": 4159
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 433
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5747776879547292,
                "recall": 0.42338229456133386,
                "f1": 0.48759858269516515,
                "support": 5038
              }
            ],
            "confusion_matrix": [
              [
                2725,
                2,
                1432
              ],
              [
                287,
                0,
                146
              ],
              [
                2903,
                2,
                2133
              ]
            ],
            "support": 9630,
            "correct": 4858,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_02",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01"
        ],
        "test_dates": [
          "2022-02-01"
        ],
        "train_count": 169241,
        "test_count": 11911,
        "execution_decision_count": 11991,
        "purged_count": 0,
        "audit": {
          "name": "development_02",
          "train_rows": 169241,
          "test_rows": 11911,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01"
          ],
          "test_dates": [
            "2022-02-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1643673614317079,
          "max_train_label_end_us": 1641071699560021,
          "first_evaluation_order": 2045067,
          "max_train_label_end_order": 2032366,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "017cceb3fe131a607377255bf464a4b526698ea762e923740e0520fb08830395",
          "test_index_sha256": "af554e362b29c4d8d35d2a5214d77cffe1db9abca0dd430d525e2855692beafe",
          "train_feature_order_sha256": "3457fddf18e1d738d2c97ea28d48c7a9864fec251e5faca3614df5ec5a5ac3b9",
          "test_feature_order_sha256": "6568ce9305cf27eb0b3a8a4578b0a5c08640cd5888ddd0b18b85cfa974f11f61"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.21431012874558505,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.4737637477961548,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 5727
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 541
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4737637477961548,
                "recall": 1.0,
                "f1": 0.6429303862367551,
                "support": 5643
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                5727
              ],
              [
                0,
                0,
                541
              ],
              [
                0,
                0,
                5643
              ]
            ],
            "support": 11911,
            "correct": 5643,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3096928826374232,
            "balanced_accuracy": 0.3365301500634595,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3365301500634595,
            "accuracy": 0.48022836033918226,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5001603077909587,
                "recall": 0.2723939235201676,
                "f1": 0.35270178611801944,
                "support": 5727
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 541
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4731574158325751,
                "recall": 0.7371965266702108,
                "f1": 0.5763768617942501,
                "support": 5643
              }
            ],
            "confusion_matrix": [
              [
                1560,
                0,
                4167
              ],
              [
                76,
                0,
                465
              ],
              [
                1483,
                0,
                4160
              ]
            ],
            "support": 11911,
            "correct": 5720,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3163710848959684,
            "balanced_accuracy": 0.3299849886103367,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3299849886103367,
            "accuracy": 0.4715808916127949,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.47675478577939834,
                "recall": 0.36528723590012224,
                "f1": 0.41364310430054374,
                "support": 5727
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 541
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4685630732420577,
                "recall": 0.6246677299308878,
                "f1": 0.5354701503873613,
                "support": 5643
              }
            ],
            "confusion_matrix": [
              [
                2092,
                0,
                3635
              ],
              [
                178,
                0,
                363
              ],
              [
                2118,
                0,
                3525
              ]
            ],
            "support": 11911,
            "correct": 5617,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3445168417872315,
            "balanced_accuracy": 0.35297454215230584,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.35297454215230584,
            "accuracy": 0.5051632944337168,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5160525355709595,
                "recall": 0.4939759036144578,
                "f1": 0.5047729503077883,
                "support": 5727
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 541
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4969602494154326,
                "recall": 0.5649477228424596,
                "f1": 0.5287775750539061,
                "support": 5643
              }
            ],
            "confusion_matrix": [
              [
                2829,
                4,
                2894
              ],
              [
                208,
                0,
                333
              ],
              [
                2445,
                10,
                3188
              ]
            ],
            "support": 11911,
            "correct": 6017,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_03",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01"
        ],
        "test_dates": [
          "2022-03-01"
        ],
        "train_count": 181152,
        "test_count": 13383,
        "execution_decision_count": 13463,
        "purged_count": 0,
        "audit": {
          "name": "development_03",
          "train_rows": 181152,
          "test_rows": 13383,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01"
          ],
          "test_dates": [
            "2022-03-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1646092810213289,
          "max_train_label_end_us": 1643750099805042,
          "first_evaluation_order": 2181662,
          "max_train_label_end_order": 2167494,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "547e7d7f12241e3b4975eb2b6658ee75245e6bd015c5ae41bf1e2cd3faf7676f",
          "test_index_sha256": "b71832ae1128083ff756cf1b7bf93ac01d2f647cf5abbeece3811ae0bc3006e2",
          "train_feature_order_sha256": "d2b7c25845b4cc7e02e3c5fce726dcacdfab9067fc63a3bbee0208ca6d920b7a",
          "test_feature_order_sha256": "222f10bef949a0820631ba97a3ba821b631606e847911bed58b373b42afc0bcf"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.21020498652750774,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.46050960173354255,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 6700
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 520
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.46050960173354255,
                "recall": 1.0,
                "f1": 0.6306149595825232,
                "support": 6163
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                6700
              ],
              [
                0,
                0,
                520
              ],
              [
                0,
                0,
                6163
              ]
            ],
            "support": 13383,
            "correct": 6163,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.33369043812052296,
            "balanced_accuracy": 0.35236097623193463,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.35236097623193463,
            "accuracy": 0.5011581857580513,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5453718444393905,
                "recall": 0.357910447761194,
                "f1": 0.43218887987744437,
                "support": 6700
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 520
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4795237035388382,
                "recall": 0.6991724809346098,
                "f1": 0.5688824344841243,
                "support": 6163
              }
            ],
            "confusion_matrix": [
              [
                2398,
                0,
                4302
              ],
              [
                145,
                0,
                375
              ],
              [
                1854,
                0,
                4309
              ]
            ],
            "support": 13383,
            "correct": 6707,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3473275162185048,
            "balanced_accuracy": 0.35436281193416336,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.35436281193416336,
            "accuracy": 0.511469775087798,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5286127167630058,
                "recall": 0.5459701492537313,
                "f1": 0.537151248164464,
                "support": 6700
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 520
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4931146526380938,
                "recall": 0.5171182865487587,
                "f1": 0.5048313004910502,
                "support": 6163
              }
            ],
            "confusion_matrix": [
              [
                3658,
                0,
                3042
              ],
              [
                286,
                0,
                234
              ],
              [
                2976,
                0,
                3187
              ]
            ],
            "support": 13383,
            "correct": 6845,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3624112750375867,
            "balanced_accuracy": 0.36973655170520914,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.36973655170520914,
            "accuracy": 0.5341104386161548,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5523701390860063,
                "recall": 0.5808955223880597,
                "f1": 0.56627382511276,
                "support": 6700
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 520
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5138077954868234,
                "recall": 0.5283141327275678,
                "f1": 0.52096,
                "support": 6163
              }
            ],
            "confusion_matrix": [
              [
                3892,
                0,
                2808
              ],
              [
                247,
                0,
                273
              ],
              [
                2907,
                0,
                3256
              ]
            ],
            "support": 13383,
            "correct": 7148,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_04",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01"
        ],
        "test_dates": [
          "2022-04-01"
        ],
        "train_count": 194535,
        "test_count": 11773,
        "execution_decision_count": 11853,
        "purged_count": 0,
        "audit": {
          "name": "development_04",
          "train_rows": 194535,
          "test_rows": 11773,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01"
          ],
          "test_dates": [
            "2022-04-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1648771214471667,
          "max_train_label_end_us": 1646169299854719,
          "first_evaluation_order": 2341235,
          "max_train_label_end_order": 2324738,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "6b32865196a76fc5aca36a3d4639246a62ade2ddc615a6143085b207413ac221",
          "test_index_sha256": "38b923b2e58319d0a39e6d93ca85e7fa091735a2822bbf4e01c8a5d4a2eef218",
          "train_feature_order_sha256": "87447267cd2b3f529f2185ad39681283616bae5655bf54b1277b6a3c06baf102",
          "test_feature_order_sha256": "5e1754d0e0a62ab2364e4a1b56d4c671a93017e0c628e26c19289cf197c97676"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.22496107453054948,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.5093009428353011,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 5406
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5093009428353011,
                "recall": 1.0,
                "f1": 0.6748832235916484,
                "support": 5996
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                5406
              ],
              [
                0,
                0,
                371
              ],
              [
                0,
                0,
                5996
              ]
            ],
            "support": 11773,
            "correct": 5996,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.349092915971925,
            "balanced_accuracy": 0.35996964227641876,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.35996964227641876,
            "accuracy": 0.5307907924912937,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5172241637543684,
                "recall": 0.38327783943766186,
                "f1": 0.44028899277518063,
                "support": 5406
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5377880777649028,
                "recall": 0.6966310873915944,
                "f1": 0.6069897551405944,
                "support": 5996
              }
            ],
            "confusion_matrix": [
              [
                2072,
                0,
                3334
              ],
              [
                115,
                0,
                256
              ],
              [
                1819,
                0,
                4177
              ]
            ],
            "support": 11773,
            "correct": 6249,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3552275465093624,
            "balanced_accuracy": 0.36113416672487125,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.36113416672487125,
            "accuracy": 0.525014864520513,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.496816382722423,
                "recall": 0.5340362560118387,
                "f1": 0.5147543906570384,
                "support": 5406
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5524991613552499,
                "recall": 0.5493662441627751,
                "f1": 0.5509282488710486,
                "support": 5996
              }
            ],
            "confusion_matrix": [
              [
                2887,
                0,
                2519
              ],
              [
                222,
                0,
                149
              ],
              [
                2702,
                0,
                3294
              ]
            ],
            "support": 11773,
            "correct": 6181,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.371574917731141,
            "balanced_accuracy": 0.3779620910590206,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3779620910590206,
            "accuracy": 0.5487980973413743,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.520868394479973,
                "recall": 0.5725120236773955,
                "f1": 0.5454705675008812,
                "support": 5406
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5773584905660377,
                "recall": 0.5613742494996664,
                "f1": 0.5692541856925418,
                "support": 5996
              }
            ],
            "confusion_matrix": [
              [
                3095,
                0,
                2311
              ],
              [
                218,
                0,
                153
              ],
              [
                2629,
                1,
                3366
              ]
            ],
            "support": 11773,
            "correct": 6461,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_05",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01"
        ],
        "test_dates": [
          "2022-05-01"
        ],
        "train_count": 206308,
        "test_count": 9575,
        "execution_decision_count": 9655,
        "purged_count": 0,
        "audit": {
          "name": "development_05",
          "train_rows": 206308,
          "test_rows": 9575,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01"
          ],
          "test_dates": [
            "2022-05-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1651363214016727,
          "max_train_label_end_us": 1648847699839220,
          "first_evaluation_order": 2476258,
          "max_train_label_end_order": 2462457,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "889a673d355873bde91b49295a346cd1e7f8a20e510f83d4adca9547b7943058",
          "test_index_sha256": "2db8ec15aed0eabbd8d6647a58811dd84a3521a953dccc2d768fd1d4f28e81ee",
          "train_feature_order_sha256": "5dec6db704066948271b6bf7b3591671aae9370cc835485164e0bf97cc470a3e",
          "test_feature_order_sha256": "84ef0fbe1ba21e7c5c943c1f16fed84dc2e54ac7570e46061cea9dbe19fb033b"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.21583445158556394,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.4787467362924282,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 4428
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 563
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4787467362924282,
                "recall": 1.0,
                "f1": 0.6475033547566919,
                "support": 4584
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                4428
              ],
              [
                0,
                0,
                563
              ],
              [
                0,
                0,
                4584
              ]
            ],
            "support": 9575,
            "correct": 4584,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3232512086438242,
            "balanced_accuracy": 0.3480475271593903,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3480475271593903,
            "accuracy": 0.49493472584856396,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5081285444234405,
                "recall": 0.3035230352303523,
                "f1": 0.3800367595079881,
                "support": 4428
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 563
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4898989898989899,
                "recall": 0.7406195462478184,
                "f1": 0.5897168664234844,
                "support": 4584
              }
            ],
            "confusion_matrix": [
              [
                1344,
                0,
                3084
              ],
              [
                112,
                0,
                451
              ],
              [
                1189,
                0,
                3395
              ]
            ],
            "support": 9575,
            "correct": 4739,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.34310257833626195,
            "balanced_accuracy": 0.3539771894228541,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3539771894228541,
            "accuracy": 0.5002610966057441,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4887267904509284,
                "recall": 0.4993224932249323,
                "f1": 0.49396782841823056,
                "support": 4428
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 563
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5105919619877252,
                "recall": 0.56260907504363,
                "f1": 0.5353399065905553,
                "support": 4584
              }
            ],
            "confusion_matrix": [
              [
                2211,
                0,
                2217
              ],
              [
                308,
                0,
                255
              ],
              [
                2005,
                0,
                2579
              ]
            ],
            "support": 9575,
            "correct": 4790,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3672532297703608,
            "balanced_accuracy": 0.368043002775003,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.368043002775003,
            "accuracy": 0.5066318537859008,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.494566375452802,
                "recall": 0.5241644083107497,
                "f1": 0.5089354237473961,
                "support": 4428
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.4864864864864865,
                "recall": 0.03197158081705151,
                "f1": 0.06,
                "support": 563
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5184726522187822,
                "recall": 0.5479930191972077,
                "f1": 0.5328242655636864,
                "support": 4584
              }
            ],
            "confusion_matrix": [
              [
                2321,
                18,
                2089
              ],
              [
                301,
                18,
                244
              ],
              [
                2071,
                1,
                2512
              ]
            ],
            "support": 9575,
            "correct": 4851,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_06",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01"
        ],
        "test_dates": [
          "2022-06-01"
        ],
        "train_count": 215883,
        "test_count": 8674,
        "execution_decision_count": 8754,
        "purged_count": 0,
        "audit": {
          "name": "development_06",
          "train_rows": 215883,
          "test_rows": 8674,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01"
          ],
          "test_dates": [
            "2022-06-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1654041636005988,
          "max_train_label_end_us": 1651439699620252,
          "first_evaluation_order": 2588906,
          "max_train_label_end_order": 2575187,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "22ea332111d59c28518869105c4f98c4e02914783df5646f949523f35455b9ea",
          "test_index_sha256": "4799c195a31e75ac16a9fc9c1bd50dd26ad5b04a7038af961c2aac83cc9b1e39",
          "train_feature_order_sha256": "f5ffc8ac658a4f0f9dbf54beb4e0436a389c003c9939a5c993bddae23de5a4fb",
          "test_feature_order_sha256": "480261f798df3f1c7b434aa2a86d15367158a84a062568254ae66c6a206abbdd"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.21123099944868864,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.4637998616555222,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 4077
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 574
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4637998616555222,
                "recall": 1.0,
                "f1": 0.633692998346066,
                "support": 4023
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                4077
              ],
              [
                0,
                0,
                574
              ],
              [
                0,
                0,
                4023
              ]
            ],
            "support": 8674,
            "correct": 4023,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.33089075093689607,
            "balanced_accuracy": 0.35943819725321124,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.35943819725321124,
            "accuracy": 0.5020751671662439,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5489270386266094,
                "recall": 0.3137110620554329,
                "f1": 0.39925081941626345,
                "support": 4077
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 574
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4848675914249685,
                "recall": 0.7646035297042009,
                "f1": 0.5934214333944247,
                "support": 4023
              }
            ],
            "confusion_matrix": [
              [
                1279,
                0,
                2798
              ],
              [
                104,
                0,
                470
              ],
              [
                947,
                0,
                3076
              ]
            ],
            "support": 8674,
            "correct": 4355,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3328191253373316,
            "balanced_accuracy": 0.3479265745144229,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3479265745144229,
            "accuracy": 0.486741987548997,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4873024830699774,
                "recall": 0.42359578121167524,
                "f1": 0.45322136202598085,
                "support": 4077
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 574
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.48644960031195167,
                "recall": 0.6201839423315934,
                "f1": 0.545236013986014,
                "support": 4023
              }
            ],
            "confusion_matrix": [
              [
                1727,
                0,
                2350
              ],
              [
                290,
                0,
                284
              ],
              [
                1527,
                1,
                2495
              ]
            ],
            "support": 8674,
            "correct": 4222,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3896852057316726,
            "balanced_accuracy": 0.38967154604308485,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.38967154604308485,
            "accuracy": 0.5259395895780493,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5392464678178964,
                "recall": 0.5055187637969095,
                "f1": 0.5218382073680212,
                "support": 4077
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.30434782608695654,
                "recall": 0.04878048780487805,
                "f1": 0.08408408408408409,
                "support": 574
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5195378151260505,
                "recall": 0.614715386527467,
                "f1": 0.5631333257429124,
                "support": 4023
              }
            ],
            "confusion_matrix": [
              [
                2061,
                17,
                1999
              ],
              [
                258,
                28,
                288
              ],
              [
                1503,
                47,
                2473
              ]
            ],
            "support": 8674,
            "correct": 4562,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_07",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01"
        ],
        "test_dates": [
          "2022-07-01"
        ],
        "train_count": 224557,
        "test_count": 11401,
        "execution_decision_count": 11481,
        "purged_count": 0,
        "audit": {
          "name": "development_07",
          "train_rows": 224557,
          "test_rows": 11401,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01",
            "2022-06-01"
          ],
          "test_dates": [
            "2022-07-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1656633610176813,
          "max_train_label_end_us": 1654118095293269,
          "first_evaluation_order": 2704023,
          "max_train_label_end_order": 2691935,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "3d692118d5475ee5b55c71e80b1eae6a959c1298ec192c958743e57440da0fbe",
          "test_index_sha256": "cdb0d27f968e86c8d52b405ac14fa319dc8ad1940ad027b64ddfbc770d22e4b8",
          "train_feature_order_sha256": "41e79231a322fa67cb927ef4ab31bc328567ce2a025c073fb83d5053770dfeea",
          "test_feature_order_sha256": "3badc55bae927a28cab500ebf327d9834e1969fabfcc36df92bec81d43d15c6d"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.21724219489120153,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.4833786509955267,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 5519
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4833786509955267,
                "recall": 1.0,
                "f1": 0.6517265846736046,
                "support": 5511
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                5519
              ],
              [
                0,
                0,
                371
              ],
              [
                0,
                0,
                5511
              ]
            ],
            "support": 11401,
            "correct": 5511,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3004952841976729,
            "balanced_accuracy": 0.3244377947011094,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3244377947011094,
            "accuracy": 0.47066046837996667,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4668192219679634,
                "recall": 0.25874252581989493,
                "f1": 0.3329447423641875,
                "support": 5519
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.47206904818988255,
                "recall": 0.7145708582834331,
                "f1": 0.5685411102288312,
                "support": 5511
              }
            ],
            "confusion_matrix": [
              [
                1428,
                0,
                4091
              ],
              [
                58,
                0,
                313
              ],
              [
                1573,
                0,
                3938
              ]
            ],
            "support": 11401,
            "correct": 5366,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.32194984759923023,
            "balanced_accuracy": 0.3274604491456889,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3274604491456889,
            "accuracy": 0.4752214718007192,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4733668341708543,
                "recall": 0.5120492842906323,
                "f1": 0.49194882061101924,
                "support": 5519
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.47752394988946206,
                "recall": 0.4703320631464344,
                "f1": 0.47390072218667156,
                "support": 5511
              }
            ],
            "confusion_matrix": [
              [
                2826,
                3,
                2690
              ],
              [
                225,
                0,
                146
              ],
              [
                2919,
                0,
                2592
              ]
            ],
            "support": 11401,
            "correct": 5418,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3675055578211854,
            "balanced_accuracy": 0.3650307136321464,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3650307136321464,
            "accuracy": 0.4871502499780721,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4948799106311674,
                "recall": 0.4816089871353506,
                "f1": 0.4881542699724518,
                "support": 5519
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.12027491408934708,
                "recall": 0.09433962264150944,
                "f1": 0.10574018126888217,
                "support": 371
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.498518905732706,
                "recall": 0.519143531119579,
                "f1": 0.5086222222222222,
                "support": 5511
              }
            ],
            "confusion_matrix": [
              [
                2658,
                128,
                2733
              ],
              [
                191,
                35,
                145
              ],
              [
                2522,
                128,
                2861
              ]
            ],
            "support": 11401,
            "correct": 5554,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_08",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01",
          "2022-07-01"
        ],
        "test_dates": [
          "2022-08-01"
        ],
        "train_count": 235958,
        "test_count": 10188,
        "execution_decision_count": 10268,
        "purged_count": 0,
        "audit": {
          "name": "development_08",
          "train_rows": 235958,
          "test_rows": 10188,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01",
            "2022-06-01",
            "2022-07-01"
          ],
          "test_dates": [
            "2022-08-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1659312014544294,
          "max_train_label_end_us": 1656710099602181,
          "first_evaluation_order": 2845797,
          "max_train_label_end_order": 2832837,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "675ccc04073527d75917ec2a36af5f0dcc1717bb575b250034b380f7f77e527e",
          "test_index_sha256": "d21214f73a8434776307cb11fff760d93bf76262e3e52c08c00bb4c1396dc1f3",
          "train_feature_order_sha256": "a24691d6005109c78bcbfea0c930203a56db594ec8255b9f3b5354de05452ba2",
          "test_feature_order_sha256": "c491bfe1fca7928ff6adba9492f457ddc5f9c5f2c1dda15efaa48e31aeea2431"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.21953039280228218,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.49096976835492734,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 4942
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 244
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.49096976835492734,
                "recall": 1.0,
                "f1": 0.6585911784068466,
                "support": 5002
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                4942
              ],
              [
                0,
                0,
                244
              ],
              [
                0,
                0,
                5002
              ]
            ],
            "support": 10188,
            "correct": 5002,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.28738065946055974,
            "balanced_accuracy": 0.3209258317447336,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3209258317447336,
            "accuracy": 0.47153513937966235,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.44715073529411764,
                "recall": 0.19688385269121814,
                "f1": 0.27339140207923573,
                "support": 4942
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 244
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.47815776335496757,
                "recall": 0.7658936425429828,
                "f1": 0.5887505763024435,
                "support": 5002
              }
            ],
            "confusion_matrix": [
              [
                973,
                0,
                3969
              ],
              [
                32,
                0,
                212
              ],
              [
                1171,
                0,
                3831
              ]
            ],
            "support": 10188,
            "correct": 4804,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.36084040659989675,
            "balanced_accuracy": 0.35481122538169413,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.35481122538169413,
            "accuracy": 0.48802512760109934,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4790268456375839,
                "recall": 0.34662080129502226,
                "f1": 0.40220709086640055,
                "support": 4942
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.4358974358974359,
                "recall": 0.06967213114754098,
                "f1": 0.12014134275618374,
                "support": 244
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.49322987981134947,
                "recall": 0.648140743702519,
                "f1": 0.5601727861771059,
                "support": 5002
              }
            ],
            "confusion_matrix": [
              [
                1713,
                10,
                3219
              ],
              [
                115,
                17,
                112
              ],
              [
                1748,
                12,
                3242
              ]
            ],
            "support": 10188,
            "correct": 4972,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3396988983567053,
            "balanced_accuracy": 0.34391291372295,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.34391291372295,
            "accuracy": 0.5036317235963879,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5061957868649318,
                "recall": 0.49595305544314044,
                "f1": 0.5010220768601799,
                "support": 4942
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 244
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.5014970059880239,
                "recall": 0.5357856857257097,
                "f1": 0.5180746182099362,
                "support": 5002
              }
            ],
            "confusion_matrix": [
              [
                2451,
                1,
                2490
              ],
              [
                70,
                0,
                174
              ],
              [
                2321,
                1,
                2680
              ]
            ],
            "support": 10188,
            "correct": 5131,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_09",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01",
          "2022-07-01",
          "2022-08-01"
        ],
        "test_dates": [
          "2022-09-01"
        ],
        "train_count": 246146,
        "test_count": 12944,
        "execution_decision_count": 13024,
        "purged_count": 0,
        "audit": {
          "name": "development_09",
          "train_rows": 246146,
          "test_rows": 12944,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01",
            "2022-06-01",
            "2022-07-01",
            "2022-08-01"
          ],
          "test_dates": [
            "2022-09-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1661990409924324,
          "max_train_label_end_us": 1659388499175651,
          "first_evaluation_order": 2973073,
          "max_train_label_end_order": 2959797,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "c384161ee3e6acc8816f96df47549ae961005c06437f0309ce8940a09bbc37bd",
          "test_index_sha256": "d06849b439255198910106e169e537c4c353a4bf566bbd27f4a129e56a388efa",
          "train_feature_order_sha256": "29fa06562b85024ccb7c2e99cf630f964686c093f3131207349ef2367e67f1ab",
          "test_feature_order_sha256": "49e06109f0db69a459e3df859513f9b120fa2c30994d70c62ca961e15e6a5e04"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.2063127945229839,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.4481613102595797,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 5814
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 1329
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4481613102595797,
                "recall": 1.0,
                "f1": 0.6189383835689517,
                "support": 5801
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                5814
              ],
              [
                0,
                0,
                1329
              ],
              [
                0,
                0,
                5801
              ]
            ],
            "support": 12944,
            "correct": 5801,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.28702150357017614,
            "balanced_accuracy": 0.3355917603615903,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3355917603615903,
            "accuracy": 0.45140605686032137,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.46635730858468677,
                "recall": 0.20743034055727555,
                "f1": 0.28714285714285714,
                "support": 5814
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 1329
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4476732960030894,
                "recall": 0.7993449405274953,
                "f1": 0.5739216535676712,
                "support": 5801
              }
            ],
            "confusion_matrix": [
              [
                1206,
                0,
                4608
              ],
              [
                216,
                0,
                1113
              ],
              [
                1164,
                0,
                4637
              ]
            ],
            "support": 12944,
            "correct": 5843,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3051034742130348,
            "balanced_accuracy": 0.34972329834425886,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.34972329834425886,
            "accuracy": 0.47017923362175523,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4994648590795576,
                "recall": 0.24079807361541108,
                "f1": 0.3249390739236393,
                "support": 5814
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.03225806451612903,
                "recall": 0.0007524454477050414,
                "f1": 0.0014705882352941176,
                "support": 1329
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.46340257171117705,
                "recall": 0.8076193759696604,
                "f1": 0.5889007604801709,
                "support": 5801
              }
            ],
            "confusion_matrix": [
              [
                1400,
                28,
                4386
              ],
              [
                289,
                1,
                1039
              ],
              [
                1114,
                2,
                4685
              ]
            ],
            "support": 12944,
            "correct": 6086,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3837641018175509,
            "balanced_accuracy": 0.3847763133388344,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3847763133388344,
            "accuracy": 0.46446229913473425,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.5132340777502068,
                "recall": 0.4269005847953216,
                "f1": 0.4661032863849765,
                "support": 5814
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.1697019867549669,
                "recall": 0.1542513167795335,
                "f1": 0.16160819865983445,
                "support": 1329
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.48188405797101447,
                "recall": 0.573177038441648,
                "f1": 0.5235808204078419,
                "support": 5801
              }
            ],
            "confusion_matrix": [
              [
                2482,
                455,
                2877
              ],
              [
                426,
                205,
                698
              ],
              [
                1928,
                548,
                3325
              ]
            ],
            "support": 12944,
            "correct": 6012,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_10",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01",
          "2022-07-01",
          "2022-08-01",
          "2022-09-01"
        ],
        "test_dates": [
          "2022-10-01"
        ],
        "train_count": 259090,
        "test_count": 8880,
        "execution_decision_count": 8960,
        "purged_count": 0,
        "audit": {
          "name": "development_10",
          "train_rows": 259090,
          "test_rows": 8880,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01",
            "2022-06-01",
            "2022-07-01",
            "2022-08-01",
            "2022-09-01"
          ],
          "test_dates": [
            "2022-10-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1664582413764957,
          "max_train_label_end_us": 1662066899794480,
          "first_evaluation_order": 3129476,
          "max_train_label_end_order": 3113868,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "e1832630bbf8dc793d598b113404a545503c623004e35bc03752d35f49890779",
          "test_index_sha256": "98fadba57c5a6e92ada4172fad2dfd24a15b20b54911a71d5e3647502553e16d",
          "train_feature_order_sha256": "617adcf7cfffefcdcff381c3c0e91f3b19af8362dee8d6bec6a5ac41b4b12236",
          "test_feature_order_sha256": "c98009ef2a4efb7bff112285d8ac45408c75209cd59d2bc902e5211cf3f77246"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.1801446416831032,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.37027027027027026,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 3576
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 2016
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.37027027027027026,
                "recall": 1.0,
                "f1": 0.5404339250493096,
                "support": 3288
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                3576
              ],
              [
                0,
                0,
                2016
              ],
              [
                0,
                0,
                3288
              ]
            ],
            "support": 8880,
            "correct": 3288,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.23293868026811393,
            "balanced_accuracy": 0.33495811492676236,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.33495811492676236,
            "accuracy": 0.37567567567567567,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4600231749710313,
                "recall": 0.11101789709172259,
                "f1": 0.1788691146654652,
                "support": 3576
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 2016
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.3665959835349881,
                "recall": 0.8938564476885644,
                "f1": 0.5199469261388766,
                "support": 3288
              }
            ],
            "confusion_matrix": [
              [
                397,
                0,
                3179
              ],
              [
                117,
                0,
                1899
              ],
              [
                349,
                0,
                2939
              ]
            ],
            "support": 8880,
            "correct": 3336,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3477712621998932,
            "balanced_accuracy": 0.37606147181081045,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.37606147181081045,
            "accuracy": 0.41655405405405405,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4363572433192686,
                "recall": 0.3470357941834452,
                "f1": 0.3866043613707165,
                "support": 3576
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.4943502824858757,
                "recall": 0.08680555555555555,
                "f1": 0.14767932489451477,
                "support": 2016
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.40179514255543824,
                "recall": 0.6943430656934306,
                "f1": 0.5090301003344482,
                "support": 3288
              }
            ],
            "confusion_matrix": [
              [
                1241,
                67,
                2268
              ],
              [
                710,
                175,
                1131
              ],
              [
                893,
                112,
                2283
              ]
            ],
            "support": 8880,
            "correct": 3699,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.3247503226801933,
            "balanced_accuracy": 0.3574399707547089,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3574399707547089,
            "accuracy": 0.4115990990990991,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.41025223759153784,
                "recall": 0.7049776286353467,
                "f1": 0.5186709186297705,
                "support": 3576
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.46987951807228917,
                "recall": 0.05803571428571429,
                "f1": 0.10331125827814569,
                "support": 2016
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4090909090909091,
                "recall": 0.3093065693430657,
                "f1": 0.3522687911326637,
                "support": 3288
              }
            ],
            "confusion_matrix": [
              [
                2521,
                63,
                992
              ],
              [
                1422,
                117,
                477
              ],
              [
                2202,
                69,
                1017
              ]
            ],
            "support": 8880,
            "correct": 3655,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_11",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01",
          "2022-07-01",
          "2022-08-01",
          "2022-09-01",
          "2022-10-01"
        ],
        "test_dates": [
          "2022-11-01"
        ],
        "train_count": 267970,
        "test_count": 10720,
        "execution_decision_count": 10800,
        "purged_count": 0,
        "audit": {
          "name": "development_11",
          "train_rows": 267970,
          "test_rows": 10720,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01",
            "2022-06-01",
            "2022-07-01",
            "2022-08-01",
            "2022-09-01",
            "2022-10-01"
          ],
          "test_dates": [
            "2022-11-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1667260814530712,
          "max_train_label_end_us": 1664658898751234,
          "first_evaluation_order": 3236617,
          "max_train_label_end_order": 3226128,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "37fefc4e4e9911fdc2f93c290d8f3e4b02bed18bb3d335ad7a80e54ca5983179",
          "test_index_sha256": "3fe612b03f7bb8e9974853ee8f321fb3c30aecd424d2d0131d82fcb93db3aa15",
          "train_feature_order_sha256": "cf9f9f602b30460b9750cc5d5906a549f35d6bf2f3a3dc97c500874c78f79a34",
          "test_feature_order_sha256": "6e979cb2ce95df4575046efbd6a5d6db2c4954d995e7becf1d55c59f7a49db19"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.1853772420140526,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.3851679104477612,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 3926
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 2665
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.3851679104477612,
                "recall": 1.0,
                "f1": 0.5561317260421578,
                "support": 4129
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                3926
              ],
              [
                0,
                0,
                2665
              ],
              [
                0,
                0,
                4129
              ]
            ],
            "support": 10720,
            "correct": 4129,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.2518823677991422,
            "balanced_accuracy": 0.34397356586476024,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.34397356586476024,
            "accuracy": 0.39477611940298507,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4311145510835913,
                "recall": 0.14187468160978095,
                "f1": 0.21349175929474895,
                "support": 3926
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 2665
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.3897963512940178,
                "recall": 0.8900460159844998,
                "f1": 0.5421553441026776,
                "support": 4129
              }
            ],
            "confusion_matrix": [
              [
                557,
                0,
                3369
              ],
              [
                281,
                0,
                2384
              ],
              [
                454,
                0,
                3675
              ]
            ],
            "support": 10720,
            "correct": 4232,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.35987827897590496,
            "balanced_accuracy": 0.38530506863391434,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.38530506863391434,
            "accuracy": 0.4222014925373134,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.3932236520605962,
                "recall": 0.6148751910341315,
                "f1": 0.4796820665673125,
                "support": 3926
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.5199063231850117,
                "recall": 0.08330206378986867,
                "f1": 0.14359637774902975,
                "support": 2665
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.4549831487722677,
                "recall": 0.4577379510777428,
                "f1": 0.4563563926113727,
                "support": 4129
              }
            ],
            "confusion_matrix": [
              [
                2414,
                69,
                1443
              ],
              [
                1622,
                222,
                821
              ],
              [
                2103,
                136,
                1890
              ]
            ],
            "support": 10720,
            "correct": 4526,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.4191207291146181,
            "balanced_accuracy": 0.42620536537216663,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.42620536537216663,
            "accuracy": 0.43180970149253733,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.39542586750788644,
                "recall": 0.6385634233316353,
                "f1": 0.4884083382037795,
                "support": 3926
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.48715313463514903,
                "recall": 0.3557223264540338,
                "f1": 0.41119063109954457,
                "support": 2665
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.48233360723089563,
                "recall": 0.2843303463308307,
                "f1": 0.35776321804053024,
                "support": 4129
              }
            ],
            "confusion_matrix": [
              [
                2507,
                573,
                846
              ],
              [
                1303,
                948,
                414
              ],
              [
                2530,
                425,
                1174
              ]
            ],
            "support": 10720,
            "correct": 4629,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      },
      {
        "name": "development_12",
        "train_dates": [
          "2021-01-01",
          "2021-02-01",
          "2021-03-01",
          "2021-04-01",
          "2021-05-01",
          "2021-06-01",
          "2021-07-01",
          "2021-08-01",
          "2021-09-01",
          "2021-10-01",
          "2021-11-01",
          "2021-12-01",
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01",
          "2022-07-01",
          "2022-08-01",
          "2022-09-01",
          "2022-10-01",
          "2022-11-01"
        ],
        "test_dates": [
          "2022-12-01"
        ],
        "train_count": 278690,
        "test_count": 9624,
        "execution_decision_count": 9704,
        "purged_count": 0,
        "audit": {
          "name": "development_12",
          "train_rows": 278690,
          "test_rows": 9624,
          "train_dates": [
            "2021-01-01",
            "2021-02-01",
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2021-06-01",
            "2021-07-01",
            "2021-08-01",
            "2021-09-01",
            "2021-10-01",
            "2021-11-01",
            "2021-12-01",
            "2022-01-01",
            "2022-02-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01",
            "2022-06-01",
            "2022-07-01",
            "2022-08-01",
            "2022-09-01",
            "2022-10-01",
            "2022-11-01"
          ],
          "test_dates": [
            "2022-12-01"
          ],
          "purged_count": 0,
          "evaluation_boundary_us": 1669852810758387,
          "max_train_label_end_us": 1667337299604981,
          "first_evaluation_order": 3365245,
          "max_train_label_end_order": 3353339,
          "strict_time_boundary": true,
          "strict_source_order_boundary": true,
          "train_index_sha256": "49ec423ac4bb2552363aa8f6149a79e63d468eec9647083805099770a64be930",
          "test_index_sha256": "401ed6da0d0f034a656c8f8da3e27ad87b894d0aa4ac19933156986df7d9bcbc",
          "train_feature_order_sha256": "02c522cc12f7743c4e0bb62fb91238288ad9504d913ba6337ed922ef7ab97ee3",
          "test_feature_order_sha256": "c2dca70c42b1f3abcac19fdd4740fd129e6d0df6e058b361f47c42b6d0a0fd40"
        },
        "models": {
          "majority": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.14397827562797014,
            "balanced_accuracy": 0.3333333333333333,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3333333333333333,
            "accuracy": 0.2754571903574397,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 3024
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 3949
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.2754571903574397,
                "recall": 1.0,
                "f1": 0.4319348268839104,
                "support": 2651
              }
            ],
            "confusion_matrix": [
              [
                0,
                0,
                3024
              ],
              [
                0,
                0,
                3949
              ],
              [
                0,
                0,
                2651
              ]
            ],
            "support": 9624,
            "correct": 2651,
            "absent_true_classes": [],
            "unpredicted_classes": [
              -1,
              0
            ],
            "warnings": [
              "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "history_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.21687580417543625,
            "balanced_accuracy": 0.3479689621632913,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.3479689621632913,
            "accuracy": 0.29353699085619284,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4726720647773279,
                "recall": 0.15443121693121692,
                "f1": 0.23280159521435692,
                "support": 3024
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "support": 3949
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.2730430754979157,
                "recall": 0.8894756695586571,
                "f1": 0.4178258173119518,
                "support": 2651
              }
            ],
            "confusion_matrix": [
              [
                467,
                0,
                2557
              ],
              [
                228,
                0,
                3721
              ],
              [
                293,
                0,
                2358
              ]
            ],
            "support": 9624,
            "correct": 2825,
            "absent_true_classes": [],
            "unpredicted_classes": [
              0
            ],
            "warnings": [
              "No predictions for classes: 0. Undefined precision/F1 components use zero."
            ],
            "fit_warnings": []
          },
          "book_logistic": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.44188130998239505,
            "balanced_accuracy": 0.443933226231286,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.443933226231286,
            "accuracy": 0.4605153782211139,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.4463729417000445,
                "recall": 0.3316798941798942,
                "f1": 0.3805729463099981,
                "support": 3024
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.5563131906889255,
                "recall": 0.5991390225373512,
                "f1": 0.5769324554986589,
                "support": 3949
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.34026888604353395,
                "recall": 0.4009807619766126,
                "f1": 0.36813852813852815,
                "support": 2651
              }
            ],
            "confusion_matrix": [
              [
                1003,
                782,
                1239
              ],
              [
                761,
                2366,
                822
              ],
              [
                483,
                1105,
                1063
              ]
            ],
            "support": 9624,
            "correct": 4432,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          },
          "boosted": {
            "class_order": [
              -1,
              0,
              1
            ],
            "macro_f1": 0.46112813473562375,
            "balanced_accuracy": 0.4624343222721903,
            "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
            "fixed_class_macro_recall": 0.4624343222721903,
            "accuracy": 0.4818162926018288,
            "per_class": [
              {
                "label": -1,
                "name": "down",
                "precision": 0.44405182567726736,
                "recall": 0.3740079365079365,
                "f1": 0.40603123317178247,
                "support": 3024
              },
              {
                "label": 0,
                "name": "unchanged",
                "precision": 0.5608275241736002,
                "recall": 0.6315522917194226,
                "f1": 0.5940924249642687,
                "support": 3949
              },
              {
                "label": 1,
                "name": "up",
                "precision": 0.38479087452471483,
                "recall": 0.3817427385892116,
                "f1": 0.38326074607081995,
                "support": 2651
              }
            ],
            "confusion_matrix": [
              [
                1131,
                891,
                1002
              ],
              [
                839,
                2494,
                616
              ],
              [
                577,
                1062,
                1012
              ]
            ],
            "support": 9624,
            "correct": 4637,
            "absent_true_classes": [],
            "unpredicted_classes": [],
            "warnings": [],
            "fit_warnings": []
          }
        }
      }
    ],
    "by_date": {
      "2022-01-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.22897918371057177,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.5231568016614746,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 4159
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 433
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5231568016614746,
              "recall": 1.0,
              "f1": 0.6869375511317153,
              "support": 5038
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              4159
            ],
            [
              0,
              0,
              433
            ],
            [
              0,
              0,
              5038
            ]
          ],
          "support": 9630,
          "correct": 5038,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.33922514267769976,
          "balanced_accuracy": 0.3542886199213142,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3542886199213142,
          "accuracy": 0.5256490134994808,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.49393723252496435,
              "recall": 0.33301274344794424,
              "f1": 0.3978170328881229,
              "support": 4159
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 433
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5386756519191327,
              "recall": 0.7298531163159984,
              "f1": 0.6198583951449764,
              "support": 5038
            }
          ],
          "confusion_matrix": [
            [
              1385,
              0,
              2774
            ],
            [
              58,
              0,
              375
            ],
            [
              1361,
              0,
              3677
            ]
          ],
          "support": 9630,
          "correct": 5062,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.34048779489237724,
          "balanced_accuracy": 0.35257991956354195,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.35257991956354195,
          "accuracy": 0.49179646936656285,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.45342155667769457,
              "recall": 0.6261120461649435,
              "f1": 0.5259543526560291,
              "support": 4159
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.2857142857142857,
              "recall": 0.009237875288683603,
              "f1": 0.017897091722595078,
              "support": 433
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.549444874774077,
              "recall": 0.4223898372369988,
              "f1": 0.47761194029850745,
              "support": 5038
            }
          ],
          "confusion_matrix": [
            [
              2604,
              0,
              1555
            ],
            [
              239,
              4,
              190
            ],
            [
              2900,
              10,
              2128
            ]
          ],
          "support": 9630,
          "correct": 4736,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3428650692234496,
          "balanced_accuracy": 0.3595292909417798,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3595292909417798,
          "accuracy": 0.5044652128764279,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4606931530008453,
              "recall": 0.6552055782640057,
              "f1": 0.5409966249751836,
              "support": 4159
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 433
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5747776879547292,
              "recall": 0.42338229456133386,
              "f1": 0.48759858269516515,
              "support": 5038
            }
          ],
          "confusion_matrix": [
            [
              2725,
              2,
              1432
            ],
            [
              287,
              0,
              146
            ],
            [
              2903,
              2,
              2133
            ]
          ],
          "support": 9630,
          "correct": 4858,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-02-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.21431012874558505,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.4737637477961548,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 5727
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 541
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4737637477961548,
              "recall": 1.0,
              "f1": 0.6429303862367551,
              "support": 5643
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              5727
            ],
            [
              0,
              0,
              541
            ],
            [
              0,
              0,
              5643
            ]
          ],
          "support": 11911,
          "correct": 5643,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3096928826374232,
          "balanced_accuracy": 0.3365301500634595,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3365301500634595,
          "accuracy": 0.48022836033918226,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5001603077909587,
              "recall": 0.2723939235201676,
              "f1": 0.35270178611801944,
              "support": 5727
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 541
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4731574158325751,
              "recall": 0.7371965266702108,
              "f1": 0.5763768617942501,
              "support": 5643
            }
          ],
          "confusion_matrix": [
            [
              1560,
              0,
              4167
            ],
            [
              76,
              0,
              465
            ],
            [
              1483,
              0,
              4160
            ]
          ],
          "support": 11911,
          "correct": 5720,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3163710848959684,
          "balanced_accuracy": 0.3299849886103367,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3299849886103367,
          "accuracy": 0.4715808916127949,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.47675478577939834,
              "recall": 0.36528723590012224,
              "f1": 0.41364310430054374,
              "support": 5727
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 541
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4685630732420577,
              "recall": 0.6246677299308878,
              "f1": 0.5354701503873613,
              "support": 5643
            }
          ],
          "confusion_matrix": [
            [
              2092,
              0,
              3635
            ],
            [
              178,
              0,
              363
            ],
            [
              2118,
              0,
              3525
            ]
          ],
          "support": 11911,
          "correct": 5617,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3445168417872315,
          "balanced_accuracy": 0.35297454215230584,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.35297454215230584,
          "accuracy": 0.5051632944337168,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5160525355709595,
              "recall": 0.4939759036144578,
              "f1": 0.5047729503077883,
              "support": 5727
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 541
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4969602494154326,
              "recall": 0.5649477228424596,
              "f1": 0.5287775750539061,
              "support": 5643
            }
          ],
          "confusion_matrix": [
            [
              2829,
              4,
              2894
            ],
            [
              208,
              0,
              333
            ],
            [
              2445,
              10,
              3188
            ]
          ],
          "support": 11911,
          "correct": 6017,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-03-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.21020498652750774,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.46050960173354255,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 6700
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 520
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.46050960173354255,
              "recall": 1.0,
              "f1": 0.6306149595825232,
              "support": 6163
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              6700
            ],
            [
              0,
              0,
              520
            ],
            [
              0,
              0,
              6163
            ]
          ],
          "support": 13383,
          "correct": 6163,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.33369043812052296,
          "balanced_accuracy": 0.35236097623193463,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.35236097623193463,
          "accuracy": 0.5011581857580513,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5453718444393905,
              "recall": 0.357910447761194,
              "f1": 0.43218887987744437,
              "support": 6700
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 520
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4795237035388382,
              "recall": 0.6991724809346098,
              "f1": 0.5688824344841243,
              "support": 6163
            }
          ],
          "confusion_matrix": [
            [
              2398,
              0,
              4302
            ],
            [
              145,
              0,
              375
            ],
            [
              1854,
              0,
              4309
            ]
          ],
          "support": 13383,
          "correct": 6707,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3473275162185048,
          "balanced_accuracy": 0.35436281193416336,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.35436281193416336,
          "accuracy": 0.511469775087798,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5286127167630058,
              "recall": 0.5459701492537313,
              "f1": 0.537151248164464,
              "support": 6700
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 520
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4931146526380938,
              "recall": 0.5171182865487587,
              "f1": 0.5048313004910502,
              "support": 6163
            }
          ],
          "confusion_matrix": [
            [
              3658,
              0,
              3042
            ],
            [
              286,
              0,
              234
            ],
            [
              2976,
              0,
              3187
            ]
          ],
          "support": 13383,
          "correct": 6845,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3624112750375867,
          "balanced_accuracy": 0.36973655170520914,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.36973655170520914,
          "accuracy": 0.5341104386161548,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5523701390860063,
              "recall": 0.5808955223880597,
              "f1": 0.56627382511276,
              "support": 6700
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 520
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5138077954868234,
              "recall": 0.5283141327275678,
              "f1": 0.52096,
              "support": 6163
            }
          ],
          "confusion_matrix": [
            [
              3892,
              0,
              2808
            ],
            [
              247,
              0,
              273
            ],
            [
              2907,
              0,
              3256
            ]
          ],
          "support": 13383,
          "correct": 7148,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        }
      },
      "2022-04-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.22496107453054948,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.5093009428353011,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 5406
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5093009428353011,
              "recall": 1.0,
              "f1": 0.6748832235916484,
              "support": 5996
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              5406
            ],
            [
              0,
              0,
              371
            ],
            [
              0,
              0,
              5996
            ]
          ],
          "support": 11773,
          "correct": 5996,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.349092915971925,
          "balanced_accuracy": 0.35996964227641876,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.35996964227641876,
          "accuracy": 0.5307907924912937,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5172241637543684,
              "recall": 0.38327783943766186,
              "f1": 0.44028899277518063,
              "support": 5406
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5377880777649028,
              "recall": 0.6966310873915944,
              "f1": 0.6069897551405944,
              "support": 5996
            }
          ],
          "confusion_matrix": [
            [
              2072,
              0,
              3334
            ],
            [
              115,
              0,
              256
            ],
            [
              1819,
              0,
              4177
            ]
          ],
          "support": 11773,
          "correct": 6249,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3552275465093624,
          "balanced_accuracy": 0.36113416672487125,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.36113416672487125,
          "accuracy": 0.525014864520513,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.496816382722423,
              "recall": 0.5340362560118387,
              "f1": 0.5147543906570384,
              "support": 5406
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5524991613552499,
              "recall": 0.5493662441627751,
              "f1": 0.5509282488710486,
              "support": 5996
            }
          ],
          "confusion_matrix": [
            [
              2887,
              0,
              2519
            ],
            [
              222,
              0,
              149
            ],
            [
              2702,
              0,
              3294
            ]
          ],
          "support": 11773,
          "correct": 6181,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.371574917731141,
          "balanced_accuracy": 0.3779620910590206,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3779620910590206,
          "accuracy": 0.5487980973413743,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.520868394479973,
              "recall": 0.5725120236773955,
              "f1": 0.5454705675008812,
              "support": 5406
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5773584905660377,
              "recall": 0.5613742494996664,
              "f1": 0.5692541856925418,
              "support": 5996
            }
          ],
          "confusion_matrix": [
            [
              3095,
              0,
              2311
            ],
            [
              218,
              0,
              153
            ],
            [
              2629,
              1,
              3366
            ]
          ],
          "support": 11773,
          "correct": 6461,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-05-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.21583445158556394,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.4787467362924282,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 4428
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 563
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4787467362924282,
              "recall": 1.0,
              "f1": 0.6475033547566919,
              "support": 4584
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              4428
            ],
            [
              0,
              0,
              563
            ],
            [
              0,
              0,
              4584
            ]
          ],
          "support": 9575,
          "correct": 4584,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3232512086438242,
          "balanced_accuracy": 0.3480475271593903,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3480475271593903,
          "accuracy": 0.49493472584856396,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5081285444234405,
              "recall": 0.3035230352303523,
              "f1": 0.3800367595079881,
              "support": 4428
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 563
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4898989898989899,
              "recall": 0.7406195462478184,
              "f1": 0.5897168664234844,
              "support": 4584
            }
          ],
          "confusion_matrix": [
            [
              1344,
              0,
              3084
            ],
            [
              112,
              0,
              451
            ],
            [
              1189,
              0,
              3395
            ]
          ],
          "support": 9575,
          "correct": 4739,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.34310257833626195,
          "balanced_accuracy": 0.3539771894228541,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3539771894228541,
          "accuracy": 0.5002610966057441,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4887267904509284,
              "recall": 0.4993224932249323,
              "f1": 0.49396782841823056,
              "support": 4428
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 563
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5105919619877252,
              "recall": 0.56260907504363,
              "f1": 0.5353399065905553,
              "support": 4584
            }
          ],
          "confusion_matrix": [
            [
              2211,
              0,
              2217
            ],
            [
              308,
              0,
              255
            ],
            [
              2005,
              0,
              2579
            ]
          ],
          "support": 9575,
          "correct": 4790,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3672532297703608,
          "balanced_accuracy": 0.368043002775003,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.368043002775003,
          "accuracy": 0.5066318537859008,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.494566375452802,
              "recall": 0.5241644083107497,
              "f1": 0.5089354237473961,
              "support": 4428
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.4864864864864865,
              "recall": 0.03197158081705151,
              "f1": 0.06,
              "support": 563
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5184726522187822,
              "recall": 0.5479930191972077,
              "f1": 0.5328242655636864,
              "support": 4584
            }
          ],
          "confusion_matrix": [
            [
              2321,
              18,
              2089
            ],
            [
              301,
              18,
              244
            ],
            [
              2071,
              1,
              2512
            ]
          ],
          "support": 9575,
          "correct": 4851,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-06-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.21123099944868864,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.4637998616555222,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 4077
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 574
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4637998616555222,
              "recall": 1.0,
              "f1": 0.633692998346066,
              "support": 4023
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              4077
            ],
            [
              0,
              0,
              574
            ],
            [
              0,
              0,
              4023
            ]
          ],
          "support": 8674,
          "correct": 4023,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.33089075093689607,
          "balanced_accuracy": 0.35943819725321124,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.35943819725321124,
          "accuracy": 0.5020751671662439,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5489270386266094,
              "recall": 0.3137110620554329,
              "f1": 0.39925081941626345,
              "support": 4077
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 574
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4848675914249685,
              "recall": 0.7646035297042009,
              "f1": 0.5934214333944247,
              "support": 4023
            }
          ],
          "confusion_matrix": [
            [
              1279,
              0,
              2798
            ],
            [
              104,
              0,
              470
            ],
            [
              947,
              0,
              3076
            ]
          ],
          "support": 8674,
          "correct": 4355,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3328191253373316,
          "balanced_accuracy": 0.3479265745144229,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3479265745144229,
          "accuracy": 0.486741987548997,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4873024830699774,
              "recall": 0.42359578121167524,
              "f1": 0.45322136202598085,
              "support": 4077
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 574
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.48644960031195167,
              "recall": 0.6201839423315934,
              "f1": 0.545236013986014,
              "support": 4023
            }
          ],
          "confusion_matrix": [
            [
              1727,
              0,
              2350
            ],
            [
              290,
              0,
              284
            ],
            [
              1527,
              1,
              2495
            ]
          ],
          "support": 8674,
          "correct": 4222,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3896852057316726,
          "balanced_accuracy": 0.38967154604308485,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.38967154604308485,
          "accuracy": 0.5259395895780493,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5392464678178964,
              "recall": 0.5055187637969095,
              "f1": 0.5218382073680212,
              "support": 4077
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.30434782608695654,
              "recall": 0.04878048780487805,
              "f1": 0.08408408408408409,
              "support": 574
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5195378151260505,
              "recall": 0.614715386527467,
              "f1": 0.5631333257429124,
              "support": 4023
            }
          ],
          "confusion_matrix": [
            [
              2061,
              17,
              1999
            ],
            [
              258,
              28,
              288
            ],
            [
              1503,
              47,
              2473
            ]
          ],
          "support": 8674,
          "correct": 4562,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-07-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.21724219489120153,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.4833786509955267,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 5519
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4833786509955267,
              "recall": 1.0,
              "f1": 0.6517265846736046,
              "support": 5511
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              5519
            ],
            [
              0,
              0,
              371
            ],
            [
              0,
              0,
              5511
            ]
          ],
          "support": 11401,
          "correct": 5511,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3004952841976729,
          "balanced_accuracy": 0.3244377947011094,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3244377947011094,
          "accuracy": 0.47066046837996667,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4668192219679634,
              "recall": 0.25874252581989493,
              "f1": 0.3329447423641875,
              "support": 5519
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.47206904818988255,
              "recall": 0.7145708582834331,
              "f1": 0.5685411102288312,
              "support": 5511
            }
          ],
          "confusion_matrix": [
            [
              1428,
              0,
              4091
            ],
            [
              58,
              0,
              313
            ],
            [
              1573,
              0,
              3938
            ]
          ],
          "support": 11401,
          "correct": 5366,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.32194984759923023,
          "balanced_accuracy": 0.3274604491456889,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3274604491456889,
          "accuracy": 0.4752214718007192,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4733668341708543,
              "recall": 0.5120492842906323,
              "f1": 0.49194882061101924,
              "support": 5519
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.47752394988946206,
              "recall": 0.4703320631464344,
              "f1": 0.47390072218667156,
              "support": 5511
            }
          ],
          "confusion_matrix": [
            [
              2826,
              3,
              2690
            ],
            [
              225,
              0,
              146
            ],
            [
              2919,
              0,
              2592
            ]
          ],
          "support": 11401,
          "correct": 5418,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3675055578211854,
          "balanced_accuracy": 0.3650307136321464,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3650307136321464,
          "accuracy": 0.4871502499780721,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4948799106311674,
              "recall": 0.4816089871353506,
              "f1": 0.4881542699724518,
              "support": 5519
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.12027491408934708,
              "recall": 0.09433962264150944,
              "f1": 0.10574018126888217,
              "support": 371
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.498518905732706,
              "recall": 0.519143531119579,
              "f1": 0.5086222222222222,
              "support": 5511
            }
          ],
          "confusion_matrix": [
            [
              2658,
              128,
              2733
            ],
            [
              191,
              35,
              145
            ],
            [
              2522,
              128,
              2861
            ]
          ],
          "support": 11401,
          "correct": 5554,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-08-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.21953039280228218,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.49096976835492734,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 4942
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 244
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.49096976835492734,
              "recall": 1.0,
              "f1": 0.6585911784068466,
              "support": 5002
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              4942
            ],
            [
              0,
              0,
              244
            ],
            [
              0,
              0,
              5002
            ]
          ],
          "support": 10188,
          "correct": 5002,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.28738065946055974,
          "balanced_accuracy": 0.3209258317447336,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3209258317447336,
          "accuracy": 0.47153513937966235,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.44715073529411764,
              "recall": 0.19688385269121814,
              "f1": 0.27339140207923573,
              "support": 4942
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 244
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.47815776335496757,
              "recall": 0.7658936425429828,
              "f1": 0.5887505763024435,
              "support": 5002
            }
          ],
          "confusion_matrix": [
            [
              973,
              0,
              3969
            ],
            [
              32,
              0,
              212
            ],
            [
              1171,
              0,
              3831
            ]
          ],
          "support": 10188,
          "correct": 4804,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.36084040659989675,
          "balanced_accuracy": 0.35481122538169413,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.35481122538169413,
          "accuracy": 0.48802512760109934,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4790268456375839,
              "recall": 0.34662080129502226,
              "f1": 0.40220709086640055,
              "support": 4942
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.4358974358974359,
              "recall": 0.06967213114754098,
              "f1": 0.12014134275618374,
              "support": 244
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.49322987981134947,
              "recall": 0.648140743702519,
              "f1": 0.5601727861771059,
              "support": 5002
            }
          ],
          "confusion_matrix": [
            [
              1713,
              10,
              3219
            ],
            [
              115,
              17,
              112
            ],
            [
              1748,
              12,
              3242
            ]
          ],
          "support": 10188,
          "correct": 4972,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3396988983567053,
          "balanced_accuracy": 0.34391291372295,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.34391291372295,
          "accuracy": 0.5036317235963879,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5061957868649318,
              "recall": 0.49595305544314044,
              "f1": 0.5010220768601799,
              "support": 4942
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 244
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.5014970059880239,
              "recall": 0.5357856857257097,
              "f1": 0.5180746182099362,
              "support": 5002
            }
          ],
          "confusion_matrix": [
            [
              2451,
              1,
              2490
            ],
            [
              70,
              0,
              174
            ],
            [
              2321,
              1,
              2680
            ]
          ],
          "support": 10188,
          "correct": 5131,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-09-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.2063127945229839,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.4481613102595797,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 5814
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 1329
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4481613102595797,
              "recall": 1.0,
              "f1": 0.6189383835689517,
              "support": 5801
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              5814
            ],
            [
              0,
              0,
              1329
            ],
            [
              0,
              0,
              5801
            ]
          ],
          "support": 12944,
          "correct": 5801,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.28702150357017614,
          "balanced_accuracy": 0.3355917603615903,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3355917603615903,
          "accuracy": 0.45140605686032137,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.46635730858468677,
              "recall": 0.20743034055727555,
              "f1": 0.28714285714285714,
              "support": 5814
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 1329
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4476732960030894,
              "recall": 0.7993449405274953,
              "f1": 0.5739216535676712,
              "support": 5801
            }
          ],
          "confusion_matrix": [
            [
              1206,
              0,
              4608
            ],
            [
              216,
              0,
              1113
            ],
            [
              1164,
              0,
              4637
            ]
          ],
          "support": 12944,
          "correct": 5843,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3051034742130348,
          "balanced_accuracy": 0.34972329834425886,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.34972329834425886,
          "accuracy": 0.47017923362175523,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4994648590795576,
              "recall": 0.24079807361541108,
              "f1": 0.3249390739236393,
              "support": 5814
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.03225806451612903,
              "recall": 0.0007524454477050414,
              "f1": 0.0014705882352941176,
              "support": 1329
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.46340257171117705,
              "recall": 0.8076193759696604,
              "f1": 0.5889007604801709,
              "support": 5801
            }
          ],
          "confusion_matrix": [
            [
              1400,
              28,
              4386
            ],
            [
              289,
              1,
              1039
            ],
            [
              1114,
              2,
              4685
            ]
          ],
          "support": 12944,
          "correct": 6086,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3837641018175509,
          "balanced_accuracy": 0.3847763133388344,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3847763133388344,
          "accuracy": 0.46446229913473425,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.5132340777502068,
              "recall": 0.4269005847953216,
              "f1": 0.4661032863849765,
              "support": 5814
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.1697019867549669,
              "recall": 0.1542513167795335,
              "f1": 0.16160819865983445,
              "support": 1329
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.48188405797101447,
              "recall": 0.573177038441648,
              "f1": 0.5235808204078419,
              "support": 5801
            }
          ],
          "confusion_matrix": [
            [
              2482,
              455,
              2877
            ],
            [
              426,
              205,
              698
            ],
            [
              1928,
              548,
              3325
            ]
          ],
          "support": 12944,
          "correct": 6012,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-10-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.1801446416831032,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.37027027027027026,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 3576
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 2016
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.37027027027027026,
              "recall": 1.0,
              "f1": 0.5404339250493096,
              "support": 3288
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              3576
            ],
            [
              0,
              0,
              2016
            ],
            [
              0,
              0,
              3288
            ]
          ],
          "support": 8880,
          "correct": 3288,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.23293868026811393,
          "balanced_accuracy": 0.33495811492676236,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.33495811492676236,
          "accuracy": 0.37567567567567567,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4600231749710313,
              "recall": 0.11101789709172259,
              "f1": 0.1788691146654652,
              "support": 3576
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 2016
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.3665959835349881,
              "recall": 0.8938564476885644,
              "f1": 0.5199469261388766,
              "support": 3288
            }
          ],
          "confusion_matrix": [
            [
              397,
              0,
              3179
            ],
            [
              117,
              0,
              1899
            ],
            [
              349,
              0,
              2939
            ]
          ],
          "support": 8880,
          "correct": 3336,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3477712621998932,
          "balanced_accuracy": 0.37606147181081045,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.37606147181081045,
          "accuracy": 0.41655405405405405,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4363572433192686,
              "recall": 0.3470357941834452,
              "f1": 0.3866043613707165,
              "support": 3576
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.4943502824858757,
              "recall": 0.08680555555555555,
              "f1": 0.14767932489451477,
              "support": 2016
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.40179514255543824,
              "recall": 0.6943430656934306,
              "f1": 0.5090301003344482,
              "support": 3288
            }
          ],
          "confusion_matrix": [
            [
              1241,
              67,
              2268
            ],
            [
              710,
              175,
              1131
            ],
            [
              893,
              112,
              2283
            ]
          ],
          "support": 8880,
          "correct": 3699,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.3247503226801933,
          "balanced_accuracy": 0.3574399707547089,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3574399707547089,
          "accuracy": 0.4115990990990991,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.41025223759153784,
              "recall": 0.7049776286353467,
              "f1": 0.5186709186297705,
              "support": 3576
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.46987951807228917,
              "recall": 0.05803571428571429,
              "f1": 0.10331125827814569,
              "support": 2016
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4090909090909091,
              "recall": 0.3093065693430657,
              "f1": 0.3522687911326637,
              "support": 3288
            }
          ],
          "confusion_matrix": [
            [
              2521,
              63,
              992
            ],
            [
              1422,
              117,
              477
            ],
            [
              2202,
              69,
              1017
            ]
          ],
          "support": 8880,
          "correct": 3655,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-11-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.1853772420140526,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.3851679104477612,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 3926
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 2665
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.3851679104477612,
              "recall": 1.0,
              "f1": 0.5561317260421578,
              "support": 4129
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              3926
            ],
            [
              0,
              0,
              2665
            ],
            [
              0,
              0,
              4129
            ]
          ],
          "support": 10720,
          "correct": 4129,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.2518823677991422,
          "balanced_accuracy": 0.34397356586476024,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.34397356586476024,
          "accuracy": 0.39477611940298507,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4311145510835913,
              "recall": 0.14187468160978095,
              "f1": 0.21349175929474895,
              "support": 3926
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 2665
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.3897963512940178,
              "recall": 0.8900460159844998,
              "f1": 0.5421553441026776,
              "support": 4129
            }
          ],
          "confusion_matrix": [
            [
              557,
              0,
              3369
            ],
            [
              281,
              0,
              2384
            ],
            [
              454,
              0,
              3675
            ]
          ],
          "support": 10720,
          "correct": 4232,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.35987827897590496,
          "balanced_accuracy": 0.38530506863391434,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.38530506863391434,
          "accuracy": 0.4222014925373134,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.3932236520605962,
              "recall": 0.6148751910341315,
              "f1": 0.4796820665673125,
              "support": 3926
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.5199063231850117,
              "recall": 0.08330206378986867,
              "f1": 0.14359637774902975,
              "support": 2665
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.4549831487722677,
              "recall": 0.4577379510777428,
              "f1": 0.4563563926113727,
              "support": 4129
            }
          ],
          "confusion_matrix": [
            [
              2414,
              69,
              1443
            ],
            [
              1622,
              222,
              821
            ],
            [
              2103,
              136,
              1890
            ]
          ],
          "support": 10720,
          "correct": 4526,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.4191207291146181,
          "balanced_accuracy": 0.42620536537216663,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.42620536537216663,
          "accuracy": 0.43180970149253733,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.39542586750788644,
              "recall": 0.6385634233316353,
              "f1": 0.4884083382037795,
              "support": 3926
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.48715313463514903,
              "recall": 0.3557223264540338,
              "f1": 0.41119063109954457,
              "support": 2665
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.48233360723089563,
              "recall": 0.2843303463308307,
              "f1": 0.35776321804053024,
              "support": 4129
            }
          ],
          "confusion_matrix": [
            [
              2507,
              573,
              846
            ],
            [
              1303,
              948,
              414
            ],
            [
              2530,
              425,
              1174
            ]
          ],
          "support": 10720,
          "correct": 4629,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      },
      "2022-12-01": {
        "majority": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.14397827562797014,
          "balanced_accuracy": 0.3333333333333333,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3333333333333333,
          "accuracy": 0.2754571903574397,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 3024
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 3949
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.2754571903574397,
              "recall": 1.0,
              "f1": 0.4319348268839104,
              "support": 2651
            }
          ],
          "confusion_matrix": [
            [
              0,
              0,
              3024
            ],
            [
              0,
              0,
              3949
            ],
            [
              0,
              0,
              2651
            ]
          ],
          "support": 9624,
          "correct": 2651,
          "absent_true_classes": [],
          "unpredicted_classes": [
            -1,
            0
          ],
          "warnings": [
            "No predictions for classes: -1, 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "history_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.21687580417543625,
          "balanced_accuracy": 0.3479689621632913,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.3479689621632913,
          "accuracy": 0.29353699085619284,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4726720647773279,
              "recall": 0.15443121693121692,
              "f1": 0.23280159521435692,
              "support": 3024
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.0,
              "recall": 0.0,
              "f1": 0.0,
              "support": 3949
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.2730430754979157,
              "recall": 0.8894756695586571,
              "f1": 0.4178258173119518,
              "support": 2651
            }
          ],
          "confusion_matrix": [
            [
              467,
              0,
              2557
            ],
            [
              228,
              0,
              3721
            ],
            [
              293,
              0,
              2358
            ]
          ],
          "support": 9624,
          "correct": 2825,
          "absent_true_classes": [],
          "unpredicted_classes": [
            0
          ],
          "warnings": [
            "No predictions for classes: 0. Undefined precision/F1 components use zero."
          ],
          "fit_warnings": []
        },
        "book_logistic": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.44188130998239505,
          "balanced_accuracy": 0.443933226231286,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.443933226231286,
          "accuracy": 0.4605153782211139,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.4463729417000445,
              "recall": 0.3316798941798942,
              "f1": 0.3805729463099981,
              "support": 3024
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.5563131906889255,
              "recall": 0.5991390225373512,
              "f1": 0.5769324554986589,
              "support": 3949
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.34026888604353395,
              "recall": 0.4009807619766126,
              "f1": 0.36813852813852815,
              "support": 2651
            }
          ],
          "confusion_matrix": [
            [
              1003,
              782,
              1239
            ],
            [
              761,
              2366,
              822
            ],
            [
              483,
              1105,
              1063
            ]
          ],
          "support": 9624,
          "correct": 4432,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        },
        "boosted": {
          "class_order": [
            -1,
            0,
            1
          ],
          "macro_f1": 0.46112813473562375,
          "balanced_accuracy": 0.4624343222721903,
          "balanced_accuracy_policy": "mean_recall_of_present_true_classes",
          "fixed_class_macro_recall": 0.4624343222721903,
          "accuracy": 0.4818162926018288,
          "per_class": [
            {
              "label": -1,
              "name": "down",
              "precision": 0.44405182567726736,
              "recall": 0.3740079365079365,
              "f1": 0.40603123317178247,
              "support": 3024
            },
            {
              "label": 0,
              "name": "unchanged",
              "precision": 0.5608275241736002,
              "recall": 0.6315522917194226,
              "f1": 0.5940924249642687,
              "support": 3949
            },
            {
              "label": 1,
              "name": "up",
              "precision": 0.38479087452471483,
              "recall": 0.3817427385892116,
              "f1": 0.38326074607081995,
              "support": 2651
            }
          ],
          "confusion_matrix": [
            [
              1131,
              891,
              1002
            ],
            [
              839,
              2494,
              616
            ],
            [
              577,
              1062,
              1012
            ]
          ],
          "support": 9624,
          "correct": 4637,
          "absent_true_classes": [],
          "unpredicted_classes": [],
          "warnings": [],
          "fit_warnings": []
        }
      }
    },
    "summary": {
      "majority": {
        "macro_f1_mean": 0.20484219717417165,
        "macro_f1_std": 0.023993081195765487,
        "balanced_accuracy_mean": 0.3333333333333333,
        "date_count": 12,
        "test_count": 128703
      },
      "history_logistic": {
        "macro_f1_mean": 0.2968698032049493,
        "macro_f1_std": 0.04328037233116664,
        "balanced_accuracy_mean": 0.34320759522233124,
        "date_count": 12,
        "test_count": 128703
      },
      "book_logistic": {
        "macro_f1_mean": 0.3477300188133468,
        "macro_f1_std": 0.034379598572895326,
        "balanced_accuracy_mean": 0.3614383658598202,
        "date_count": 12,
        "test_count": 128703
      },
      "boosted": {
        "macro_f1_mean": 0.3728561903172766,
        "macro_f1_std": 0.037684659158876685,
        "balanced_accuracy_mean": 0.37980971864745,
        "date_count": 12,
        "test_count": 128703
      }
    },
    "comparisons": {
      "book_logistic_vs_history_logistic": {
        "method": "paired_non_circular_moving_block_percentile_bootstrap",
        "metric": "macro_f1",
        "analysis_unit": "observed_date",
        "difference_direction": "scores_a_minus_scores_b",
        "units": [
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01",
          "2022-07-01",
          "2022-08-01",
          "2022-09-01",
          "2022-10-01",
          "2022-11-01",
          "2022-12-01"
        ],
        "n_units": 12,
        "block_length_dates": 3,
        "nonoverlapping_block_count": 4,
        "minimum_blocks": 2,
        "mean_difference": 0.05086021560839742,
        "min_difference": 0.0012626522146774732,
        "max_difference": 0.2250055058069588,
        "std_difference": 0.0682822751810613,
        "confidence": 0.95,
        "ci_lower": 0.010155851646128186,
        "ci_upper": 0.09212558032967372,
        "half_width": 0.040984864341772766,
        "n_resamples": 2000,
        "seed": 42,
        "status": "exploratory",
        "warnings": [
          "Exploratory moving-block date bootstrap; assumes suitable local stationarity and exchangeability of blocks.",
          "Adjacent observed dates may have calendar gaps; shared expanding training histories can create dependence beyond the chosen block length.",
          "No order-book rows are treated as IID observations.",
          "Fewer than eight nonoverlapping date blocks; interval stability is limited."
        ],
        "model_a": "book_logistic",
        "model_b": "history_logistic",
        "role": "primary",
        "decision": {
          "practical_delta": 0.01,
          "positive_practical_gain": true,
          "rules_out_practical_gain": false,
          "equivalence_within_margin": false,
          "negative_practical_effect": false,
          "status": "positive_practical_gain",
          "scope": "conditional on the declared date-block uncertainty assumptions"
        }
      },
      "boosted_vs_book_logistic": {
        "method": "paired_non_circular_moving_block_percentile_bootstrap",
        "metric": "macro_f1",
        "analysis_unit": "observed_date",
        "difference_direction": "scores_a_minus_scores_b",
        "units": [
          "2022-01-01",
          "2022-02-01",
          "2022-03-01",
          "2022-04-01",
          "2022-05-01",
          "2022-06-01",
          "2022-07-01",
          "2022-08-01",
          "2022-09-01",
          "2022-10-01",
          "2022-11-01",
          "2022-12-01"
        ],
        "n_units": 12,
        "block_length_dates": 3,
        "nonoverlapping_block_count": 4,
        "minimum_blocks": 2,
        "mean_difference": 0.025126171503929803,
        "min_difference": -0.023020939519699857,
        "max_difference": 0.07866062760451609,
        "std_difference": 0.031120812648041535,
        "confidence": 0.95,
        "ci_lower": 0.016271969857510435,
        "ci_upper": 0.03530177078155257,
        "half_width": 0.009514900462021067,
        "n_resamples": 2000,
        "seed": 42,
        "status": "exploratory",
        "warnings": [
          "Exploratory moving-block date bootstrap; assumes suitable local stationarity and exchangeability of blocks.",
          "Adjacent observed dates may have calendar gaps; shared expanding training histories can create dependence beyond the chosen block length.",
          "No order-book rows are treated as IID observations.",
          "Fewer than eight nonoverlapping date blocks; interval stability is limited."
        ],
        "model_a": "boosted",
        "model_b": "book_logistic",
        "role": "secondary",
        "decision": {
          "practical_delta": 0.01,
          "positive_practical_gain": true,
          "rules_out_practical_gain": false,
          "equivalence_within_margin": false,
          "negative_practical_effect": false,
          "status": "positive_practical_gain",
          "scope": "conditional on the declared date-block uncertainty assumptions"
        }
      }
    }
  },
  "precision_plan": {
    "method": "development_nonoverlapping_block_mean_SD_normal_approximation",
    "stage": "planning_only",
    "pilot_dates": [
      "2022-01-01",
      "2022-02-01",
      "2022-03-01",
      "2022-04-01",
      "2022-05-01",
      "2022-06-01",
      "2022-07-01",
      "2022-08-01",
      "2022-09-01",
      "2022-10-01",
      "2022-11-01",
      "2022-12-01"
    ],
    "pilot_date_count": 12,
    "pilot_block_count": 4,
    "block_length_dates": 3,
    "planned_final_dates": 24,
    "planned_final_blocks": 8,
    "minimum_final_blocks": 8,
    "confidence": 0.95,
    "target_half_width": 0.015,
    "pilot_block_mean_sd": 0.06706681425008036,
    "estimated_required_final_blocks": 77,
    "estimated_required_final_dates": 231,
    "estimated_final_half_width": 0.0464740771780679,
    "estimated_precision_adequate": false,
    "status": "insufficient_precision",
    "positive_pilot_date_fraction": 1.0,
    "mean_pilot_difference": 0.05086021560839742,
    "warnings": [
      "Pilot precision estimates are approximate; they do not guarantee future variance, independence or achieved precision.",
      "Use all fixed final dates once. No optional stopping, margin changes or data extension based on intermediate final results.",
      "Few pilot blocks make the planning variance uncertain.",
      "Planned final coverage does not meet the pilot precision estimate; research decisiveness must remain explicitly downgraded."
    ],
    "positive_pilot_block_fraction": 1.0
  },
  "final": null,
  "signal_policy": {
    "target_long_quantity": "0.001",
    "description": "Predicted up requests long; down/unchanged requests flat. After the configured maximum consecutive long decisions, force one flat target before another long request.",
    "maximum_consecutive_long_decisions": 10,
    "inference_delay_us": 0,
    "limitation": "This cap is a decision rule, not an execution holding-time guarantee. Pending IOC orders and segment-end unresolved inventory remain explicit simulator limitations. Execution decisions include the unlabelled last-horizon states."
  },
  "warnings": [
    "One venue/instrument and fixed two-hour excerpts per selected date; results do not establish continuous-day or cross-market generalization.",
    "Date-block uncertainty remains conditional on dependence/stationarity assumptions; shared expanding fits may induce longer dependence.",
    "Macro-F1 uses all three fixed classes; balanced accuracy averages classes present on each true evaluation date.",
    "Classification evidence is not evidence of executable profit. Economic results require the separate declared simulator and costs.",
    "Local signals and fitted models are excluded from published aggregate artifacts."
  ]
}
```

## Execution

Independent-segment hypothetical trials; unresolved inventory marked at bid, not executed.

```json
{}
```

## Limitations

- This is hypothetical execution under declared assumptions, not observed fills or a profitability claim.
- Eight selected 15-minute windows on each first-of-month date are not continuous four-year market coverage.
- Date blocks and adjacent months are not proven independent or exchangeable; bootstrap conclusions are conditional on the stated dependence model.
- Sessions start with equal cash independently. Segment-end inventory is marked at observed bid, not liquidated through unseen data.
- Fees/slippage/delays are scenario assumptions, not historical account-specific rates or measured trading-system latency.
- Top-five reconstructed snapshots cannot establish queue priority, hidden liquidity, market impact or exchange-realistic fills.
- Predictive comparison, hypothetical execution outcome and software acceptance are reported separately.
- Historical event data, signals, detailed ledgers and fitted model assets stay local under provider terms.
