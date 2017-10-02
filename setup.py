from distutils.core import setup
import py2exe
import sys
 
#this allows to run it with a simple double click.
sys.argv.append('py2exe')
 
py2exe_options = {
        "optimize": 2,
        "bundle_files": 1,
        }
 
setup(
      name = 'checkpass',
      version = '1.0',
      windows = [{ "script":'checkpass.py'}], 
      options = {'py2exe': py2exe_options}
      )