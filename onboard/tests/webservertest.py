import web

urls = (
    '/test', 'hello'
)
app = web.application(urls, globals())


class hello:
    def GET(self):

        data = web.input()
        try:
            name = data.name
        except AttributeError:
            name = "world"
        return 'Hello, ' + name+ '!'


if __name__ == "__main__":
    app.run()