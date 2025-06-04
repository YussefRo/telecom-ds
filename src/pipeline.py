import pandas as pd
from EDA import lecturaDatos
from preprocessing import preprosessingModel
from train_model import trainModel
from evaluate import evaluateModel


# ignorar los mensajes warning
import warnings
warnings.filterwarnings("ignore")

# mostrar todas las columnas y filas
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)




# Realizamos el EDA y la impresionde graficos
dataframe = lecturaDatos()

# Realizamos el preprocesamiento de los datos
features_train, features_test, target_train, target_test = preprosessingModel(dataframe)

# Entrenamiento del modelo
model = trainModel(features_train,target_train)

# Evaluacion del modelo
evaluateModel(model,features_test,target_test)
