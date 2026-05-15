# # import sys
# # import os

# # sys.path.insert(0, os.getcwd())

# # # =====================================================
# # # DATA PIPELINE
# # # =====================================================
# # from src.data_pipeline.download import download
# # from src.data_pipeline.validate import validate
# # from src.data_pipeline.clean import clean
# # from src.data_pipeline.feature_engineering import engineer
# # from src.data_pipeline.balance import balance

# # # =====================================================
# # # MODEL PIPELINE
# # # =====================================================
# # from src.models.train import (
# #     load_data,
# #     train_lgbm,
# #     train_xgb
# # )

# # from src.models.calibrate import (
# #     load_data_and_model,
# #     calibrate_model
# # )

# # from src.models.predict import (
# #     predict,
# #     live_prediction
# # )


# def main():

#     # =================================================
#     # DATA PIPELINE
#     # =================================================
#     print("\n========== DOWNLOAD ==========")
#     download()

#     print("\n========== VALIDATE ==========")
#     validate()

#     print("\n========== CLEAN ==========")
#     clean()

#     print("\n========== FEATURE ENGINEERING ==========")
#     engineer()

#     print("\n========== BALANCE ==========")
#     balance()

#     # =================================================
#     # TRAINING
#     # =================================================
#     print("\n========== TRAINING ==========")

#     X_train, y_train, X_test, y_test = load_data()

#     print("\nTraining LightGBM...")
#     lgbm_model, lgbm_metrics = train_lgbm(
#         X_train,
#         y_train,
#         X_test,
#         y_test
#     )

#     print("\nTraining XGBoost...")
#     xgb_model, xgb_metrics = train_xgb(
#         X_train,
#         y_train,
#         X_test,
#         y_test
#     )

#     # =================================================
#     # CALIBRATION
#     # =================================================
#     print("\n========== CALIBRATION ==========")

#     for model_name in ["lgbm", "xgb"]:

#         model, X_train, y_train, X_test, y_test = \
#             load_data_and_model(model_name)

#         calibrate_model(
#             model,
#             X_train,
#             y_train,
#             X_test,
#             y_test,
#             method="isotonic",
#             name=model_name
#         )

#     # =================================================
#     # PREDICTION
#     # =================================================
#     print("\n========== TEST PREDICTION ==========")

#     predict(
#         model_name="lgbm",
#         use_calibrated=True,
#         threshold=0.5
#     )

#     # =================================================
#     # LIVE PREDICTION
#     # =================================================
#     print("\n========== LIVE PREDICTION ==========")

#     live_prediction(
#         model_name="lgbm",
#         use_calibrated=True
#     )


# if __name__ == "__main__":
#     main()

from src.data_pipeline.download import download
from src.data_pipeline.validate import validate
from src.data_pipeline.clean import clean
from src.data_pipeline.feature_engineering import engineer
from src.data_pipeline.balance import balance

from src.models.train import (
    load_data,
    train_lgbm,
    train_xgb
)

from src.models.calibrate import (
    load_data_and_model,
    calibrate_model
)

from src.models.predict import predict


def main():

    print("\n========== DOWNLOAD ==========")
    download()

    print("\n========== VALIDATE ==========")
    validate()

    print("\n========== CLEAN ==========")
    clean()

    print("\n========== FEATURE ENGINEERING ==========")
    engineer()

    print("\n========== BALANCE ==========")
    balance()

    print("\n========== TRAIN ==========")

    X_train, y_train, X_test, y_test = load_data()

    train_lgbm(X_train, y_train, X_test, y_test)

    train_xgb(X_train, y_train, X_test, y_test)

    print("\n========== CALIBRATE ==========")

    for model_name in ["lgbm", "xgb"]:

        model, X_train, y_train, X_test, y_test = \
            load_data_and_model(model_name)

        calibrate_model(
            model,
            X_train,
            y_train,
            X_test,
            y_test,
            method="isotonic",
            name=model_name
        )

    print("\n========== PREDICT ==========")

    predict(
        model_name="lgbm",
        use_calibrated=True
    )


if __name__ == "__main__":
    main()