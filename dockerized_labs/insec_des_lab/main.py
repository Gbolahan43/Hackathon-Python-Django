from flask import Flask, render_template, request
import pickle
import base64
from dataclasses import dataclass

app = Flask(__name__)


@dataclass
class User:
    username: str
    is_admin: bool = False

    def __reduce__(self):
        """
        Intentionally insecure method for object deserialization.
        Used for educational demonstration of insecure pickle usage.
        """
        return (User, (self.username, self.is_admin))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/serialize', methods=['POST'])
def serialize_data():
    username = request.form.get('username', 'guest')
    user = User(username=username, is_admin=False)
    
    try:
        serialized = base64.b64encode(pickle.dumps(user)).decode()
        return render_template('result.html', serialized=serialized)
    except Exception as e:
        return render_template('result.html', message=f"Serialization Error: {str(e)}")


@app.route('/deserialize', methods=['POST'])
def deserialize_data():
    serialized_data = request.form.get('serialized_data', '')
    
    try:
        decoded_data = base64.b64decode(serialized_data)
        user = pickle.loads(decoded_data)  #  Vulnerable to RCE!

        if isinstance(user, User):
            if user.is_admin:
                message = f"Welcome Admin {user.username}! Here's the secret admin content: ADMIN_KEY_123"
            else:
                message = f"Welcome {user.username}. Only admins can see the secret content."
        else:
            message = "Invalid user data."

    except Exception as e:
        message = f"Deserialization Error: {str(e)}"

    return render_template('result.html', message=message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
