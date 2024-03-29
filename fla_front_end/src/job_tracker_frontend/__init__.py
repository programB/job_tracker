# The MIT License
#
# Copyright (c) 2024 programb
# Copyright (c) 2018 Todd Birchard
#
# Permission is hereby granted, free of charge,
# to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to
# deal in the Software without restriction, including
# without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom
# the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from dotenv import load_dotenv
from flask import Flask

answer = load_dotenv()
print(f"loaded env?: {answer}")


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()

    with app.app_context():

        # Register Flask app pages
        from job_tracker_frontend.pages import bp as pages_bp

        app.register_blueprint(pages_bp)

        # Initialize Dash sub app together with whatever it provides
        from job_tracker_frontend.pages import init_dash_app

        app = init_dash_app(app)

        return app
