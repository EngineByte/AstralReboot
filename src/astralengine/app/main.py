from astralengine.app.bootstrap import create_application
#from astralengine.app.logging_setup import configure_logging

def main() -> int:
    '''
    Main application entry.
    
    Returns:
        Process exit code.
    '''
    
    #configure_logging()
    
    app = create_application()
    app.run()
    
    return 0