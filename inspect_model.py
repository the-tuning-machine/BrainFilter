import json

with open('extension/model.json', 'r') as f:
    model = json.load(f)

print("Classes:", model['svm']['classes'])
print("N classes:", len(model['svm']['classes']))
print("N support vectors:", len(model['svm']['support_vectors']))
print("Intercept shape:", len(model['svm']['intercept']))
print("dual_coef type:", type(model['svm']['dual_coef']))
print("dual_coef shape:", len(model['svm']['dual_coef']), "x", len(model['svm']['dual_coef'][0]) if model['svm']['dual_coef'] else 0)
print("\nFirst few dual_coef values:")
for i in range(min(3, len(model['svm']['dual_coef']))):
    print(f"  dual_coef[{i}]: length={len(model['svm']['dual_coef'][i])}, first_values={model['svm']['dual_coef'][i][:3]}")
