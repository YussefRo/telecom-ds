import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, RandomizedSearchCV
from imblearn.over_sampling import SMOTE
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


def preprosessingModel(df):

    #Creamos una columna donde simplifiquemos los valores de PaymentMethod
    df["payment"] =  np.where((df['PaymentMethod'] == 'Mailed check') | (df['PaymentMethod'] == 'Electronic check'),'Manual','Automatic')

    # creamos el dataframe con la informacion que nos servira para el entrenamiento del modelo
    df_model = df[["Type","PaperlessBilling","MonthlyCharges","TotalCharges","InternetService","MultipleLines","Churn","SeniorityMonths","ContratedServices","payment"]]

    # Creacion de columnas binarias con label encoding

    df_model["PaperlessBilling"] = df_model["PaperlessBilling"].map({'Yes':1,'No':0})
    df_model["payment"] = df_model["payment"].map({"Automatic":1,"Manual":0})

    # Multiclase con One-Hot-Encoding (sin duplicar informacion con drop_first=true)
    df_model = pd.get_dummies(df_model,columns=["Type","InternetService","MultipleLines"], drop_first=True)


    # Escalar variables numericas

    scaler = StandardScaler()

    num_cols = ['MonthlyCharges','TotalCharges','SeniorityMonths','ContratedServices']

    df_model[num_cols] = scaler.fit_transform(df_model[num_cols])

    df_model.sample(20)

    df.groupby("Churn").count()

    # separacion de el objetivo y las caracteristicas

    features = df_model.drop(columns=["Churn"])
    target = df_model["Churn"]

    features.head()

    # realizamos la separacion de entrenamiento y prueba
    features_train, features_test, target_train, target_test = train_test_split(features, target, test_size=0.2, random_state=12345)
    print(target_train.value_counts())
    print(target_test.value_counts())

    # implementamos tecnica SMOTE para el desbalanceo de clases, se aplica a los datos de entrenamiento

    smote = SMOTE(random_state=12345)
    features_train_resampled, target_train_resampled = smote.fit_resample(features_train,target_train)

    target_train_resampled.value_counts()

    # pasamos a crear nuestra baseline con DummyClassifier

    dummy = DummyClassifier(strategy='most_frequent', random_state=12345)

    auc_scores = cross_val_score(dummy, features_train_resampled,target_train_resampled, cv=5,scoring='roc_auc')

    acc_scores = cross_val_score(dummy, features_train_resampled,target_train_resampled, cv=5,scoring='accuracy')

    print(f" - AUC-ROC {np.mean(auc_scores):.4f}")
    print(f" - Accuracy {np.mean(acc_scores):.4f}")

    # evaluacion de modelos con metrica principal AUC-ROC  y Accuaracy

    # utilizamos la validacion cruzada estratificada de 5 folds
    sfk = StratifiedKFold(n_splits=5, shuffle=True, random_state=12345)

    # parametrizacion de los modelos
    modelos = { "Logistic Regression": LogisticRegression(max_iter=1000, random_state=12345),
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=12345),
            "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss',random_state=12345)}


    # iteramos el diccionario de los modelos para evaluar
    for nombre, modelo in modelos.items():
        auc_scores = cross_val_score(modelo,features_train_resampled,target_train_resampled,cv=sfk,scoring='roc_auc')
        acc_scores = cross_val_score(modelo,features_train_resampled,target_train_resampled,cv=sfk,scoring='accuracy')

        print(f"{nombre}: AUC-ROC promedio = {auc_scores.mean():.4f} (+/- {auc_scores.std():.4f})")
        print(f"          Accuracy promedio = {acc_scores.mean():.4f}\n")


    return features_train_resampled, features_test, target_train_resampled, target_test

