import os
import sys
import time

path_parent = os.path.dirname(os.getcwd())
path_project = os.path.dirname(path_parent)
path_src = os.path.join(path_project, 'src')
sys.path.insert(0, path_src)

import src.node_to_csv

path_test_settings = os.path.join(path_parent, 'local', 'settings.json')
start_time = time.time()
src.node_to_csv.main(path_test_settings)
print("--- %s seconds ---" % (time.time() - start_time))
