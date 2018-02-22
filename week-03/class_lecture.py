import pandas as pd
import numpy as np
import matplotlib
%matplotlib inline
#create new dataframe
df = pd.DataFrame()
print(df)

#populate the DataFrame
df['name'] = ['Bilbo', 'Frodo', 'Samwise']
df

#creates new colums, gives it name, and inputs the data.
df.assign(height=[0.5,0.4,0.6])

#Read file and change directory
import os
os.chdir('week-03')
df = pd.read_csv('data/skyhook_2017-07.csv', sep=',')

df.head()
#length and width of the dataframe and return a tuple (paired collection of values)
df.shape

#only return the second item
df.shape[1]

#index that return the column names
df.columns

#unique categories
df['cat_name'].unique()
#or
df.cat_name.unique()

#Pull out subsets of data#
#filter by time#

#this is a mask. An array of truw false values. the query is tested for each row.
df['hour'] == 158

#to query we need to pass the mask to the dataframe.
one_fifty_eight = df[df['hour'] == 158]
one_fifty_eight
one_fifty_eight.shape


#only rows in which we have more than 50 pings
df[(df['hour'] == 158) & (df['count'] > 50)]


#how many people cheched in on the 14th
bastille_day = df[df['date'] == '2017-07-14']
bastille_day.head()

#more active than average on bastille bastille_day
#we created a mask that countains the true values for rows where the count is greater than the mean of the count column
bastille_day['count'] > bastille_day['count'].mean()


lovers_of_bastille = bastille_day[bastille_day['count'] > bastille_day['count'].mean()]

#automated way of generating summary statistics. Only look into the count column.
lovers_of_bastille['count'].describe()

#generating a table that summarizes by a given value. summary stat on other columns based on the value of a chosen colum of attribute.
df.groupby('date')['count'].sum().plot()

df.groupby('date')['count'].sum().describe()

df['count'].max()
df['count'].min()
df['count'].mean()
df['count'].std()
df['count'].count()


df[df['count'] == df['count'].max()]

#How to clean the data :)

#contiuous hours over a course of a week.
df['hour'].unique()

#goal: take each day and produce 24 hours for each

#convert date to more conventional object
df['date_new'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

#the 24 hour window in dataset corresponds to the day of the week. call a function that takes a timestamp and returns the day of the week
#lambda defines a function after that. Add one because the weekday function is monday to sunday. Our hours are sunday to saturday. So we add one
# so that index of weekday corresponds to our hours.

df['weekday'] = df['date_new'].apply(lambda x: x.weekday() + 1)
df['weekday'].replace(7, 0, inplace = True)


#select 24 hours subsets for each day. Drop columns outside of the 24 hours window on a given day. 
#full week of hours and iterating on 24's
for i in range(0, 168, 24):
    j = range()
    df.drop(df[df.['weekday'] == (i/24) ] &
    (
    (df['hour']) < j | df['hour']) > j + 18)
    )
    ])
