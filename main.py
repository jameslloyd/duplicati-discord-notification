import hyperdiv as hd
from Google_Oauth2 import login_url, auth_reponse
import requests
from dotenv import load_dotenv

load_dotenv()
router = hd.router()



class Backupjobs:
    """
    The backupjobs state. Note that we could inherit from hd.BaseState here
    and define a `backupjobs` prop, but instead we choose to use a private
    state variable created with hd.state.
    """

    def __init__(self):
        self.state = hd.state(
            backupjobs={
                "Meet Joe for lunch": False,
                "Fix bycicle": True,
                "Buy groceries": False,
            }
        )

    @property
    def backupjob_list(self):
        return self.state.backupjobs.items()

    def add_backupjob(self, backupjob):
        if backupjob not in self.state.backupjobs:
            # Note that the `|` operator is important because it
            # creates a new dictionary object.
            # `self.state.backupjobs[backupjob] = False` would not work.
            # Also note that the `|=` operator would not work, since
            # it mutates the left-hand side value in place.
            # We could also do:
            #    new_dict = dict(**self.state.backupjobs)
            #    new_dict[backupjob] = False
            #    self.state.backupjobs = new_dict
            self.state.backupjobs = {backupjob: False} | self.state.backupjobs

    def backupjob_is_done(self, backupjob):
        return self.state.backupjobs[backupjob]

    def toggle_backupjob(self, backupjob):
        self.state.backupjobs = self.state.backupjobs | {backupjob: not self.state.backupjobs[backupjob]}

@router.route("/")
def home():
    hd.markdown("# Welcome")

@router.route("/login")
def login():
    loc = hd.location()
    url = loc.protocol + "://" + loc.host + loc.path + "?" + loc.query_args
    auth = auth_reponse(url)
    if auth:
        print(auth)
        hd.local_storage.set_item("user_id", auth['id'])
        hd.local_storage.set_item("email", auth['email'])
        hd.local_storage.set_item("name", auth['name'])
        hd.local_storage.set_item("picture", auth['picture'])
        hd.local_storage.set_item("logged_in", "True")
        hd.markdown(auth)
        hd.avatar(image=auth['picture'])
   
@router.route("/logout")
def logout():
    hd.local_storage.remove_item("user_id")
    hd.local_storage.remove_item("email")
    hd.local_storage.remove_item("name")
    hd.local_storage.remove_item("picture")
    hd.local_storage.remove_item("logged_in")
    loc = hd.location()
    
    loc.go(path="/")
 
    
@router.route("/backups")
def backups():
    hd.markdown("# Backups")
    backupjobs = Backupjobs()

    # Outer container that centers the title and inner container.
    with hd.box(gap=2, padding=4, align="center"):
        # Title
        hd.markdown("# Simple Todo App")
        # Inner container with the core functionality in it
        with hd.box(gap=2, width=40):
            # Input form
            with hd.form() as form:
                form.text_input(placeholder="Enter a backupjob", name="backupjob")
            if form.submitted:
                backupjob = form.form_data["backupjob"]
                if backupjob:
                    backupjobs.add_backupjob(backupjob)
                form.reset()

            # Bullet-list of backupjobs
            with hd.table():
                for backupjob, done in backupjobs.backupjob_list:
                    with hd.scope(backupjob):
                        with hd.tr():
                            hd.td()
                            with hd.link(
                                href="", font_color="neutral-800"
                            ) as backupjob_link:
                                if backupjobs.backupjob_is_done(backupjob):
                                    hd.markdown(f"~~{backupjob}~~")
                                else:
                                    hd.markdown(backupjob)
                            if backupjob_link.clicked:
                                backupjobs.toggle_backupjob(backupjob)

def main():
    loginurl = login_url()
    template = hd.template(logo="/assets/duplicati.png", title="Duplicati Notifications")
    indexpage = hd.index_page(
        title="Duplicati Notifications"
    )
    # Sidebar menu linking to the app's pages:
    template.add_sidebar_menu(
        {
            "Home": {"icon": "house", "href": home.path},
            "Backups": {"icon": "layer-backward", "href": "/backups"},
        }
    )
    with template.sidebar:
        hd.text(
            '''
            Custom sidebar content,
            Rendered, below the menu.
            '''
        )
    # A topbar contact link:
    logged_in = hd.local_storage.has_item("user_id")
    
    print(logged_in)
    if hd.local_storage.has_item("user_id"):
        template.add_topbar_links(
            {
                "Logout": {"icon": "person-square", "href": "/logout"}
            }
        )
    else:    
        template.add_topbar_links(
            {
                "Login": {"icon": "person-square", "href": loginurl}
            }
        )


    # Render the active page in the body:
    with template.body:
        router.run()

hd.run(main)