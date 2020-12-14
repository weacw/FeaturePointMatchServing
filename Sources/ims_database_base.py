class ImsDatabaseBase(object):
    def search_single_record(self, rec, pre_filter=None):
        raise NotImplementedError

    def insert_single_record(self, rec):
        raise NotImplementedError

    def insert_multiple_record(self, rec):
        raise NotImplementedError

    def delete_single_record(self, rec):
        raise NotImplementedError

    def search_all_record(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        pass
