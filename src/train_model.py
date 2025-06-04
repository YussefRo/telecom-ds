from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBClassifier

def trainModel(features_train_resampled,target_train_resampled):

    # como el modelo XGBoost es el mejor pasamos  a afinarlo
    # usaremos RandomizedSearchCV para optimizar


    # nuestro clasificador base
    xgb_clf = XGBClassifier(use_label_encoder = False, eval_metric='logloss', random_state=12345)

    #busqueda de hiperparametros
    param_dist = {
        'n_estimators': [100,200,300],
        'max_depth': [3,5,7,10],
        'learning_rate': [0.01,0.05,0.1,0.2],
        'colsample_bytree': [0.6,0.8,1.0],
        'gamma': [0,0.1,0.3,0.5]
    }

    random_search = RandomizedSearchCV(
        estimator=xgb_clf,
        param_distributions=param_dist,
        n_iter=30,
        scoring='roc_auc',
        cv=5,
        verbose=2,
        random_state=12345,
        n_jobs=-1
    )

    random_search.fit(features_train_resampled,target_train_resampled)

    print('mejores parametros')
    print(random_search.best_params_)

    # entrenamos el modelo con los parametros recomendados

    model_xgb = XGBClassifier(
        n_estimators=200,
        max_depth=10,
        learning_rate=0.2,
        gamma=0,
        colsample_bytree=0.6,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=12345
    )

    model_xgb.fit(features_train_resampled,target_train_resampled)

    return model_xgb