import numpy

def precision(labeled_tweets):
    return numpy.mean([tweet['LBLR_label'] for tweet in labeled_tweets])
setattr(precision,'metric_name','precision')
