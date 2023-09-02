import pathlib
import json
import numpy as np
from statsmodels.stats.weightstats import ttest_ind


def cohen_d(group1, group2, size):
    # weighted mean
    mean1, mean2 = np.average(group1, weights=size), np.average(group2, weights=size)
    # weighted variance
    var1, var2 = np.average((group1 - mean1)**2, weights=size), np.average((group2 - mean2)**2, weights=size)
    
    d = (mean1 - mean2) / np.sqrt((var1 + var2) / 2)
    
    return d

if __name__ == "__main__":
    FSRS = []
    SM15 = []
    sizes = []
    result_dir = pathlib.Path("./result")
    result_files = result_dir.glob("*.json")
    for result_file in result_files:
        with open(result_file, "r") as f:
            result = json.load(f)
            FSRS.append(result["FSRS"])
            SM15.append(result["SM15"])
            sizes.append(result["size"])

    print(f"Total users: {len(sizes)}")

    sizes = np.array(sizes)
    print(f"Total size: {sizes.sum()}")
    for metric in ("log_loss", "RMSE", "universal_metric"):
        print(f"metric: {metric}")

        FSRS_metrics = np.array([item[metric] for item in FSRS])
        SM15_metrics = np.array([item[metric] for item in SM15])

        print(f"FSRS mean: {np.average(FSRS_metrics, weights=sizes):.4f}, SM17 mean: {np.average(SM15_metrics, weights=sizes):.4f}")

        t_stat, p_value, df = ttest_ind(FSRS_metrics, SM15_metrics, weights=(sizes, sizes))

        print(f"t-statistic: {t_stat}, p-value: {p_value}, df: {df}")

        if p_value < 0.05:
            print("The performance difference between FSRS and SM15 is statistically significant.")
        else:
            print("The performance difference between FSRS and SM15 is not statistically significant.")

        print(f"Cohen's d: {cohen_d(FSRS_metrics, SM15_metrics, sizes)}")

'''
metric: RMSE, t-statistic: -78.04956741295949, p-value: 0.0, df: 514624.0
The performance difference between FSRS and SM15 is statistically significant.
Cohen's d: -0.21759828991391236
metric: log_loss, t-statistic: -122.84357886657645, p-value: 0.0, df: 514624.0
The performance difference between FSRS and SM15 is statistically significant.
Cohen's d: -0.34248175325355346
metric: universal_metric, t-statistic: -329.0947639176226, p-value: 0.0, df: 514624.0
The performance difference between FSRS and SM15 is statistically significant.
Cohen's d: -0.9174997405072971
'''