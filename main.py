from projects import create_app  # import the application factory from the projects package


app = create_app()  # create the Flask app instance using the factory

if __name__ == '__main__':  # run the following only when this file is executed directly
    app.run(host="0.0.0.0", port=5000, debug=True)  # start the development server on all interfaces so others can also access the page as long as they're connected with the same network
    
# Notes:
# - host="0.0.0.0" makes the server accessible from other machines on the network
# - port=5000 is the default Flask port
# - debug=True enables auto-reload and the interactive debugger for testing (avoid in production)
