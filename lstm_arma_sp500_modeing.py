# -*- coding: utf-8 -*-
"""LSTM->ARMA .ipynb（SP500 25min for modeing）final

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18ogtl34urj430sx-y4AcQlOy66dgz5NW

## ready
"""
"""## data"""

data = pd.read_csv('/content/gdrive/MyDrive/Colab Notebooks/20180726.csv').dropna()
data = data.set_index('date')
tsPrice = data["close"]
tsPrice.describe()

# Commented out IPython magic to ensure Python compatibility.
# %config InlineBackend.figure_format = "retina"

fig = plt.figure(figsize=(15, 10))
tsPrice.plot()
plt.xlabel("Data", fontsize=15)
plt.ylabel("Index", fontsize=15)
plt.legend(["Index"], loc="upper right", fontsize=16)

plt.xticks(fontsize=15,rotation=30)

plt.yticks(fontsize=15)
¥plt.title("Standard and Poor's 500 index",fontsize=20)
plt.show()

# Commented out IPython magic to ensure Python compatibility.
# %config InlineBackend.figure_format = "retina"

fig = plt.figure(figsize=(15, 10))
plt.hist(tsPrice, bins=25 , facecolor="blue", edgecolor="black", alpha=0.7)
plt.xlabel("Ranges of index", fontsize=15)
plt.ylabel("Frequency", fontsize=15)

plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.title("Histogram of S&P 500",fontsize=20)
plt.show()

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.dates as mdate
# %config InlineBackend.figure_format = "retina"

start_time_string1 = "2018/7/26 09:30:00"
end_time_string2 = "2018/7/26 16:00:00"
x = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 
fig = plt.figure(figsize=(15, 10))
ax1 = fig.add_subplot(1,1,1)
ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d %H:%M'))

plt.title("Differential Standard and Poor's 500 index",fontsize=20)
ax1.set_xlabel("Data", fontsize=15)
ax1.set_ylabel("Index", fontsize=15)

plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xticks(rotation=15)

plt.plot(x, tsPrice.diff(), label='sin')
ax1.legend(["Index"], loc="lower right", fontsize=15)
plt.show()
plt.close()

# Commented out IPython magic to ensure Python compatibility.
lags=9
ncols=3
nrows=int(np.ceil(lags/ncols))
# %config InlineBackend.figure_format = "retina"

fig, axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=(4*ncols, 4*nrows))
 
for ax, lag in zip(axes.flat, np.arange(1,lags+1, 1)):
    lag_str = 't-{}'.format(lag)
    X = (pd.concat([tsPrice, tsPrice.shift(-lag)], axis=1,
                   keys=['y'] + [lag_str]).dropna())
 
    X.plot(ax=ax, kind='scatter', y='y', x=lag_str);
    corr = X.corr().values[0][1]
    ax.set_ylabel('Index')
    ax.set_title('Lag: {} (corr={:.2f})'.format(lag_str, corr));
    ax.set_aspect('equal');

 
fig.tight_layout()
#  fig.tight_layout();

"""## Basic"""

# ADF check
from statsmodels.tsa.stattools import adfuller
def adf_test(timeseries):
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)

adf_test(tsPrice[:5].diff().dropna())
# adf_test(tsPrice)

# find the best order
from statsmodels.tsa.statespace.sarimax import SARIMAX
from tqdm import tqdm_notebook

def optimize_ARIMA(order_list, exog):

    results = []
    
    for order in tqdm_notebook(order_list):
        try: 
            model = SARIMAX(exog, order=order).fit(disp=-1)
        except:
            continue
            
        aic = model.aic
        results.append([order, model.aic])
        
    result_df = pd.DataFrame(results)
    result_df.columns = ['(p, d, q)', 'AIC']
    #Sort in ascending order, lower AIC is better
    result_df = result_df.sort_values(by='AIC', ascending=True).reset_index(drop=True)
    
    return result_df

from itertools import product
ps = range(0, 6, 1)
d = 0
qs = range(0, 6, 1)
parameters = product(ps, qs)
parameters_list = list(parameters)
order_list = []
for each in parameters_list:
    each = list(each)
    each.insert(1, 1)
    each = tuple(each)
    order_list.append(each)

result_df = optimize_ARIMA(order_list, exog=tsPrice[:8].dropna())
print(result_df)

"""## ARMA"""

##using
from statsmodels.tsa.arima.model import ARIMA
from tqdm import tqdm
import time
def ARMA(dataset):

    predictions = []

    for i in tqdm(range(len(data)-25)):
        train_data=dataset["close"][i-1:26+i]
        model = ARIMA(train_data,order=(2, 2, 1))
        model_fit = model.fit()

        output = model_fit.forecast()
        
        predictions.append(output.values[0])

    a=dataset[25:]
    a['arma_pre']=predictions
    a['arma_residual']=a['close']-a['arma_pre']

    return a

from statsmodels.tsa.arima.model import ARIMA
from tqdm import tqdm
import time
def ARMA(dataset):

    predictions = []

    for i in tqdm(range(len(data)-25)):
        train_data=dataset["close"][i-1:26+i]
        model = ARIMA(train_data,order=(2, 1, 1))
        model_fit = model.fit()

        output = model_fit.forecast()
        
        predictions.append(output.values[0])

    a=dataset[25:]
    a['arma_pre']=predictions
    a['arma_residual']=a['close']-a['arma_pre']

    # a['arma_residual']=a-a['arma_pre']
    return a

start = time.perf_counter()

result_df=ARMA(data)

end = time.perf_counter()
print (str(end-start))

from sklearn.metrics import mean_squared_error
from sklearn import metrics
mse1 = mean_squared_error(result_df['arma_pre'][-365:], result_df['close'][-365:])
rmse1 = mse1 ** 0.5
print(rmse1)
MAE1 = metrics.mean_absolute_error(result_df['arma_pre'][-365:], result_df['close'][-365:])
print(MAE1)

# Commented out IPython magic to ensure Python compatibility.
#plot amra only 
# %config InlineBackend.figure_format = "retina"

start_time_string1 = "2018/7/26 09:56:00"
end_time_string2 = "2018/7/26 16:00:00"
x = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 

all_data = result_df['close'][-365:]
test_dataLstm = result_df['arma_pre'][-365:]
plt.figure(figsize=(12, 7))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))

plt.ylabel("Index", fontsize=22)
plt.xlabel("Index", fontsize=22)
plt.plot(x, test_dataLstm, label='predict value')
plt.plot(x, all_data, label='true value')
plt.xlabel("Data", fontsize=22)
plt.ylabel("Index", fontsize=22)
plt.xticks(fontsize=22, rotation=20)
plt.yticks(fontsize=22)
plt.yticks(fontsize=22)
plt.title("Hybrid Model for 25-minutes data)",fontsize=35)

plt.legend(fontsize=22)
plt.show()
plt.close()

# Commented out IPython magic to ensure Python compatibility.
#plot aram differenced final 
# %config InlineBackend.figure_format = "retina"

start_time_string1 = "2018/7/26 09:56:00"
end_time_string2 = "2018/7/26 16:00:00"
x = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 
# %config InlineBackend.figure_format = "retina"


all_data = result_df['close'][-365:].diff()
test_dataLstm = result_df['arma_pre'][-365:].diff()

plt.figure(figsize=(12, 7))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))

plt.plot(x, all_data, label='true value')
plt.plot(x, test_dataLstm, label='predict value')
plt.xticks(rotation=20, fontsize=22)

plt.xlabel("Data", fontsize=22)

plt.yticks(fontsize=22)
plt.title("Hybrid Model for 25-minutes data(Differential data)",fontsize=30)

plt.legend(fontsize=22)
plt.show()
plt.close()

"""## LSTM"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('/content/gdrive/MyDrive/Colab Notebooks/2018072460mins.csv', usecols=['close']).dropna()

#for LSTM ONLY
def get_lstm_only(data, train_len, test_len, lstm_len=25):
    # prepare train and test data
    data = data.tail(test_len + train_len).reset_index(drop=True)
    dataset = np.reshape(data.values, (len(data), 1))
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset_scaled = scaler.fit_transform(dataset)
    x_train = []
    y_train = []
    x_test = []

    for i in range(lstm_len, train_len):
        x_train.append(dataset_scaled[i - lstm_len:i, 0])
        y_train.append(dataset_scaled[i, 0])

  
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))


    window_size = lstm_len
    fea_num = 1

    model = Sequential()
    model.add(LSTM(21, input_shape=(window_size,1)))
    model.add(Dense(21, input_dim = 21))
    model.add(keras.layers.Dropout(0.3))
    model.add(Dense(21, activation="tanh"))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=50)
    prediction = model.predict(x_train)

    prediction = scaler.inverse_transform(prediction).tolist()
    print('pred how many',pd.Series(prediction).describe())

    output = []
    for i in range(len(prediction)):
        output.extend(prediction[i])
    prediction = output

    print('pred how many out ',pd.Series(prediction).describe())
    return prediction

import time
start = time.perf_counter()

lstmPrediction = get_lstm_only(tsPrice, 390, 0)

end = time.perf_counter()

from sklearn.metrics import mean_squared_error
mse2 = mean_squared_error(lstmPrediction[-365:], result_df['close'][-365:])
rmse2 = mse2 ** 0.5
print(rmse2)

MAE2 = metrics.mean_absolute_error(lstmPrediction[-365:], result_df['close'][-365:])
MAE2

# Commented out IPython magic to ensure Python compatibility.
#plot LSTM only 
# %config InlineBackend.figure_format = "retina"

start_time_string1 = "2018/7/26 09:56:00"
end_time_string2 = "2018/7/26 16:00:00"
x = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 

all_data = result_df['close'][-365:]
test_dataLstm = lstmPrediction[-365:]
plt.figure(figsize=(20, 10))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))

plt.plot(x, test_dataLstm, label='predict value')
plt.plot(x, all_data, label='true value')

plt.xlabel("Data", fontsize=15)
plt.ylabel("Index", fontsize=15)
plt.xticks(fontsize=15, rotation=30)
plt.yticks(fontsize=15)
plt.title("Prediction results (LSTM for 25-minutes data)", fontsize=25)
plt.legend(fontsize=15)
plt.show()
plt.close()

# Commented out IPython magic to ensure Python compatibility.
#plot LSTM diff only 
# %config InlineBackend.figure_format = "retina"

start_time_string1 = "2018/7/26 09:37:00"
end_time_string2 = "2018/7/26 16:00:00"
x = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 
x2 = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 
# %config InlineBackend.figure_format = "retina"

# result_df['arma_pre'].plot()
# result_df['close'].plot()

all_data = result_df['close'][-385:].diff().dropna()
diff = [ lstmPrediction[-385:][i]-lstmPrediction[-385:][i+1] for i in range(len(lstmPrediction[-385:])-1) ]
# pd.DataFrame(lstmPrediction[-385:])

# test_dataLstm = pd.DataFrame(lstmPrediction[-385:])
# test_dataLstm = test_dataLstm.diff().dropna()

plt.figure(figsize=(20, 10))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))

plt.plot(x2, diff, label='predict value')
plt.plot(x, all_data, label='true value')

plt.xlabel("Data", fontsize=15)
# plt.ylabel("Index", fontsize=15)
plt.xticks(fontsize=15, rotation=30)
plt.yticks(fontsize=15)
plt.title("Prediction results for differential data (LSTM for 5-minutes data)", fontsize=20)
plt.legend(fontsize=15)
plt.show()
plt.close()

"""## LSTM ARMA"""

from statsmodels.tsa.arima.model import ARIMA
from tqdm import tqdm
import time
def ARMA3(dataset):

    predictions = []

    for i in tqdm(range(len(data)-25)):
        train_data=dataset["close"][0+i:26+i]
        # train_data=dataset[0+i:31+i]
        model = ARIMA(train_data,order=(3, 2, 1))
        model_fit = model.fit()

        output = model_fit.forecast()
        
        predictions.append(output.values[0])
    a=dataset[25:]
    a['arma_pre']=predictions

    return a

start = time.perf_counter()

result_df3=ARMA3(data)

end = time.perf_counter()

print (str(end-start))

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error

mse3 = mean_squared_error(result_df3['close'][-365:], result_df3['arma_pre'][-365:])
rmse3 = mse3 ** 0.5
print(rmse3)

MAE3 = metrics.mean_absolute_error(result_df3['close'][-365:], result_df3['arma_pre'][-365:])
MAE3

# Commented out IPython magic to ensure Python compatibility.
#plot amra only 
# %config InlineBackend.figure_format = "retina"

start_time_string1 = "2018/7/26 09:56:00"
end_time_string2 = "2018/7/26 16:00:00"
x = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 
start_time_string2 ="2018/07/26 14:56:00"
x2 = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 
# %config InlineBackend.figure_format = "retina"

all_data = result_df3['close'][-365:]
test_dataLstm = result_df3['arma_pre'][-365:]
plt.figure(figsize=(20, 10))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))

plt.ylabel("Index", fontsize=15)
plt.xlabel("Index", fontsize=15)
plt.plot(x2, test_dataLstm, label='predict value')
plt.plot(x, all_data, label='true value')
plt.xlabel("Data", fontsize=15)
plt.ylabel("Index", fontsize=15)
plt.xticks(fontsize=15, rotation=30)
plt.yticks(fontsize=15)
plt.yticks(fontsize=15)
plt.title("Prediction results (ARMA Model for 25-minutes data)",fontsize=25)

plt.legend(fontsize=15)
plt.show()
plt.close()

# Commented out IPython magic to ensure Python compatibility.
#plot comprehensieve fightr 
# %config InlineBackend.figure_format = "retina"

start_time_string1 = "2018/7/26 09:56:00"
end_time_string2 = "2018/7/26 16:00:00"
x = pd.date_range(start=start_time_string1, end=end_time_string2, freq="60S") 

plt.figure(figsize=(15, 10))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))


hybirdModel = result_df['arma_pre'][-365:]
armaModel = result_df3['arma_pre'][-365:]
plt.plot(x, all_data, label='true value', color = 'k')
plt.plot(x, armaModel, label='ARMA Model')
plt.plot(x, lstmPrediction[-385:], label='LSTM Model')
plt.plot(x, hybirdModel, label='Hybird Model', color = 'r')

plt.xlabel("Date", fontsize=30)
plt.ylabel("Index", fontsize=30)
plt.xticks(fontsize=30, rotation=20)
plt.yticks(fontsize=30)
plt.yticks(fontsize=30)
plt.title("Comprehensive comparison of results (25-minutes as a windows size)",fontsize=30)

plt.legend()
plt.show()
plt.close()

"""### ARMA lstm"""

res = res.reset_index(drop=True)
print(res)

lstmPredictionOnly = get_lstm_only(res, 41, 10)

lstmPredictionOnly

final = lstmPredictionOnly + result_df['arma_pre'][-10:]

finalv = final.reset_index(drop=True)
finalv

finalc = result_df['close'][-10:].reset_index(drop=True)

finalc.plot()
finalv.plot()

from sklearn.metrics import mean_squared_error
mse1 = mean_squared_error(result_df['close'][-10:], result_df['arma_pre'][-10:])
rmse1 = mse1 ** 0.5
print(rmse1)