import json
import os

class Cache():

    cache_file = "app/cache.json"

    def __init__(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as cf:
                try:
                    cache = json.load(cf)
                    self.cache = cache
                except:
                    self.cache = {}
        else:
            self.cache = {}

    def read(self, run, label, index):
        label = label.replace(' ', '_').lower()

        if run in self.cache:
            if label in self.cache[run]:
                if index in self.cache[run][label]:
                    return self.cache[run][label][index]
        return False

    def save(self):
        with open(self.cache_file, "w") as cf:
            cf.write(json.dumps(self.cache))
            cf.write("\n")

    def write(self, run, label, index, value):
        label = label.replace(' ', '_').lower()

        if run not in self.cache:
            self.cache[run] = {}
        if label not in self.cache[run]:
            self.cache[run][label] = {}
        self.cache[run][label][index] = value
