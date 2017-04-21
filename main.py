
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape= True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def render_post(response, post):
    response.out.write('<b>' + post.title + '</b><br>')
    response.out.write(post.content)


##BLOG STUFF

def blog_key(name= 'default'):
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created= db.DateTimeProperty(auto_now_add= True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class BlogFront(BlogHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * from Post ORDER BY created DESC LIMIT 5")
        self.render("front.html", posts= posts)


class PostPage(BlogHandler):
    def get(self, post_id):
        key= db.Key.from_path('Post', int(post_id))
        post= db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post= post)

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            p = Post(title=title, content=content)
            p.put()
            self.redirect("/blog/%s" %str(p.key().id()))

        else:
            error = "You need to write a title and content"
            self.render("newpost.html", title = title, content= content, error= error)



app = webapp2.WSGIApplication([
    ('/blog/?', BlogFront),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)', PostPage)
], debug=True)
