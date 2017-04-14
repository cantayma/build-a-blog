import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render (self, template, **kw):
        self.write (self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class FrontPage(Handler):

    def get(self):
        self.redirect('/blog')

class BlogPage(Handler):

    def get(self):
        latest_five_posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")

        self.render("front.html",
                    postsT = latest_five_posts)

class NewPost(Handler):
    def render_front(self, subject="", content="", error=""):
        self.render("newpost.html",
                    subjectT = subject,
                    contentT = content,
                    errorT = error)

    def get(self):
        self.render_front() #draws blank form

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            b = Post(subject=subject, content=content)
            b.put()

            self.redirect('/blog/' + str(b.key().id()))

        else:
            error = "We need both a subject and some ruminations in the content box..."
            self.render_front(subject, content, error)

class ViewPostHandler(Handler):
    def get(self, id):
        self.render("confirmpost.html",
                    newestpostT = Post.get_by_id(int(id)))

app = webapp2.WSGIApplication([
        ('/', FrontPage),
        ('/blog', BlogPage),
        ('/newpost', NewPost),
        webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
        ], debug = True)
