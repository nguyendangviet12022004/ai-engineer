from mlkit.models import create_model_from_name

model = create_model_from_name("linear")
print(model)   # <mlkit.models.linear.LinearModel object at 0x...>

try:
    create_model_from_name("random_forest")
except ValueError as e:
    print("Error:", e)   # Unknown model 'random_forest'. Valid options: ['linear', 'dummy']
