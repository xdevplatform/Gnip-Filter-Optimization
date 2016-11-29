#!/usr/bin/env python

# input is a single dictionary, representing the configuration
from my_objects import config

# import functions
from analysis_functions import *

# use Search API to get PowerTrack data (Tweets)
#pt_data_generator = get_pt_data_generator(config['search_config']) 

# save Tweets to disk
#tweets = save_data_to_disk(pt_data_generator,config['search_config'])

# read Tweets from disk
tweets = list(generate_data_from_disk(config['search_config'])) 

# describe Tweets in PowerTrack data
tweets_description = describe_data(tweets)

# hand-label Tweets and print metrics
labeled_tweets = get_labeled_tweets(tweets, config['labeling_config'])  
pt_filter_metrics = calculate_metrics(labeled_tweets)
print("PT filter metrics: " + str(pt_filter_metrics))

# filter Tweets with a custom, downstream filter
filtered_tweets = list(filter_data(tweets,config['filter']))

# describe filtered Tweets
filtered_tweets_description = describe_data(filtered_tweets)

# hand-label filtered Tweets
labeled_filtered_tweets = get_labeled_tweets(filtered_tweets, config['labeling_config'])
filter_metrics = calculate_metrics(labeled_filtered_tweets)
print("Downstream filter metrics: " + str(filter_metrics))

# Segment Tweets with a classifier
classified_data = classify_data(tweets,config['classifier'])

classified_data_descriptions = { 
        class_label:describe_data(class_data) 
        for class_label,class_data in classified_data.items() 
        }

#classified_data_labeled = {
#        class_label:get_labeled_tweets(class_data, config['labeling_config']) 
#        for class_label,class_data in classified_data.items()
#        }

#classified_data_metrics = {
#        class_label:calculate_metrics(class_data) 
#        for class_label,class_data in classified_data_labeled.items()  
#        }

#######
# print or save things

from gnip_tweet_evaluation import output
output.dump_results(classified_data_descriptions['iphone'], './results/', config['name'])
