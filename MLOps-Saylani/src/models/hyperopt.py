# def optimize_lgbm(X_train, y_train, X_test, y_test):
#     """
#     Optuna searches for best LightGBM hyperparameters.
#     Each trial trains a model and returns validation AUC.
#     Optuna uses TPE (Tree-structured Parzen Estimator) to
#     intelligently explore the hyperparameter space.
#     """
#     def objective(trial):
#         params = {
#             "objective":        "binary",
#             "metric":           "auc",
#             "verbosity":        -1,
#             "boosting_type":    "gbdt",
#             "random_state":     RANDOM_STATE,
#             # ── Hyperparameters Optuna tunes ──────────────────────────────
#             "n_estimators":     trial.suggest_int("n_estimators", 200, 1000),
#             "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
#             "num_leaves":       trial.suggest_int("num_leaves", 20, 300),
#             "max_depth":        trial.suggest_int("max_depth", 3, 12),
#             "min_child_samples":trial.suggest_int("min_child_samples", 5, 100),
#             "subsample":        trial.suggest_float("subsample", 0.5, 1.0),
#             "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
#             "reg_alpha":        trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
#             "reg_lambda":       trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
#         }
#         model = lgb.LGBMClassifier(**params)
#         model.fit(
#             X_train, y_train,
#             eval_set=[(X_test, y_test)],
#             callbacks=[lgb.early_stopping(50, verbose=False),
#                        lgb.log_evaluation(-1)]
#         )
#         probs = model.predict_proba(X_test)[:, 1]
#         return roc_auc_score(y_test, probs)

#     # TPE sampler = smarter than random search
#     sampler = TPESampler(seed=RANDOM_STATE)
#     study   = optuna.create_study(direction="maximize", sampler=sampler)
#     study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)

#     print(f"\n[lgbm] Best AUC: {study.best_value:.4f}")
#     print(f"[lgbm] Best params: {study.best_params}")
#     return study.best_params
