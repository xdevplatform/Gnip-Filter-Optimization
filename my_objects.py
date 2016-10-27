import json

search_configs = [
        {
            'name':'test_run',
            'rule':'apple lang:en',
            'start':'2016-07-25T00:00',
            'end':'2016-07-26T00:00',
            'max_tweets':5000
        }
        ]
labeling_config = {
        'label_fraction':0.1,
        'max_num_to_label':20, # 
        # only display tweet bodies, with newlines stripped out
        'payload_element_to_score':lambda x: {'body':x['body'].replace('\n',' ')}
        }

config = {  'search_config': search_configs[0],
            'labeling_config' : labeling_config,
            'name' : 'test_run'
        }

class LongNameFilter: 
    def filter(self,tweet):
        preferred_name = tweet['actor']['preferredUsername'] 
        if len(preferred_name) > 9:
            return True
        else:
            return False

my_filter = LongNameFilter()

class NameLengthClassifier:
    def classify(self,tweet):
        try:
            preferred_name = tweet['actor']['preferredUsername'] 
        except json.JSONDecodeError:
            return -1
        return len(preferred_name)
my_classifier = NameLengthClassifier()



