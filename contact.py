from alt_super_dict import Super_dict
import os

class Contact(Super_dict):
    def __init__(self):
        Super_dict.__init__(self)
       
        """
        This class is designed to provide a fast, memory resident cli searchable contact database.
        
        Database fields are specified in the .csv load file in the top row, for example:
        #Name,Comment,Company,Department,Job Title,Business Street,Business City,Business State,
        Business Postal Code,Business Country,Business Fax,Business Phone,Business Phone 2,
        Home Phone,Mobile Phone,Pager,E-mail Display Name,E-mail 2 Address,Notes,Office Location
       
        self.dict_db format is [Name][user specified fields]
        
        Written by Peter Rogers
        (C) Intelligent Planet 2013
        """
       
        self.path = os.getcwd() + '\\'
       
        self.load_file = self.path + 'contacts.csv'
        
        self.prompt_text = 'Contact Search >>>'
        
        #load the dictionary into memory
        self.dict_db = {}
        self.load_csv(self.load_file)
       
       
    def search(self):
        while True:
            q = raw_input(self.prompt_text)
            q = q.rstrip('\n').lower()
            
            if q: 
                if 'exit' in q: return
                res = self.search_func(q)
                if res: print '\n', res
                
                
    def search_func(self, q):
        res = []
        if q in self.index: 
            self.show_info(q)
            return

        res = self.search_info(q)
            
        if q in res: res = [x for x in res if q == x]    #check for exact match
        
        if len(res) > 1: res = self.index_find(q, res)    #check if q resolves to unique entry
        
        if len(res) ==1: 
            key = self.list_view(res)[0]
            self.show_info(key)
            
        else:
            print '\n', len(res), 'Result(s)\n'
    
    
    def show_info(self, key): 
        print '\n'
        self.view(self.display_view(key))
        print '\n'
    
    
    def index_find(self, q, clist):
        out = []
        for item in self.index:
            if q in item:
                if item not in out: out.append(item)
        if len(out) == 1: return out    #filter out duplicate entries and return if unique
        else: return clist
        
        
if __name__ == "__main__":
    x = Contact()
    x.search()
        
        
        
        
       

               
