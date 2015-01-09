import os, shutil, getpass

path = os.getcwd() + '\\'    #get the path before we change it
verbose = 0

### Test paths ###
user = getpass.getuser()
dest_path = 'C:/Documents and Settings/' + user + '/Application Data/VanDyke/SecureCRT/Config/Sessions'
source_path = path + 'CRT'

### check if SecureCRT is installed ###
try: 
    os.chdir(dest_path)
    res = 1
    if verbose > 0: print 'SecureCRT detected'
except: res = 0

if res:
    try: 
        cfile = dest_path + '/telnet.ini'
        open(cfile)
        res = 0    
        if verbose > 0: print 'Custom files exist'
    except: res = 1
    
os.chdir(path)    #change back to original working directory
     
if res: 
    #install the custom files in CRT
    try:
        if verbose > 0: print 'Installing SecureCRTcustom files'
        file_list = os.listdir(source_path)
        
        for item in file_list:
            src = source_path + '\\' + item
            dst = dest_path + '/'
            if '.ini' in src: 
                shutil.copy(src, dst)
                if verbose > 0: print 'creating file', dst + item
            else:
                dst_dir = dst + item
                if verbose > 0: print 'creating directory', dst_dir
                shutil.copytree(src, dst_dir, symlinks=False, ignore=None)

    except: print 'CRT setup failed'
    
    
def update(source_path, dest_path):
    try:
        update_list = os.listdir(source_path)
        for item in update_list:
            upd_file = update_path + item
            cur_file = dest_path + item
            if os.path.isfile(upd_file):
                if verbose > 0: print 'checking updates for', item,
                if not os.path.isfile(cur_file):
                    #file does not exist add it
                    if verbose > 0: print 'adding new file', cur_file,
                    shutil.copy(upd_file, cur_file)
                if os.path.getmtime(upd_file) > os.path.getmtime(cur_file): 
                    if verbose > 0: print 'updating file', cur_file
                    shutil.copy(upd_file, cur_file)
                else: 
                    if verbose > 0: print '- ok'
    except: print '*** update failed ***\n', source_path, '>-- to -->',  dest_path
    
        
#Check for updates on config files
print 'Checking for config updates -',
update_path = 'path to the master repository'
source_path = path
update(update_path, source_path)

#Check for updates in pynet files
print '\nChecking for Pynet source updates -\n',

try:
    update_path = 'path to updates'
    ignore = os.path.getmtime(update_path)
except:
    update_path = 'path to master repository'

source_path = path + 'Lib\\site-packages\\pynet\\'
update(update_path, source_path)


### start the CLI
print '\nStarting Pynet\n'
import cli
x = cli.Cli()







  
