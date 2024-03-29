# -*- coding: utf-8 -*-
"""Untitled32.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OjTv-x58pE79CFk_IZ5vNdlqmtIcxwhV
"""

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

from sklearn import model_selection, metrics
from sklearn.linear_model import LinearRegression, RANSACRegressor
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

import warnings
warnings.filterwarnings('ignore')

COLOR = 'black'
mpl.rcParams.update({'text.color' : COLOR,
                     'axes.labelcolor' : COLOR,
                     'xtick.color' : COLOR,
                     'ytick.color' : COLOR,
                     'axes.labelsize' : 18,
                     'axes.titlesize' : 18,
                     'xtick.labelsize' : 16,
                     'ytick.labelsize' : 16,
                     'axes.grid' : True,
                     'grid.color' : 'k',
                     'grid.alpha' : 0.4,
                     'grid.linestyle' : ':',
                     'grid.linewidth' : 0.5})

palette = ["#5f0f40","#9a031e","#fb8b24","#e36414","#0f4c5c"]
sns.palplot(sns.color_palette(palette))
plt.show()

def feature_analysis(df, col):    
    df[col].value_counts().plot(kind="pie", autopct='%1.1f%%', figsize=(10,10))
    
    
    return df[col].value_counts(dropna = False).to_frame(name=f"{col} #").style.bar(subset=f"{col} #", color = palette[4])

"""Data Preprocessing


"""

df_raw = pd.read_csv("/content/Automobile_data.csv")
df_raw.head

df_raw.columns

TARGET = "price"

df_raw.info()

df_raw.describe().T

"""Handling Missing Values

"""

for col in df_raw.columns:
    num_of_nans = len(df_raw[df_raw[col]=='?']) 
    if num_of_nans != 0:
        print(f"{col} =  {num_of_nans}")

# Removing all rows with '?'
print(f"Data without '?': {len(df_raw[(df_raw != '?').all(axis=1)].index)/len(df_raw.index)*100:.2f}%")

df0 = df_raw.copy() 
col_to_clean = ["price", "peak-rpm", "horsepower", "stroke", "bore"]
def remove_nans(df, col):
    df[col] = df[col].replace('?',np.nan)
    df[col] = pd.to_numeric(df[col])
    return df[df[col].notna()]
     
for col in col_to_clean:
    df0 = remove_nans(df0, col)
    
print(f"Data without '?': {len(df0.index)/len(df_raw.index)*100:.2f}%")
df0.info()

df0.sample(10).T

df0.describe().T

df0.describe(include=object).T

"""EDA(Exploratory Data Analysis)
feature analysis
"""

feature_analysis(df0, 'make')

plt.figure(figsize=(14,14))
for index, feature in enumerate(df0.describe(include=object).T.index[1:].drop(['make', 'num-of-doors'])):
    plt.subplot(4, 2, index+1)
    plt.tight_layout(pad=3.0)
    plt.axhline(y = 20_000, color = palette[4], linestyle = ':' )
    sns.boxplot(x=feature, y="price", data=pd.concat([df0['price'], df0[feature]], axis=1).sort_values(by = "price"))
    
plt.show()

_, ax = plt.subplots(figsize=(14, 14))

sns.boxplot(x='make', y="price", data=pd.concat([df0['price'], df0['make']], axis=1).sort_values(by = "price"))
ax.axhline(y = 20_000, color = palette[4], linestyle = ':' )
ax.axhline(y = 12_000, color = palette[4], linestyle = ':' )
plt.grid(True, alpha = 0.4, linestyle = ':')
plt.xticks(rotation=45)
plt.title("price vs make", fontsize = 20)
plt.show()

plt.figure(figsize=(14,35))
high_corr_col = ["engine-size", "curb-weight", "horsepower", "city-mpg", "highway-mpg"]

for index, (feature, corr_feature) in enumerate(zip(high_corr_col, df0.select_dtypes(include=np.number).corr()['price'].sort_values(ascending=False).to_frame().T[["engine-size", "curb-weight", "horsepower", "city-mpg", "highway-mpg"]].values[0])):
    plt.subplot(len(high_corr_col), 1, index+1)
    plt.tight_layout(pad=3.0)
    plt.title(f"price vs {feature} with correlation: {corr_feature:.5f}", fontsize = 20)
    plt.axvline(x = 12_000, color = palette[4], linestyle = ':' )
    plt.axvline(x = 20_000, color = palette[4], linestyle = ':' )
    plt.grid(True, alpha = 0.4, linestyle = ':')
    sns.scatterplot(data=df0, x='price', y=feature, color = palette[0])
    
plt.show()

"""Correlation

"""

_ , ax = plt.subplots(figsize =(14, 12))

_ = sns.heatmap(
    df0.corr(), 
    cmap = palette,
    square=True, 
    cbar_kws={'shrink':.9 }, 
    ax=ax,
    annot=True, 
    linewidths=0.1,vmax=1.0, linecolor='white',
    annot_kws={'fontsize':12 }
)

plt.title('Pearson Correlation of Features', y=1.05, size=15)

plt.xticks(rotation=45)
plt.show()

_,ax = plt.subplots(figsize=(16,3))
sns.heatmap(df0.select_dtypes(include=np.number).corr()['price'].sort_values( ascending=False).to_frame().T, 
            cmap = palette,
            annot=True, 
            linewidths=0.1,vmax=1.0, linecolor='white',
            annot_kws={'fontsize':16 }
)

plt.title("Numerical features correlation with price", weight='bold', fontsize=20)
plt.xticks(rotation=45)
plt.show()

"""Initial Model Hypothesis"""

model_col = [TARGET, "engine-size", "curb-weight", "horsepower", "city-mpg", "highway-mpg", "make"]
df_model = df0[model_col].copy()
df_model.sample(10).T

X_train_w, X_test_w, y_train_w, y_test_w = train_test_split(
    df_model.drop([TARGET], axis=1), 
    df_model[TARGET], 
    test_size = 0.20, 
    random_state = 0xBEEF
)

X_train_wout = X_train_w.copy().drop(["make"], axis=1)
X_test_wout = X_test_w.copy().drop(["make"], axis=1)
y_train_wout = y_train_w.copy()
y_test_wout = y_test_w.copy()

X_train_wout.shape

y_train_wout.shape

ecars = df_model["make"].loc[df_model['price'] > 25000].unique()
ecars

df_model[df_model["make"].isin(ecars)].sample(10)

inx = df_model[df_model["make"].isin(ecars)].index
inx

df_model.loc[inx].sample(10)

df_model[~df_model["make"].isin(ecars)].sample(10)

"""Custom  scitik-learn Estimator"""

class WithSplitLinearRegression:
    def __init__(self, 
                 ecars, 
                 elr_params = {}, 
                 clr_params = {}
                 ):
        self.ecars = ecars
        self.elr_params = elr_params
        self.clr_params = clr_params
    
    def fit(self, X_train, y_train):
        ecars_indx = self.get_index(X_train)
        X_train = X_train.drop(["make"], axis = 1)
        
        self.elr = LinearRegression(**self.elr_params).fit(
            X = X_train.loc[ecars_indx], 
            y = y_train.loc[ecars_indx]
        )
        
        self.clr = LinearRegression(**self.clr_params).fit(
            X = X_train[~X_train.index.isin(ecars_indx)], 
            y = y_train[~y_train.index.isin(ecars_indx)]
        )
        
        return self
    
    def predict(self, X_test):
        ecars_indx = self.get_index(X_test)
        X_test = X_test.drop(["make"], axis = 1)

        y_elr = self.elr.predict(X_test.loc[ecars_indx])
        y_clr = self.clr.predict(X_test[~X_test.index.isin(ecars_indx)])
        
        return y_elr, y_clr
    
    def get_index(self, X):
        return X[X["make"].isin(self.ecars)].index

"""Machine learning model

"""

lr_params = {}
lr = LinearRegression(**lr_params).fit(X_train_wout, y_train_wout)
predictions_wout = lr.predict(X_test_wout)
r2_score_wout = r2_score(y_test_wout, predictions_wout)
print(f"r2_score is : {r2_score_wout}")

_ , ax = plt.subplots(figsize =(14, 14))
sns.regplot(
    x = y_test_wout, 
    y = predictions_wout,
    ax = ax,
    color = palette[4] 
)
plt.show()

ecars = df_model["make"].loc[df_model['price'] > 25000].unique()
ecars

elr_params = {}
clr_params = {}

wslr = WithSplitLinearRegression(
    ecars = ecars, 
    elr_params = elr_params, 
    clr_params = clr_params
).fit(X_train_w, y_train_w)

y_pred_e, y_pred_c = wslr.predict(X_test_w)

ecars_indx = wslr.get_index(X_test_w)

r2_score_elr = r2_score(y_test_w.loc[ecars_indx], y_pred_e)
r2_score_clr = r2_score(y_test_w[~y_test_w.index.isin(ecars_indx)], y_pred_c)

print(f"elr r2_score is : {r2_score_elr}")
print(f"clr r2_score is : {r2_score_clr}")

_ , ax = plt.subplots( figsize =(14, 14))

sns.regplot(
    x = y_test_w.loc[ecars_indx], 
    y = y_pred_e,
    ax = ax,
    color = palette[3]
)

sns.regplot(
    x = y_test_w[~y_test_w.index.isin(ecars_indx)], 
    y = y_pred_c,
    ax = ax,
    color = palette[4] 
)

plt.show()

"""Final thoughts"""

print("Model without split on make:")
print(f"\tr2_score is : {r2_score_wout}\n")

print("Model with split on make:")
print(f"\telr r2_score is : {r2_score_elr}")
print(f"\tclr r2_score is : {r2_score_clr}")

