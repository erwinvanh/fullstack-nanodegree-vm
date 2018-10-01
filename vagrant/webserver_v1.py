from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print('Received request')
        if self.path.endswith("/hello"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>Hello!</h1>"
            output += "<form method='POST' enctype='multipart/form-data' action='/hello'>"
            output += "<h2>What would you like me to say?</h2><input name='message' type='text' >"
            output += "<input type='submit' value='Submit'> </form>"
            output += "</body></html>"
            self.wfile.write(bytes(output, " utf-8"))
            print(output)
            return

        if self.path.endswith("/hola"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>&#161 Hola !</h1>"
            output += "<form method='POST' enctype='multipart/form-data' action='/hello'>"
            output += "<h2>What would you like me to say?</h2><input name='message' type='text' >"
            output += "<input type='submit' value='Submit'> </form>"
            output += "</body></html>"
            self.wfile.write(bytes(output, " utf-8"))
            print(output)
            return
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                self.headers['content-type'])

            # boundary data needs to be encoded in a binary format
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            output = ""
            output += "<html><body>"
            output += " <h2> Okay, how about this: </h2>"
            output += "<h1> {} </h1>".format(messagecontent[0].decode())
            output += "<form method='POST' enctype='multipart/form-data' action='/hello'>"
            output += "<h2>What would you like me to say?</h2><input name='message' type='text' >"
            output += "<input type='submit' value='Submit'> </form>"
            output += "</body></html>"
            self.wfile.write(bytes(output, " utf-8"))
            print(output)
        except:
            pass


def main():
    try:
        print("Starting webserver")
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()
