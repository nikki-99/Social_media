

from social_media import create_app
# it takes config class as default 
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)        