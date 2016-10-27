# Purpose

This sample code is intended to demonstrate the processes and tools
described in the accompanying "Filter Optimization" paper.

# Code Elements

To access Tweet data from the Twitter Search API, you must have a file
called `.creds.yaml` in your local directory with the following structure:
```yaml
username: MY_USER_NAME
password: MY_PASSWORD
search_endpoint: "https://data-api.twitter.com/search/..."
```

## Top-level Control

This repository contains simple examples of collecting data from the Twitter
Search API, and filtering and classifying those Tweets. At each step
in the process, the user can choose to describe the Tweets, in which
descriptive statistics are calculated for the Tweets and associated users.
The user can also choose to calculate performance metrics at each step,
which usually involves had labeling a subset of the Tweets. 
A large set of possible operations is defined in `run.py`. This executable
script is meant to define the overall configuration of operations.
The script imports the core set of functions (description, filtering,
labeling, and classification). The script also import custom implementations
of the filter and the classifier, as well as configuration data for
the operations.

## Custom Objects

The module `my_objects` contains a variety of custom configuration
dictionaries, all of which are packaged into a main `config` dictionary.
It also defines a trivial filter and classifier, mainly to demonstrate 
the expected form for these objects. The filter selects Tweets produced
by users with usernames longer than 9 characters, and the classifier labels
Tweets by the length of their author's username.

## Analysis Functions

The module `analysis_functions` contains base function definitions.
These functions are highly configurable via their configuration and
shouldn't need modification for simple workflow changes. 

Functions in this module use the `lblr` module for hand-labeling, and
the `metrics_lib` module for definitions of corpus-quality metrics.

 
