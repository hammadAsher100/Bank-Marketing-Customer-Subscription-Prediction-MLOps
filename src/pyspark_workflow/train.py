import os
import yaml
import mlflow
import mlflow.spark
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.functions import vector_to_array

# Load parameters
with open("params.yaml", "r") as f:
    PARAMS = yaml.safe_load(f)

def balance_training_data(df):
    print("[PySpark Train] Balancing training data using random oversampling...")
    pos_df = df.filter(df["y"] == 1)
    neg_df = df.filter(df["y"] == 0)
    
    pos_count = pos_df.count()
    neg_count = neg_df.count()
    
    print(f"[PySpark Train]   Original Train Class counts - Pos: {pos_count}, Neg: {neg_count}")
    
    if pos_count < neg_count:
        ratio = neg_count / pos_count
        pos_df_oversampled = pos_df.sample(withReplacement=True, fraction=ratio, seed=PARAMS["base"]["random_state"])
        df = neg_df.unionAll(pos_df_oversampled)
        print(f"[PySpark Train]   New Train count after balancing: {df.count()}")
    
    return df

def calculate_threshold_metrics(predictions, test_count):
    print("[PySpark Train] Generating threshold metrics...")
    thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80]
    
    # Use vector_to_array to avoid UDF serialization issues
    preds_with_prob = predictions.withColumn("prob_array", vector_to_array("probability"))
    preds_with_prob = preds_with_prob.withColumn("prob_1", F.col("prob_array")[1]).cache()
    
    rows = []
    for t in thresholds:
        # Assign prediction based on threshold
        t_preds = preds_with_prob.withColumn("prediction_t", F.when(F.col("prob_1") >= t, 1.0).otherwise(0.0))
        
        # Calculate confusion matrix components
        # We can use groupby to do this more efficiently in one go if we had many thresholds, 
        # but for 12, simple counts on a cached DF are fine.
        counts = t_preds.groupBy("y", "prediction_t").count().collect()
        
        tp = 0; fp = 0; tn = 0; fn = 0
        for row in counts:
            if row['y'] == 1 and row['prediction_t'] == 1.0: tp = row['count']
            if row['y'] == 0 and row['prediction_t'] == 1.0: fp = row['count']
            if row['y'] == 0 and row['prediction_t'] == 0.0: tn = row['count']
            if row['y'] == 1 and row['prediction_t'] == 0.0: fn = row['count']
        
        accuracy = (tp + tn) / test_count if test_count > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        customers_targeted = tp + fp
        targeting_rate = customers_targeted / test_count if test_count > 0 else 0
        
        rows.append({
            "threshold": t,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "customers_targeted": customers_targeted,
            "targeting_rate": targeting_rate
        })
    
    metrics_df = pd.DataFrame(rows)
    metrics_path = "data_and_model/models/pyspark_threshold_metrics.csv"
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    metrics_df.to_csv(metrics_path, index=False)
    print(f"[PySpark Train] Threshold metrics saved to {metrics_path}")
    return metrics_path

def train_pyspark_model():
    spark = SparkSession.builder \
        .appName(PARAMS["pyspark"]["app_name"] + "_Training") \
        .getOrCreate()

    processed_path = PARAMS["pyspark"]["processed_path"]
    print(f"[PySpark Train] Loading processed data from {processed_path}")
    df = spark.read.parquet(processed_path)

    test_size = PARAMS["data"]["test_size"]
    train_df, test_df = df.randomSplit([1.0 - test_size, test_size], seed=PARAMS["base"]["random_state"])
    train_count = train_df.count()
    test_count = test_df.count()
    print(f"[PySpark Train] Split data - Train: {train_count}, Test: {test_count}")

    train_df_balanced = balance_training_data(train_df)
    balanced_train_count = train_df_balanced.count()

    cat_cols = [item[0] for item in df.dtypes if item[1].startswith('string')]
    num_cols = [item[0] for item in df.dtypes if (item[1].startswith('int') or item[1].startswith('double')) and item[0] != 'y']

    indexers = [StringIndexer(inputCol=c, outputCol=f"{c}_index", handleInvalid="keep") for c in cat_cols]
    encoder = OneHotEncoder(inputCols=[f"{c}_index" for c in cat_cols], outputCols=[f"{c}_vec" for c in cat_cols])
    assembler = VectorAssembler(inputCols=[f"{c}_vec" for c in cat_cols] + num_cols, outputCol="features")
    gbt = GBTClassifier(labelCol="y", featuresCol="features", maxIter=20, seed=PARAMS["base"]["random_state"])
    
    pipeline = Pipeline(stages=indexers + [encoder, assembler, gbt])

    mlflow.set_experiment(PARAMS["base"]["project"])
    with mlflow.start_run(run_name="pyspark_gbt_retraining"):
        print("[PySpark Train] Training GBT model...")
        model = pipeline.fit(train_df_balanced)
        
        print("[PySpark Train] Evaluating on untouched test data...")
        predictions = model.transform(test_df).cache()
        
        # 1. Binary Classification Metrics
        evaluator_auc = BinaryClassificationEvaluator(labelCol="y", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
        auc = evaluator_auc.evaluate(predictions)
        
        evaluator_pr = BinaryClassificationEvaluator(labelCol="y", rawPredictionCol="rawPrediction", metricName="areaUnderPR")
        pr_auc = evaluator_pr.evaluate(predictions)
        
        # 2. Multiclass Metrics
        evaluator_acc = MulticlassClassificationEvaluator(labelCol="y", predictionCol="prediction", metricName="accuracy")
        accuracy = evaluator_acc.evaluate(predictions)
        
        evaluator_f1_weighted = MulticlassClassificationEvaluator(labelCol="y", predictionCol="prediction", metricName="f1")
        f1_weighted = evaluator_f1_weighted.evaluate(predictions)
        
        # Manual Confusion Matrix for 0.5 threshold
        counts_05 = predictions.groupBy("y", "prediction").count().collect()
        tp = 0; fp = 0; tn = 0; fn = 0
        for row in counts_05:
            if row['y'] == 1 and row['prediction'] == 1.0: tp = row['count']
            if row['y'] == 0 and row['prediction'] == 1.0: fp = row['count']
            if row['y'] == 0 and row['prediction'] == 0.0: tn = row['count']
            if row['y'] == 1 and row['prediction'] == 0.0: fn = row['count']
        
        precision_pos = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall_pos = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_pos = 2 * precision_pos * recall_pos / (precision_pos + recall_pos) if (precision_pos + recall_pos) > 0 else 0
        
        print(f"[PySpark Train]   AUC-ROC: {auc:.4f}")
        print(f"[PySpark Train]   AUC-PR:  {pr_auc:.4f}")
        print(f"[PySpark Train]   Accuracy: {accuracy:.4f}")
        print(f"[PySpark Train]   F1 (Pos): {f1_pos:.4f}")
        
        # Log to MLflow
        mlflow.log_metrics({
            "area_under_roc": auc,
            "area_under_pr": pr_auc,
            "accuracy": accuracy,
            "precision_positive_class": precision_pos,
            "recall_positive_class": recall_pos,
            "f1_positive_class": f1_pos,
            "weighted_f1": f1_weighted,
            "true_positives": float(tp),
            "false_positives": float(fp),
            "true_negatives": float(tn),
            "false_negatives": float(fn),
            "train_row_count": float(train_count),
            "test_row_count": float(test_count),
            "balanced_train_row_count": float(balanced_train_count)
        })
        
        # 3. Threshold Analysis
        threshold_csv_path = calculate_threshold_metrics(predictions, test_count)
        mlflow.log_artifact(threshold_csv_path)
        
        # Save and log model
        model_path = PARAMS["pyspark"]["model_path"]
        model.write().overwrite().save(model_path)
        mlflow.spark.log_model(model, "pyspark_model")
        print(f"[PySpark Train] Model and metrics logged successfully.")

    spark.stop()

if __name__ == "__main__":
    train_pyspark_model()
