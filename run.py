from app import app
# from flask_script import Manager
# from flask_bootstrap import Bootstrap

# manager = Manager(app)
# bootstrap = Bootstrap(app)

if __name__ == "__main__":
    # manager.run()
    app.run(host='127.0.0.1', port=8110, debug=True)
