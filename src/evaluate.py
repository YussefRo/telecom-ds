from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, RocCurveDisplay
import matplotlib.pyplot as plt


def evaluateModel(model_xgb,features_test,target_test):

    #predicciones 
    target_predict = model_xgb.predict(features_test)
    target_proba = model_xgb.predict_proba(features_test)[:,1]

    print("Matriz de confusion")
    print(confusion_matrix(target_test,target_predict))

    print("\nReporte de clasificacion")
    print(classification_report(target_test,target_predict))

    auc = roc_auc_score(target_test,target_proba)
    print(f"\nAUC-ROC: {auc:.4f}")


    RocCurveDisplay.from_estimator(model_xgb,features_test,target_test)
    plt.title("Curva ROC - XGBoost Optimizado")
    plt.show()

