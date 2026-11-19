# Mission 1 – Baseline Model Results

## Model Evaluation

Dataset: Team 11  
Rows removed: 5  
Remaining records: 1995  
Training-validation split: 80:20

| Model | Validation MAE |
|---|---:|
| Mean baseline | 60.26 days |
| Linear regression | 39.27 days |
| Neural network (32, 32) | 17.22 days |

## Observations

- Mean baseline provides the simplest reference.
- Linear regression improves considerably over the mean baseline.
- Neural network achieves the lowest validation MAE.
- The neural network captures relationships that the linear model may not capture effectively.

## Conclusion

The neural network achieved a validation MAE of 17.22 days and outperformed both baseline models.