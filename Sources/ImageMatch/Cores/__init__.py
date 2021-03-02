import os
import time
import numpy as np
from datetime import datetime


from elasticsearch import Elasticsearch
from elasticsearch import helpers

from ImageMatch.Cores.elasticsearch_driver import ImsES
from ImageMatch.Cores.Utitliy import *
from ImageMatch.Cores.configure_runtime import *
from ImageMatch.Cores.annoyindex_driver import AnnoyIndex_driver
from ImageMatch.Cores.ims_database_base import ImsDatabaseBase
ims = ImsES(Elasticsearch())  

from ImageMatch.Cores.cvmodule import CVModule
CVAlgorithm = CVModule()

from ImageMatch.Cores.memory_cache import memory_cache

#Caching the es data to local RAM
memory_cache = memory_cache()
all_record = ims.search_all_record()
for record in all_record:    
    record_metadata = record['_source']
    memory_cache.add_to_cache(record_metadata['id'],record_metadata)

from ImageMatch.Cores.image_search import ImageSearch

