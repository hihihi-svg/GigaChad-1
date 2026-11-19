# Mission 2 – Architecture Evaluation

## 1. Validation Method
An 80:20 holdout split was used. The training set was used for model fitting, while the validation set was used to evaluate generalization. A fixed random seed ensured reproducibility.

## 2. Architecture Comparison
Ten neural network architectures were evaluated using different hidden-layer widths and depths.

The best-performing architecture was **5 → 32 → 32 → 1**, with:
- Trainable parameters: 1,281
- Validation MAE: 6.48 days
- Training MAE: 5.11 days
- Float32 parameter storage: 5,124 bytes
- MACs per inference: 1,216

## 3. Observations
- Two-hidden-layer architectures generally performed better than single-hidden-layer architectures.
- The 32,32 architecture achieved the lowest validation MAE.
- Increasing the width to 64,64 increased model parameters without improving validation accuracy.
- The training-validation MAE difference was 1.37 days, indicating reasonable generalization.

## 4. Conclusion
The 5 → 32 → 32 → 1 architecture was selected as the current candidate because it achieved the best validation accuracy among the evaluated architectures while maintaining a relatively small parameter count.