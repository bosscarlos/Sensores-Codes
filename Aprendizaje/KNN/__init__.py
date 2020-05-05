import logging
import azure.functions as func
import pyodbc
import pandas as pd
import json
import uuid
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics

# Definicion de la funcion de traseo de error.
def traceDB(cnxnAzure,uuid,message):
    query = "INSERT INTO [dbo].[logs] ([ID],[Fecha],[Descripcion]) VALUES ('{}',GETDATE(),'{}')".format(uuid,message)
    cnxnAzure.execute(query)
    cnxnAzure.commit()
    return(True)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Seteo de variables globales.')
    ID = str(uuid.uuid1())
    logging.info(ID)
    driverAzure = os.environ["DriverAzure"]
    serverAzure = os.environ["ServerBdAzure"]
    databaseAzure = os.environ["DataBaseAzure"]
    usernameAzure = os.environ["UserNameBdAzure"]
    passwordAzure = os.environ["PassWordBdAzure"]
    SQL_datos = os.environ["SQL_datos"]
    logging.info(SQL_datos)

    logging.info('Establece conexión con la base de datos Conectados.')
    logging.warning('Establece conexión con la base de datos Conectados.')
    logging.error('Establece conexión con la base de datos Conectados.')
    conStringAzure = "DRIVER={{{}}};SERVER={};DATABASE={};UID={};PWD={}".format(driverAzure,serverAzure,databaseAzure,usernameAzure,passwordAzure)
    logging.info(conStringAzure)
    cnxnAzure = pyodbc.connect(conStringAzure)
    logging.info('Conexión establecida con la base de datos Azure.')
    traceDB(cnxnAzure,ID,'Inicio servicio web.')

    logging.info('Obtiene parámetros del JSON.')
    traceDB(cnxnAzure,ID,'Parámetros del servicio recibidos.')
    req_body = req.get_json()
    variable1 = req_body.get('variable1')
    logging.info(variable1)

    query = (SQL_datos)
    Data = pd.read_sql_query(query,cnxnAzure)
    X = Data.iloc[:, 0:-2].values
    y = Data.iloc[:, -2].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    n_neighbors = 5
    knn = KNeighborsClassifier(n_neighbors)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    json_response = json.dumps(metrics.accuracy_score(y_test, y_pred),indent=2)
    traceDB(cnxnAzure,ID,'Se envia respuesta del servicio :D .')
    if variable1 < 10:
        return func.HttpResponse(json_response)
    else:
        return func.HttpResponse("Funciona pero el Pstman mando un numero >10",status_code=200)