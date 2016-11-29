import json

search_configs = [
        {
            'name':'test_run',
            'rule':'apple lang:en',
            'start':'2016-07-25T00:00',
            'end':'2016-07-26T00:00',
            'max_tweets':1000
        }
        ]
labeling_config = {
        'label_fraction':0.1, # score this fraction of the tweets 
        'max_num_to_label':10, # never score more than this number of tweets
        # only display tweet bodies, with newlines stripped out
        'payload_element_to_score':lambda x: {'body':x['body'].replace('\n',' ')}
        }

class AppleVarietyRejector(object):
    apple_varieties = ['gala','fuji','granny smith']
    def filter(self,tweet):
        return all( [token.lower() not in self.apple_varieties for token in tweet['body'].split()] )

class LongNameFilter(object): 
    def filter(self,tweet):
        preferred_name = tweet['actor']['preferredUsername'] 
        if len(preferred_name) > 9:
            return True
        else:
            return False

class NameLengthClassifier(object):
    def classify(self,tweet):
        try:
            preferred_name = tweet['actor']['preferredUsername'] 
        except json.JSONDecodeError:
            return -1
        return len(preferred_name)

class AppleDeviceClassifier(object):
    classes = {
            'iphone':['iphone','iphone5','iphone5s','iphone5c','iphone5se','iphone6','iphone6s','iphone6plus'],
            'ipad':['ipad','ipadair','ipadair2','ipad2','ipad3','ipadmini'],
            'macbook':['macbook','mbp','macbookpro'],
            }
    def classify(self,tweet):
        tokens = [token.lower().strip().rstrip() for token in tweet['body'].split()]
        if any( [token in self.classes['iphone'] for token in tokens] ):
            return 'iphone'
        if any( [token in self.classes['ipad'] for token in tokens] ):
            return 'ipad'
        if any( [token in self.classes['macbook'] for token in tokens] ):
            return 'macbook'
        return 'other'
        
config = {  'search_config': search_configs[0],
            'labeling_config' : labeling_config,
            'name' : 'test_run'
        }
config['filter'] = AppleVarietyRejector()
config['classifier'] = AppleDeviceClassifier()

