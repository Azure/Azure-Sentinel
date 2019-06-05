from Registry import Registry
from Registry.RegistryParse import ParseException

class RegiHelper(object):
    root_path = 'ROOT'
    
    def __init__(self, hive_path):
        self.hive = Registry.Registry(hive_path)
        self.root = self.hive.root()
        self.current_key = self.root
    
    def get_current_subkey_name_path_tuples(self):
        #return [(k.name(), k.path()) for k in self.current_key.subkeys()] 
        if self.current_key is not None and self.current_key.subkeys_number() != 0:
            tup_list = [(k.name(), k.path()) for k in self.current_key.subkeys()]
            return [(n, p[5:]) if self.root_path in p else (n, p) for (n, p) in tup_list]
        else:
            return []
        
    def find_key_by_path(self, key_path):
        try:
            if key_path.strip() == '':
                return self.root;
            else:
                return self.hive.open(key_path)
        except Registry.RegistryKeyNotFoundException:
            print("Couldn't find Run key. Exiting...")
            sys.exit(-1)
            
    def set_current_key(self, key_path):
        self.current_key = self.find_key_by_path(key_path)

    def get_value_name_list(self):
        if self.current_key.values_number() != 0:  
            return [v.name() for v in self.current_key.values()]
        else:
            return []
        
    def get_value_list(self):
        if self.current_key.values_number() != 0:  
            return [v for v in self.current_key.values()]
        else:
            return []