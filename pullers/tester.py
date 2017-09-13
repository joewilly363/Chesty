from pullers import utils
from pprint import pprint

for x in utils.pull_config():

    print(x)
    pprint(x.pull_records())