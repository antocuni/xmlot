
import logging
import os

logger = logging.getLogger('settings')

# media root needs to be an absolute path for the file open functions
# to function correctly
CAMELOT_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# backup root is the directory where the default backups are stored
CAMELOT_BACKUP_ROOT = os.path.join(os.path.dirname(__file__), 'backup')

# default extension for backup files
CAMELOT_BACKUP_EXTENSION = 'db'

# template used to create and find default backups
CAMELOT_BACKUP_FILENAME_TEMPLATE = 'default-backup-%(text)s.' + CAMELOT_BACKUP_EXTENSION


def ENGINE():
    """This function should return a connection to the database"""
    from sqlalchemy import create_engine
    return create_engine('sqlite:///:memory:')
    #return create_engine('sqlite:///model-data.sqlite')

def setup_model():
    """This function will be called at application startup, it is used to setup
    the model"""
    pass
