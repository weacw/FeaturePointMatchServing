class memory_cache():
    def __init__(self):
        self.all_cache = dict()

    def add_to_cache(self, id, record):
        if id in self.all_cache:
            return False
        self.all_cache[id] = record
        return True

    def get_from_cache(self, id):
        if id in self.all_cache:
            return self.all_cache[id]
        return None

    def get_cache_len(self):
        return len(self.all_cache)

    def re_cache(self, records):
        for record_source in records:
            record = record_source['_source']
            self.add_to_cache(record['id'], record)
        return True
