import collections
import logging
import json
import random
import yaml
import os

from search.api import Query
from gnip_tweet_evaluation import analysis as tweet_evaluation_module 

import metrics_lib 
import lblr

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()  
stream_handler.setFormatter( logging.Formatter('%(asctime)s %(name)s:%(lineno)s - %(levelname)s - %(message)s')) 
logger.addHandler( stream_handler )
logger.setLevel(logging.INFO)


def get_pt_data_generator(config):
    """
    Hit the search API with the rules provided and return data 
    """
    HARD_MAX = 20000

    logger.info('Getting PT data from Gnip API')

    if int(config['max_tweets']) < HARD_MAX:
        HARD_MAX = config['max_tweets']

    creds = yaml.load(open('.creds.yaml'))
    q = Query(creds['username'],
            creds['password'],
            creds['search_endpoint'],
            paged=True,
            hard_max = HARD_MAX,
            search_v2=True
            )
    rule = config['rule']
    start_date = config['start']
    end_date = config['end']
    q.execute(rule,start=start_date,end=end_date)
    data_generator = q.get_activity_set()

    return data_generator

def save_data_to_disk(data,config):
    """
    Save data to file named by PT rule
    """
    logger.info('Saving data to disk') 
   
    try:
        os.mkdir('data')
    except FileExistsError:
        pass

    data_file_name = 'data/' + config['name'] + '.json'
    data = list(data)
    with open(data_file_name,'w') as f:
        for tweet in data: 
            f.write(json.dumps(tweet) + '\n')
    return data

def generate_data_from_disk(config):
    """
    Generator function to yield dictionaries representing Tweets from disk
    """
    
    logger.info('Reading Tweets from disk') 
    
    data_file_name = 'data/' + config['name'] + '.json'
    with open(data_file_name) as f:
        for line in f:
            yield json.loads(line)

def describe_data(tweets):
    """
    Evaluate the Tweets provided and return the results object
    """ 

    logger.info('Describing Tweets')
    results = tweet_evaluation_module.setup_analysis(conversation=True,audience=True)
    tweet_evaluation_module.analyze_tweets(tweets,results)
    return results

def get_labeled_tweets(tweets,labeling_config):
    """ 
    Assign labels to Tweets 
    """

    logger.info('Begin assigning human labels')

    ## create random labels for now
    #labels = [round(random.random()*1.1) for _ in tweets] 
    
    # get subset of Tweets to label
    tweets_to_label = []  
    labeled_counter = 0
    for tweet in tweets:
        if random.random() < float(labeling_config['label_fraction']):
            tweets_to_label.append( labeling_config['payload_element_to_score'](tweet) ) 
            labeled_counter += 1
        if labeled_counter > int(labeling_config['max_num_to_label']):
            break

    # set up labeler
    labeler = lblr.TweetLabeler()
    labeler.input_source = tweets_to_label
    labeled_tweets = labeler.label_tweets()

    logger.info('Done assigning human labels') 
    return labeled_tweets

def calculate_metrics(labeled_tweets,metrics=None):
    """
    Calculate metrics and return them
    """
    if metrics is None:
        logger.info('No metrics specified; running "precision"')
        metrics = [metrics_lib.precision]
    
    logger.info('Calculating filter metrics') 

    metric_values = { (metric.__name__,metric(labeled_tweets) ) for metric in metrics}

    return metric_values

def filter_data(data,the_filter):
    """
    Return Tweets in 'data' that pass the filter
    """
    logger.info('Filtering Tweets') 
    return (tweet for tweet in data if the_filter.filter(tweet) )

def classify_data(data,the_classifier):
    """ 
    classify Tweets and return tuple of classes of Tweets
    """
    logger.info('Classifying Tweets') 
    classes = collections.defaultdict(list)
    for tweet in data:
        tweet_class = the_classifier.classify(tweet)  
        classes[tweet_class].append(tweet)

    return classes
    

