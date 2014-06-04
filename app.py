from valverest import create_app

app = create_app(env='local')

if __name__ == '__main__':
    app.run()