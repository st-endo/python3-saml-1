from flask import Flask, render_template, redirect, url_for, request, session
from urllib.parse import urlparse
from onelogin.saml2.auth import OneLogin_Saml2_Auth
# from onelogin.saml2.utils import OneLogin_Saml2_Utils


app = Flask(__name__)
app.secret_key = 'secret'


def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=".")
    return auth


def prepare_flask_request():
    # FlaskのrequestオブジェクトをSAML auth requestに合わせて整形
    url_data = urlparse(request.url)
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    req = prepare_flask_request()
    auth = init_saml_auth(req)
    return redirect(auth.login())


@app.route('/acs', methods=['POST'])
def acs():
    req = prepare_flask_request()
    auth = init_saml_auth(req)
    auth.process_response()
    errors = auth.get_errors()

    # print(req, auth)

    if not errors:
        session['samlUserdata'] = auth.get_attributes()
        session['samlNameId'] = auth.get_nameid()
        session['samlSessionIndex'] = auth.get_session_index()
        print(session)
        return redirect(url_for('user'))
    else:
        return 'エラーが発生しました: ' + ', '.join(errors)


@app.route('/user')
def user():
    if 'samlUserdata' in session:
        return 'ユーザーデータ: ' + str(session['samlUserdata'])
    else:
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    return 'Logout page'


if __name__ == '__main__':
    app.run(debug=True)
