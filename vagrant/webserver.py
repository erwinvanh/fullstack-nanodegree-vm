from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/edit"):
            # Get the restaurant from the table
            myRestaurantQuery = session.query(Restaurant).get(int(self.path.split("/")[-2]))
            if myRestaurantQuery:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>" + myRestaurantQuery.name +  "</h1>"
                output += "<form method='POST' enctype='multipart/form-data' "
                output += "action='/restaurants/" + str(myRestaurantQuery.id) +  "/edit'>"
                output += "<input name='newRestaurantName' type='text' "
                output += "placeholder = '" + myRestaurantQuery.name + "'>"
                output += "<input type='submit' value='Rename'> </form>"
                output += "</body></html>"
                self.wfile.write(bytes(output, " utf-8"))
            else:
                print("Restaurant doesn't exist")
                # Redirect to restaurants
                self.send_response(404)
                #self.send_header('Content-type', 'text/html')
                #self.send_header('Location', '/restaurants')
                self.end_headers()
            return
        # Delete one restaurant
        if self.path.endswith("/delete"):
            # Get the restaurant from the table
            myRestaurantQuery = session.query(Restaurant).get(int(self.path.split("/")[-2]))
            if myRestaurantQuery:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s?</h1>" % myRestaurantQuery.name
                output += "<form method='POST' enctype='multipart/form-data' "
                output += "action='/restaurants/" + str(myRestaurantQuery.id) +  "/delete'>"
                output += "<input type='submit' value='Delete'> </form>"
                output += "</body></html>"
                self.wfile.write(bytes(output, " utf-8"))
            else:
                print("Restaurant doesn't exist")
                # Redirect to restaurants
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
            return
        # Show overview page
        if self.path.endswith("/restaurants"):
            restaurants = session.query(Restaurant).all()
            output = ""
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output += "<html><body>"
            output += "<a href ='/restaurants/new'>Create a new restaurant here</a></br>"
            for restaurant in restaurants:
                output += restaurant.name
                output += "</br><a href ='/restaurants/%s/edit' >Edit </a> " % restaurant.id
                output += "</br><a href ='/restaurants/%s/delete'>Delete </a> " % restaurant.id
                output += "</br></br>"
            output += "</body></html>"
            self.wfile.write(bytes(output, " utf-8"))
            return
        # Add a restaurant (input-page)
        if self.path.endswith("/restaurants/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>Enter the name of the new restaurant</h1>"
            output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
            output += "<input name='newRestaurantName' type='text' >"
            output += "<input type='submit' value='Submit'> </form>"
            output += "</body></html>"
            self.wfile.write(bytes(output, " utf-8"))

    def do_POST(self):
        try:
            # Add a new restaurant to table
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers['content-type'])

                # boundary data needs to be encoded in a binary format
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    # Create new Restaurant Object
                    newRestaurant = Restaurant(name=messagecontent[0].decode())
                    session.add(newRestaurant)
                    session.commit()
                    # Redirect to restaurants
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            # Update the name of the restaurant
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers['content-type'])

                # boundary data needs to be encoded in a binary format
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    # Get the restaurant from the table
                    myRestaurantQuery = session.query(Restaurant).get(int(self.path.split("/")[-2]))
                    if myRestaurantQuery:
                        fields = cgi.parse_multipart(self.rfile, pdict)
                        messagecontent = fields.get('newRestaurantName')
                        myRestaurantQuery.name = messagecontent[0].decode()
                        session.add(myRestaurantQuery)
                        session.commit()
                    # Redirect to restaurants (both after succesfull update and after not found)
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            # Delete restaurant
            if self.path.endswith("/delete"):
                # Get the restaurant from the table
                myRestaurantQuery = session.query(Restaurant).get(int(self.path.split("/")[-2]))
                if myRestaurantQuery:
                    # Delete the restaurant
                    session.delete(myRestaurantQuery)
                    session.commit()
                else:
                    print("Restaurant doesn't exist, not possible to delete")
                # Redirect to restaurants (both after succesfull update and after not found)
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
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
