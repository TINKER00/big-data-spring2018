# Problem Set 3: Scraping and Cleaning Twitter Data

Now that you know how to scrape data from Twitter, let's extend the exercise a little so you can show us what you know. You will set up the scraper, clean the resulting data, and visualize it. Make sure you get your own Twitter key (AND make sure that you don't accidentally push it to GitHub); careful with your `.gitignore`.

## Graphic Presentation

Make sure to label all your axes and add legends and units (where appropriate)! Think of these graphs as though they were appearing in a published report for an audience unfamiliar with the data.

## Don't Work on Incomplete Data!

One of the dangers of cleaning data is that you inadvertently delete data that is pertinent to your analysis. If you find yourself getting strange results, you can always run previous portions of your script again to rewind your data. See the section called 'reloading your Tweets in the workshop.

## Deliverables

### Push to GitHub

1. A Python script that contains your scraper code in the provided submission folder. You can copy much of the provided scraper, but you'll have to customize it. This should include the code to generate two scatterplots, and the code you use to clean your datasets.
2. Extra Credit: A Python script that contains the code you used to scrape Wikipedia with the BeautifulSoup library.

### Submit to Stellar

1. Your final CSV files---one with no search term, one with your chosen search term---appropriately cleaned.
2. Extra Credit: A CSV file produced by your BeautifulSoup scraper.

## Instructions

### Step 1

Using the Twitter REST API, collect at least 80,000 tweets. Do not specify a search term. Use a lat/lng of `42.359416,-71.093993` and a radius of `5mi`. Note that this will probably take 20-30 minutes to run.

```python
# In the file you should define two variables (these must be strings!)
api_key = "your twitter key"
api_secret = "your twitter secret"
```

```python
import jsonpickle
import tweepy
import pandas as pd

# Imports the keys from the python file
# You may need to change working directory
import os
os.chdir('week-04')
from twitter_keys import api_key, api_secret
```

```python
auth = tweepy.AppAuthHandler(api_key, api_secret)
# wait_on_rate_limit and wait_on_rate_limit_notify are options that tell our API object to automatically wait before passing additional queries if we come up against Twitter's wait limits (and to inform us when it's doing so).
api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
```

```python
def auth(key, secret):
  auth = tweepy.AppAuthHandler(key, secret)
  api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
  # Print error and exit if there is an authentication error
  if (not api):
      print ("Can't Authenticate")
      sys.exit(-1)
  else:
      return api
```

```python
api = auth(api_key, api_secret)
```
```python
def parse_tweet(tweet):
  p = pd.Series()
  if tweet.coordinates != None:
    p['lat'] = tweet.coordinates['coordinates'][0]
    p['lon'] = tweet.coordinates['coordinates'][1]
  else:
    p['lat'] = None
    p['lon'] = None
  p['location'] = tweet.user.location
  p['id'] = tweet.id_str
  p['content'] = tweet.text
  p['user'] = tweet.user.screen_name
  p['user_id'] = tweet.user.id_str
  p['time'] = str(tweet.created_at)
  return p
```


```python
```python
def get_tweets(
    geo,
    out_file,
    search_term = '',
    tweet_per_query = 100,
    tweet_max = 150,
    since_id = None,
    max_id = -1,
    write = False
):
  tweet_count = 0
  all_tweets = pd.DataFrame()
  while tweet_count < tweet_max:
    try:
      if (max_id <= 0):
        if (not since_id):
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo
          )
        else:
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo,
            since_id = since_id
          )
      else:
        if (not since_id):
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo,
            max_id = str(max_id - 1)
          )
        else:
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo,
            max_id = str(max_id - 1),
            since_id = since_id
          )
      if (not new_tweets):
        print("No more tweets found")
        break
      for tweet in new_tweets:
        all_tweets = all_tweets.append(parse_tweet(tweet), ignore_index = True)
        if write == True:
            with open(out_file, 'w') as f:
                f.write(jsonpickle.encode(tweet._json, unpicklable=False) + '\n')
      max_id = new_tweets[-1].id
      tweet_count += len(new_tweets)
    except tweepy.TweepError as e:
      # Just exit if any error
      print("Error : " + str(e))
      break
  print (f"Downloaded {tweet_count} tweets.")
  return all_tweets

# Set a Lat Lon
latlng = '42.359416,-71.093993' # Eric's office (ish)
# Set a search distance
radius = '5mi'
# See tweepy API reference for format specifications
geocode_query = latlng + ',' + radius
# set output file location
file_name = 'data/tweets.json'
# set threshold number of Tweets. Note that it's possible
# to get more than one
t_max = 80000

```

```python
tweets = get_tweets(
  geo = geocode_query,
  tweet_max = t_max,
  write = True,
  out_file = file_name
)

```
#save the raw data (only ran once when I saved the file)
```python
tweets.to_csv('/Users/arianna/Desktop/github/big-data-spring2018/week-04/data/tweets_parsed.csv')
```
#import the 80,000 downloaded tweets and save it to a df
```python
df = pd.read_csv('/Users/arianna/Desktop/github/big-data-spring2018/week-04/data/tweets_parsed.csv', low_memory=False, sep=',')

# Import some additional libraries that will allow us to plot and interact with the operating system
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

df.dtypes
```

### Step 2

Clean up the data so that variations of the same user-provided location name are replaced with a single variation. Once you've cleaned up the locations, create a pie chart of user-provided locations. Your pie chart should strive for legibility! Let the [`matplotlib` documentation](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.pie.html) be your guide!
```python

#drop missing values of location. Dropped 12,645 tweets that had no location assigned to them.
df = df.dropna(subset=['location'])
df.head()
#drop duplicate tweets
df.shape
```

#We want to classify massachusetts tweets. So, I first replace all the Boston names with the counties. That way, later I can exclude all the tweets outside massachusetts

```python
df = df.copy()
df.loc[df['location'].str.contains('Barnstable', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Bourne', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Brewster', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Chatham', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Dennis', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Eastham', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Falmouth', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Harwich', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Mashpee', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Orleans', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Provincetown', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Sandwich', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Truro', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Wellfleet', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Yarmouth', case=False), 'location'] = 'Barnstable'


df.loc[df['location'].str.contains('Adams', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Alford', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Becket', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Cheshire', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Clarksburg', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Dalton', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Egremont', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Florida', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Great Barrington', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Hancock', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Hinsdale', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Lanesborough', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Lee', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Lenox', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Monterey', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Mount Washington', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('New Ashford', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('New Marlborough', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('North Adams', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Otis', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Peru', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Pittsfield', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Richmond', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Sandisfield', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Savoy', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Sheffield', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Stockbridge', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Tyringham', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Washington', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('West Stockbridge', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Williamstown', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Windsor', case=False), 'location'] = 'Berkshire'


df.loc[df['location'].str.contains('Abington', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Acushnet', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Attleboro', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Berkley', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Dartmouth', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Dighton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Easton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Fairhaven', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Fall River', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Freetown', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Mansfield', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('New Bedford', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('North Attleborough', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Norton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Raynham', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Rehoboth', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Seekonk', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Somerset', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Swansea', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Taunton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Westport', case=False), 'location'] = 'Bristol'


df.loc[df['location'].str.contains('Abington', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Aquinnah', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Chilmark', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Edgartown', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Gosnold', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Oak Bluffs', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Tisbury', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('West Tisbury', case=False), 'location'] = 'Dukes'

df.loc[df['location'].str.contains('Amesbury', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Andover', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Beverly', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Boxford', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Danvers', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Essex', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Georgetown', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Gloucester', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Groveland', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Hamilton', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Haverhill', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Ipswich', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Lawrence', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Lynn', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Lynnfield', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Manchester-by-the-Sea', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Marblehead', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Merrimac', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Methuen', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Middleton', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Nahant', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Newbury', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Newburyport', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('North Andover', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Peabody', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Rockport', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Rowley', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Salem', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Salisbury', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Saugus', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Swampscott', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Topsfield', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Wenham', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('West Newbury', case=False), 'location'] = 'Essex'


df.loc[df['location'].str.contains('Ashfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Bernardston', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Buckland', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Charlemont', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Colrain', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Conway', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Deerfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Erving', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Gill', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Greenfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Hawley', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Heath', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Leverett', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Leyden', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Monroe', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Montague', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('New Salem', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Northfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Orange', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Rowe', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Shelburne', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Shutesbury', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Sunderland', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Warwick', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Wendell', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Whately', case=False), 'location'] = 'Franklin'

df.loc[df['location'].str.contains('Agawam', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Blandford', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Brimfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Chester', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Chicopee', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('East Longmeadow', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Granville', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Hampden', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Holland', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Holyoke', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Longmeadow', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Ludlow', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Monson', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Montgomery', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Palmer', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Russell', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Southwick', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Springfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Tolland', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Wales', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('West Springfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Westfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Wilbraham', case=False), 'location'] = 'Hampden'

df.loc[df['location'].str.contains('Amherst', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Belchertown', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Chesterfield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Cummington', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Easthampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Goshen', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Granby', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Hadley', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Hatfield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Huntington', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Middlefield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Northampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Pelham', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Plainfield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('South Hadley', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Southampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Ware', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Westhampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Williamsburg', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Worthington', case=False), 'location'] = 'Hampshire'

df.loc[df['location'].str.contains('Acton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Arlington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Ashby', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Ashland', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Ayer', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Bedford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Belmont', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Billerica', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Boxborough', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Burlington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Cambridge', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Carlisle', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Chelmsford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Concord', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Dracut', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Dunstable', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Everett', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Framingham', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Groton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Holliston', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Hopkinton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Hudson', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Lexington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Lincoln', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Littleton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Lowell', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Malden', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Marlborough', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Maynard', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Medford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Melrose', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Natick', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Newton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('North Reading', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Pepperell', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Reading', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Sherborn', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Shirley', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Somerville', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Stoneham', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Stow', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Sudbury', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Tewksbury', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Townsend', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Tyngsborough', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Wakefield', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Waltham', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Watertown', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Wayland', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Westford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Weston', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Wilmington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Winchester', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Woburn', case=False), 'location'] = 'Middlesex'

df.loc[df['location'].str.contains('nantucket', case=False), 'location'] = 'Nantucket'

df.loc[df['location'].str.contains('Avon', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Bellingham', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Braintree', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Brookline', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Canton', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Cohasset', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Dedham', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Dover', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Foxborough', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Franklin', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Holbrook', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Medfield', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Medway', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Millis', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Milton', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Needham', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Norfolk', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Norwood', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Plainville', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Quincy', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Randolph', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Sharon', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Stoughton', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Walpole', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Wellesley', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Westwood', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Weymouth', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Wrentham', case=False), 'location'] = 'Norfolk'


df.loc[df['location'].str.contains('Bridgewater', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Brockton', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Carver', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Duxbury', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('East Bridgewater', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Halifax', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hanover', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hanson', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hingham', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hull', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Kingston', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Lakeville', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Marion', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Marshfield', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Mattapoisett', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Middleborough', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Norwell', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Pembroke', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Plymouth', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Plympton', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Rochester', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Rockland', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Scituate', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Wareham', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('West Bridgewater', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Whitman', case=False), 'location'] = 'Plymouth'

df.loc[df['location'].str.contains('Boston', case=False), 'location'] = 'Suffolk'
df.loc[df['location'].str.contains('Chelsea', case=False), 'location'] = 'Suffolk'
df.loc[df['location'].str.contains('Revere', case=False), 'location'] = 'Suffolk'
df.loc[df['location'].str.contains('Winthrop', case=False), 'location'] = 'Suffolk'

df.loc[df['location'].str.contains('Ashburnham', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Athol', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Auburn', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Barre', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Berlin', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Blackstone', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Bolton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Boylston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Charlton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Clinton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Douglas', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Dudley', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('East Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Fitchburg', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Gardner', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Grafton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Hardwick', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Harvard', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Holden', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Hopedale', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Hubbardston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Lancaster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Leicester', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Leominster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Lunenburg', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Mendon', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Milford', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Millbury', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Millville', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('New Braintree', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('North Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Northborough', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Northbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Oakham', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Oxford', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Paxton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Petersham', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Phillipston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Princeton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Royalston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Rutland', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Shrewsbury', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Southborough', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Southbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Spencer', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Sterling', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Sturbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Sutton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Templeton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Upton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Uxbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Warren', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Webster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('West Boylston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('West Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Westborough', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Westminster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Winchendon', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Worcester', case=False), 'location'] = 'Worcester'

#drop all tweets that have not been classified as being in massachusetts counties.
df = df.drop(df[(df.location !='Worcester')
& (df.location !='Plymouth')
& (df.location !='Suffolk')
& (df.location !='Norfolk')
& (df.location !='Middlesex')
& (df.location !='Nantucket')
& (df.location !='Hampshire')
& (df.location !='Hampden')
& (df.location !='Franklin')
& (df.location !='Essex')
& (df.location !='Dukes')
& (df.location !='Bristol')
& (df.location !='Berkshire')
& (df.location !='Barnstable')].index)

df
```

#export cleaned twitter file as a csv. Here every user has a unique location assigned to them.
```python
df.to_csv('/Users/arianna/Desktop/github/big-data-spring2018/week-04/data/cleaned/tweets_clean.csv')

loc_tweets = df[df['location'] != '']
count_tweets = loc_tweets.groupby('location')['id'].count()
df_count_tweets = count_tweets.to_frame()
df_count_tweets
df_count_tweets.columns
df_count_tweets.columns = ['count']
df_count_tweets

df_count_tweets.sort_index()
```
#create pie chart
```python

plt.rcParams['font.size'] = 10.0
fig = plt.figure(figsize=[20, 20])
ax = fig.add_subplot(222)
labels=df_count_tweets.index.get_values()
patches, texts = plt.pie(df_count_tweets, colors=colors, shadow=False, startangle=-10)
plt.legend(patches, labels, loc="best")

colors = ["#697dc6","#5faf4c","#7969de","#b5b246",
          "#cc54bc","#4bad89","#d84577","#4eacd7",
          "#cf4e33","#894ea8","#cf8c42","#d58cc9",
          "#737632","#9f4b75","#c36960"]
plt.pie(df_count_tweets['count'], shadow=False, counterclock=False, autopct="%1.2f%%", colors=colors, pctdistance=1.3, labeldistance=1.2, radius=1)
plt.axis('equal')
plt.title('Percentage of Tweets by County in Massachusetts')  
plt.show()
```

```python
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tools.plotting import table
```
### Step 3

#Create a scatterplot showing all of the tweets are that are geolocated (i.e., include a latitude and longitude).

Create a filter from df_tweets filtering only those that have values for lat and lon

```python
tweets_geo = df[df['lon'].notnull() & df['lat'].notnull()]
len(tweets_geo)
```

```python
#Scatter Plot
plt.figure(figsize=(8, 4))
plt.scatter(tweets_geo['lon'], tweets_geo['lat'], s = 30)
plt.axes().get_xaxis().set_ticks([])
plt.axes().get_yaxis().set_ticks([])
plt.ylabel('Longitude')
plt.xlabel('Latitude')
plt.title('Tweets in Massachusetts Counties')
plt.show()
```

### Step 4

Pick a search term (e.g., "housing", "climate", "flood") and collect tweets containing it. Use the same lat/lon and search radius for Boston as you used above. Dpending on the search term, you may find that there are relatively few available tweets.


```python
def parse_tweet(tweet):
  p = pd.Series()
  if tweet.coordinates != None:
    p['lat'] = tweet.coordinates['coordinates'][0]
    p['lon'] = tweet.coordinates['coordinates'][1]
  else:
    p['lat'] = None
    p['lon'] = None
  p['location'] = tweet.user.location
  p['id'] = tweet.id_str
  p['content'] = tweet.text
  p['user'] = tweet.user.screen_name
  p['user_id'] = tweet.user.id_str
  p['time'] = str(tweet.created_at)
  return p
```

```python
```python
def get_tweets(
    geo,
    out_file,
    search_term = 'climate',
    tweet_per_query = 100,
    tweet_max = 150,
    since_id = None,
    max_id = -1,
    write = False
):
  tweet_count = 0
  all_tweets = pd.DataFrame()
  while tweet_count < tweet_max:
    try:
      if (max_id <= 0):
        if (not since_id):
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo
          )
        else:
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo,
            since_id = since_id
          )
      else:
        if (not since_id):
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo,
            max_id = str(max_id - 1)
          )
        else:
          new_tweets = api.search(
            q = search_term,
            rpp = tweet_per_query,
            geocode = geo,
            max_id = str(max_id - 1),
            since_id = since_id
          )
      if (not new_tweets):
        print("No more tweets found")
        break
      for tweet in new_tweets:
        all_tweets = all_tweets.append(parse_tweet(tweet), ignore_index = True)
        if write == True:
            with open(out_file, 'w') as f:
                f.write(jsonpickle.encode(tweet._json, unpicklable=False) + '\n')
      max_id = new_tweets[-1].id
      tweet_count += len(new_tweets)
    except tweepy.TweepError as e:
      # Just exit if any error
      print("Error : " + str(e))
      break
  print (f"Downloaded {tweet_count} tweets.")
  return all_tweets

# Set a Lat Lon
latlng = '42.359416,-71.093993' # Eric's office (ish)
# Set a search distance
radius = '5mi'
# See tweepy API reference for format specifications
geocode_query = latlng + ',' + radius
# set output file location
file_name = 'data/tweets_search_term.json'
# set threshold number of Tweets. Note that it's possible
# to get more than one
t_max = 5000


```python
tweets = get_tweets(
  geo = geocode_query,
  tweet_max = t_max,
  write = True,
  out_file = file_name
)
```
#Store the raw data of tweets searching climate (only run once after the twitter API function)
```python
tweets.to_csv('/Users/arianna/Desktop/github/big-data-spring2018/week-04/data/tweets_search_term.csv')

#load tweets
df_tweet_search = pd.read_csv('/Users/arianna/Desktop/github/big-data-spring2018/week-04/data/tweets_search_term.csv', sep=',')
len(df_tweet_search)

```
### Step 5

Clean the search term data as with the previous data.

#drop missing locations (same as before)
```python
df_tweet_search = df_tweet_search.dropna(subset=['location'])
df.shape

#Given that for specific terms there are less terms, we could consider a more granular cleaning here. But for consistency I decided to keep the same cleaning scheme as the previous question.
df = df_tweet_search.copy()
df.loc[df['location'].str.contains('Barnstable', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Bourne', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Brewster', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Chatham', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Dennis', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Eastham', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Falmouth', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Harwich', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Mashpee', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Orleans', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Provincetown', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Sandwich', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Truro', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Wellfleet', case=False), 'location'] = 'Barnstable'
df.loc[df['location'].str.contains('Yarmouth', case=False), 'location'] = 'Barnstable'


df.loc[df['location'].str.contains('Adams', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Alford', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Becket', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Cheshire', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Clarksburg', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Dalton', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Egremont', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Florida', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Great Barrington', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Hancock', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Hinsdale', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Lanesborough', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Lee', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Lenox', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Monterey', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Mount Washington', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('New Ashford', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('New Marlborough', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('North Adams', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Otis', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Peru', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Pittsfield', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Richmond', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Sandisfield', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Savoy', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Sheffield', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Stockbridge', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Tyringham', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Washington', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('West Stockbridge', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Williamstown', case=False), 'location'] = 'Berkshire'
df.loc[df['location'].str.contains('Windsor', case=False), 'location'] = 'Berkshire'


df.loc[df['location'].str.contains('Abington', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Acushnet', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Attleboro', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Berkley', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Dartmouth', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Dighton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Easton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Fairhaven', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Fall River', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Freetown', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Mansfield', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('New Bedford', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('North Attleborough', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Norton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Raynham', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Rehoboth', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Seekonk', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Somerset', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Swansea', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Taunton', case=False), 'location'] = 'Bristol'
df.loc[df['location'].str.contains('Westport', case=False), 'location'] = 'Bristol'


df.loc[df['location'].str.contains('Abington', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Aquinnah', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Chilmark', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Edgartown', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Gosnold', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Oak Bluffs', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('Tisbury', case=False), 'location'] = 'Dukes'
df.loc[df['location'].str.contains('West Tisbury', case=False), 'location'] = 'Dukes'

df.loc[df['location'].str.contains('Amesbury', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Andover', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Beverly', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Boxford', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Danvers', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Essex', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Georgetown', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Gloucester', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Groveland', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Hamilton', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Haverhill', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Ipswich', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Lawrence', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Lynn', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Lynnfield', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Manchester-by-the-Sea', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Marblehead', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Merrimac', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Methuen', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Middleton', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Nahant', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Newbury', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Newburyport', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('North Andover', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Peabody', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Rockport', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Rowley', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Salem', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Salisbury', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Saugus', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Swampscott', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Topsfield', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('Wenham', case=False), 'location'] = 'Essex'
df.loc[df['location'].str.contains('West Newbury', case=False), 'location'] = 'Essex'


df.loc[df['location'].str.contains('Ashfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Bernardston', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Buckland', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Charlemont', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Colrain', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Conway', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Deerfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Erving', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Gill', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Greenfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Hawley', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Heath', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Leverett', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Leyden', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Monroe', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Montague', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('New Salem', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Northfield', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Orange', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Rowe', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Shelburne', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Shutesbury', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Sunderland', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Warwick', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Wendell', case=False), 'location'] = 'Franklin'
df.loc[df['location'].str.contains('Whately', case=False), 'location'] = 'Franklin'

df.loc[df['location'].str.contains('Agawam', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Blandford', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Brimfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Chester', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Chicopee', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('East Longmeadow', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Granville', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Hampden', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Holland', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Holyoke', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Longmeadow', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Ludlow', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Monson', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Montgomery', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Palmer', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Russell', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Southwick', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Springfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Tolland', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Wales', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('West Springfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Westfield', case=False), 'location'] = 'Hampden'
df.loc[df['location'].str.contains('Wilbraham', case=False), 'location'] = 'Hampden'

df.loc[df['location'].str.contains('Amherst', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Belchertown', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Chesterfield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Cummington', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Easthampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Goshen', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Granby', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Hadley', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Hatfield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Huntington', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Middlefield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Northampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Pelham', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Plainfield', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('South Hadley', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Southampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Ware', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Westhampton', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Williamsburg', case=False), 'location'] = 'Hampshire'
df.loc[df['location'].str.contains('Worthington', case=False), 'location'] = 'Hampshire'

df.loc[df['location'].str.contains('Acton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Arlington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Ashby', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Ashland', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Ayer', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Bedford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Belmont', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Billerica', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Boxborough', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Burlington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Cambridge', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Carlisle', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Chelmsford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Concord', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Dracut', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Dunstable', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Everett', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Framingham', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Groton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Holliston', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Hopkinton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Hudson', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Lexington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Lincoln', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Littleton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Lowell', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Malden', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Marlborough', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Maynard', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Medford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Melrose', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Natick', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Newton', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('North Reading', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Pepperell', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Reading', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Sherborn', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Shirley', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Somerville', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Stoneham', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Stow', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Sudbury', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Tewksbury', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Townsend', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Tyngsborough', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Wakefield', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Waltham', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Watertown', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Wayland', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Westford', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Weston', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Wilmington', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Winchester', case=False), 'location'] = 'Middlesex'
df.loc[df['location'].str.contains('Woburn', case=False), 'location'] = 'Middlesex'

df.loc[df['location'].str.contains('nantucket', case=False), 'location'] = 'Nantucket'

df.loc[df['location'].str.contains('Avon', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Bellingham', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Braintree', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Brookline', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Canton', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Cohasset', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Dedham', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Dover', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Foxborough', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Franklin', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Holbrook', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Medfield', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Medway', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Millis', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Milton', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Needham', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Norfolk', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Norwood', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Plainville', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Quincy', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Randolph', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Sharon', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Stoughton', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Walpole', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Wellesley', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Westwood', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Weymouth', case=False), 'location'] = 'Norfolk'
df.loc[df['location'].str.contains('Wrentham', case=False), 'location'] = 'Norfolk'


df.loc[df['location'].str.contains('Bridgewater', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Brockton', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Carver', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Duxbury', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('East Bridgewater', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Halifax', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hanover', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hanson', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hingham', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Hull', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Kingston', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Lakeville', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Marion', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Marshfield', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Mattapoisett', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Middleborough', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Norwell', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Pembroke', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Plymouth', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Plympton', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Rochester', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Rockland', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Scituate', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Wareham', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('West Bridgewater', case=False), 'location'] = 'Plymouth'
df.loc[df['location'].str.contains('Whitman', case=False), 'location'] = 'Plymouth'

df.loc[df['location'].str.contains('Boston', case=False), 'location'] = 'Suffolk'
df.loc[df['location'].str.contains('Chelsea', case=False), 'location'] = 'Suffolk'
df.loc[df['location'].str.contains('Revere', case=False), 'location'] = 'Suffolk'
df.loc[df['location'].str.contains('Winthrop', case=False), 'location'] = 'Suffolk'

df.loc[df['location'].str.contains('Ashburnham', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Athol', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Auburn', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Barre', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Berlin', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Blackstone', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Bolton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Boylston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Charlton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Clinton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Douglas', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Dudley', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('East Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Fitchburg', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Gardner', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Grafton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Hardwick', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Harvard', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Holden', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Hopedale', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Hubbardston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Lancaster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Leicester', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Leominster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Lunenburg', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Mendon', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Milford', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Millbury', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Millville', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('New Braintree', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('North Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Northborough', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Northbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Oakham', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Oxford', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Paxton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Petersham', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Phillipston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Princeton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Royalston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Rutland', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Shrewsbury', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Southborough', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Southbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Spencer', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Sterling', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Sturbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Sutton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Templeton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Upton', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Uxbridge', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Warren', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Webster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('West Boylston', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('West Brookfield', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Westborough', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Westminster', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Winchendon', case=False), 'location'] = 'Worcester'
df.loc[df['location'].str.contains('Worcester', case=False), 'location'] = 'Worcester'

#drop tweets that are not in Massachusetts
df = df.drop(df[(df.location !='Worcester')
& (df.location !='Plymouth')
& (df.location !='Suffolk')
& (df.location !='Norfolk')
& (df.location !='Middlesex')
& (df.location !='Nantucket')
& (df.location !='Hampshire')
& (df.location !='Hampden')
& (df.location !='Franklin')
& (df.location !='Essex')
& (df.location !='Dukes')
& (df.location !='Bristol')
& (df.location !='Berkshire')
& (df.location !='Barnstable')].index)

#export cleaned twitter file as a csv. Here every user has a unique location assigned to them. Unique values of user location = 15081
df.to_csv('/Users/arianna/Desktop/github/big-data-spring2018/week-04/data/cleaned/tweets_clean_termsearch.csv')
```
### Step 6

Create a scatterplot showing all of the tweets that include your search term that are geolocated (i.e., include a latitude and longitude).

# Create a filter from df_tweets filtering only those that have values for lat and lon
```python
tweets_term_geo = df[df['lon'].notnull() & df['lat'].notnull()]

# scatter plot
plt.figure(figsize=(8, 4))
plt.scatter(tweets_term_geo ['lon'], tweets_term_geo ['lat'], s = 30)
plt.ylabel('Longitude')
plt.xlabel('Latitude')
plt.title('Tweets including the search term "climate" in Massachusetts')
plt.show()
```


### Step 7

Export your scraped Twitter datasets (one with a search term, one without) to two CSV files. We will be checking this CSV file for duplicates and for consistent location names, so make sure you clean carefully!

I exported the CSVs at the end of each section.


## Extra Credit Opportunity

Build a scraper that downloads and parses the Wikipedia [List of Countries by Greenhouse Gas Emissions page](https://en.wikipedia.org/wiki/List_of_countries_by_greenhouse_gas_emissions) using BeautifulSoup and outputs the table of countries as as a CSV.


```python
#import packages
import requests
import bs4

#find table
response = requests.get('https://en.wikipedia.org/wiki/List_of_countries_by_greenhouse_gas_emissions')
print(response.text)

soup = bs4.BeautifulSoup(response.text, "html.parser")
soup.title

emissions_saved=""
# find all table ,get the first
table = soup.find_all('table', class_="wikitable")[0]  # Only use the first table
# iterate
for record in table.findAll('tr'):
    emissions=""
    for data in record.findAll('td'):
        emissions=emissions+","+data.text
    emissions_saved=emissions_saved+"\n"+emissions[1:]
print(emissions_saved)
with open('/Users/arianna/Desktop/github/big-data-spring2018/week-04/data/cleaned/wikipedia_greenhouse_emissions.csv', 'a') as the_file:
    the_file.write(emissions_saved)
```
