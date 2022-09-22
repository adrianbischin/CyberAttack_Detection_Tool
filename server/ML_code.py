from flask import jsonify
import pandas as pd
from sklearn.ensemble import IsolationForest # algorithm implementation
from sklearn.preprocessing import LabelEncoder # encoder used for categorical features
import geoip2.database # offline database for ip to country translation
import pickle



def analize(filename):

    # Read data
    data = pd.read_csv('temporary_saved_files/{}'.format(filename), header=None, sep=' ') # , usecols=all low_memory=False
    # Setting column names
    data.columns = ['ip', 'user_identity', 'username', 'timestamp', 'timezone', 'request_line', 'status_code', 'response_size', 'referer', 'user_agent_string', 'unknown']
    # exclude unnecessary columns
    data = data.drop(['user_identity', 'username', 'unknown'], axis=1)

    # preprocessing
    data['timestamp'] = data['timestamp'].str.replace('[', '', regex=False)
    data['timestamp'] = data['timestamp'].str.replace(':', ' ', 1)
    data['timezone'] = data['timezone'].str.replace(']', '', regex=False)
    data[['request_method', 'requested_resource', 'request_type']] = data['request_line'].str.split(' ', n=2, expand=True) # split request_line column into another three columns
    data = data.drop(['request_line', 'requested_resource'], axis=1) # dropping unneeded columns
    data[['browser', 'extra']] = data['user_agent_string'].str.split(' ', n=1, expand=True) # split user_agent_string column and keep only the browser
    data = data.drop(['user_agent_string', 'extra'], axis=1) # dropping unneeded columns
    data = data[['ip', 'timestamp', 'timezone', 'request_method', 'request_type', 'status_code', 'response_size', 'referer', 'browser']] # changing columns order


    # replacing ip with country using an offline database
    reader = geoip2.database.Reader('ip_database/GeoLite2-Country-2.mmdb')
    continents = []
    countries = []
    for  index, ip in enumerate(data['ip']):
        try:
            response = reader.country(ip)
            continents.insert(index, response.continent.names['en'])
            countries.insert(index, response.country.names['en'])
        except:
            continents.insert(index, 'unknown')
            countries.insert(index, 'unknown')
    data['continent'] = continents[:len(data)]
    data['country'] = countries[:len(data)]
    data = data[['ip', 'continent', 'country', 'timestamp', 'timezone', 'request_method', 'request_type', 'status_code', 'response_size', 'referer', 'browser']] # changing columns order


    # Filling nulls
    for col in data.columns:
        if data[col].dtype == "object": # for elements of type object/string, replace nulls with the string "None"
            data[col].fillna("None", inplace=True)
        else: # for elements of other types than object/string, replace nulls with the numeric value 0
            data[col].fillna(0, inplace=True)


    # Encoding with LableEncoder
    encodedData = data.copy()
    encodedData = encodedData.drop('ip', axis=1)
    labelEncoder = LabelEncoder() # create new instance of label encoder
    for col in encodedData.columns:
        if col in ['continent', 'country', 'timezone', 'request_method', 'request_type', 'referer', 'browser']: # for elements of type object/string, replace nulls with the string "None"
            encodedData[col] = labelEncoder.fit_transform(data[col]) # use labelEncoder to encode elements of type object/string with numeric values and replace them in the same dataframe
    # timestamp transformation
    encodedData['timestamp'] = pd.to_datetime(data['timestamp']).map(pd.Timestamp.timestamp) # transform date time string into timestamp of type float64


    # Model loading
    with open('IF_model', 'rb') as file:
        model = pickle.load(file)


    # Anomaly detection
    score_column = model.decision_function(encodedData.values)
    anomaly_column = model.predict(encodedData.values)


    results = data.copy()
    results['index'] = list(map(lambda v: v+1, results.index)) # adding index column for showing
    results = results[['index', 'ip', 'continent', 'country', 'timestamp', 'timezone', 'request_method', 'request_type', 'status_code', 'response_size', 'referer', 'browser']] # setting columns order as wanted
    results['score'] = score_column
    results['anomaly'] = anomaly_column
    results['anomaly'] = results['anomaly'].map({1: 0, -1: 1})
    results = results.sort_values('score')
    

    # sending results
    columnsList = results.columns.values
    entriesCount = len(results)
    valueCounts =  results['anomaly'].value_counts()
    normalValuesCount = valueCounts[0]
    anomaliesCount = valueCounts[1]
    filter = (results['anomaly'] == 1)
    anomaliesList = results[filter].values
    json = jsonify(
        entriesCount = entriesCount,
        normalValuesCount = normalValuesCount.item(),
        anomaliesCount = anomaliesCount.item(),
        columnsList = columnsList.tolist(),
        anomaliesList = anomaliesList.tolist()
        )
    
    return json