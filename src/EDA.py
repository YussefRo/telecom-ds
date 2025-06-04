import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os 




def lecturaDatos():

    ruta = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta = os.path.join(ruta, "data")

    #lecturas de archivos
    contratos = pd.read_csv(os.path.join(carpeta,"contract.csv"))
    internet = pd.read_csv(os.path.join(carpeta,"internet.csv"))
    personal = pd.read_csv(os.path.join(carpeta,"personal.csv"))
    phone = pd.read_csv(os.path.join(carpeta,"phone.csv"))


    # Convertir fechas a datetime
    contratos['BeginDate'] = pd.to_datetime(contratos['BeginDate'])
    contratos['EndDate'] = contratos['EndDate'].replace('No', pd.NaT)
    contratos['EndDate'] = pd.to_datetime(contratos['EndDate'])

    # Convertir TotalCharges a numérico
    contratos['TotalCharges'] = pd.to_numeric(contratos['TotalCharges'], errors='coerce')

    #excluimos clientes que su contrato inicio despues del 1 dde febrero del 2020
    contratos = contratos[contratos["BeginDate"] < "01/02/2020"]

    # Unificamos los dataframes
    df = contratos.merge(internet, on='customerID', how='left') \
                .merge(personal, on='customerID', how='left') \
                .merge(phone, on='customerID', how='left')

    #Esto asignará 1 a los clientes que sí tienen fecha de finalización (cancelaron) y 0 a los que tienen 'No' (aún activos).
    df['Churn'] = df['EndDate'].notna().astype(int)


    # Llenamos los datos nulos de las columnas de servicios, los servicios externos son servicios si tienes internet, por lo tanto se agrego no a todos los que estaban nulos

    columnas_objetivo = ["InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]

    df_filtrado = df[(df["InternetService"] != 'Fiber optic') & (df["InternetService"] != 'DSL') ]

    df_filtrado.loc[:,columnas_objetivo] =  df_filtrado[columnas_objetivo].fillna("No")

    df.update(df_filtrado)


    #se le agrega otra descripcion a la columna multiples lineas, ya que le hace falta un nuevo valor que indique que no tienen el servcio de telefono "not using"

    df['MultipleLines'] =  df['MultipleLines'].fillna("Not using")

    # eliminamos clientes inactivos (sin telefonia e internet)
    inactivos = df[
        (df['InternetService'] == 'No') & (df['MultipleLines'] == 'Not using') ]

    df = df.drop(inactivos.index).reset_index(drop=True)

    #La fecha de referencia es el 1 de febrero de 2020. Vamos a crear una columna con la duración del contrato en meses.
    fecha_corte = pd.to_datetime('2020-02-01')
    df['SeniorityMonths'] = ((fecha_corte.year - df['BeginDate'].dt.year) * 12 +
                            (fecha_corte.month - df['BeginDate'].dt.month) +
                            (fecha_corte.day >= df['BeginDate'].dt.day).astype(int) - 1
                            )

    # Vamos a contar cuántos servicios adicionales usa el cliente, Contar cuántos servicios son 'Yes'
    servicios = [
        'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
        'TechSupport', 'StreamingTV', 'StreamingMovies',
        'MultipleLines'
    ]

    df['ContratedServices'] = df[servicios].apply(lambda row: sum(row == 'Yes'), axis=1)

    graficas(df, servicios)

    return df

def graficas(df, servicios):

    #distribucion general de la variable objetivo

    sns.countplot(x='Churn', data=df)
    plt.title('Distribución de cancelaciones')
    plt.xticks([0,1], ['No Canceló', 'Canceló'])
    plt.grid(True)
    plt.show()

    # cancelacion segun tipo de contrato
    sns.countplot(x='Type', hue='Churn', data=df)
    plt.title('Cancelación según tipo de contrato')
    plt.grid(True)
    plt.show()

    # cancelacion segun metodo de pago

    sns.countplot(y='PaymentMethod', hue='Churn', data=df)
    plt.title('Cancelación según método de pago')
    plt.grid(True)
    plt.show()


    sns.countplot(x='ContratedServices', data=df)
    plt.title('Distribución de servicios contratados')
    plt.xlabel('Número de servicios adicionales')
    plt.ylabel('Número de clientes')
    plt.show()

    sns.boxplot(x='Churn', y='MonthlyCharges', data=df)
    plt.title('Cargos mensuales vs. cancelación')
    plt.grid(True)
    plt.show()

    sns.boxplot(x='Churn', y='SeniorityMonths', data=df)
    plt.title('Antigüedad vs. cancelación')
    plt.grid(True)
    plt.show()

    for col in servicios:
        sns.countplot(x=col, hue='Churn', data=df)
        plt.title(f'Churn vs {col}')
        plt.xticks(rotation=45)
        plt.show()
