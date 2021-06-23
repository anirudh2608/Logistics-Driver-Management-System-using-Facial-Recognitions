from website import create_app

app = create_app()

if __name__ == '__main__':

    """
    Before executing code, Python interpreter reads source file and define few special variables/global variables.
    If the python interpreter is running that module (the source file) as the main program, it sets the special
    __name__ variable to have a value “__main__”. If this file is being imported from another module,
    __name__ will be set to the module’s name. Module’s name is available as value to __name__ global variable.
    """
    app.run(debug=True,port=8029) #Turn debug off in production

