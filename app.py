from flask import Flask, jsonify, request
from models.models import User, Recipe
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave_secreta"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin123@127.0.0.1:3306/daily-diet"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
#view login
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user =  User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            return jsonify({"message": "Autenticação realizada com sucesso"})
    
    return jsonify({"message": "Credênciais inválidas"}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})

@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso"})

    return jsonify({"message": "Dados inválidos"}), 400

@app.route("/recipe", methods=["POST"])
@login_required
def create_recipe():
    data = request.json
    name = data.get("name", "")
    description = data.get("description", "")
    datetime = data.get("datetime", "")
    in_diet = data.get("in_diet", False)    
    if name and description and datetime:
        recipe = Recipe(name=name, description=description, datetime=datetime, in_diet=in_diet, user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()
        return jsonify({"message": "Receita cadastrado com sucesso"})
    
    return jsonify({"message": "Dados inválidos"}), 400

@app.route("/recipe/<int:id_recipe>", methods=["PUT"])
@login_required
def update_recipe(id_recipe):
    data = request.json
    recipe = Recipe.query.get(id_recipe)

    if not recipe:
        return jsonify({"message": "Receita não encontrado"}), 404

    if recipe.user_id != current_user.id:
        return jsonify({"message": "Operação não permitida"}), 403
    
    if data.get("name") and data.get("description") and data.get("datetime"):
        recipe.name = data.get("name")
        recipe.description = data.get("description")
        recipe.datetime = data.get("datetime")
        recipe.in_diet = data.get("in_diet", False)
        db.session.commit()
        return jsonify({"message": f"Receita {id_recipe} atualizado com sucesso"})
    
    return jsonify({"message": "Dados inválidos"}), 400

@app.route("/recipe/<int:id_recipe>", methods=["DELETE"])
@login_required
def delete_recipe(id_recipe):
    recipe = Recipe.query.get(id_recipe)
    if recipe:
        if recipe.user_id != current_user.id:
            return jsonify({"message": "Operação não permitida"}), 403
    
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "Receita deletado com sucesso"})
    
    return jsonify({"message": "Receita não encontrado"}), 404

@app.route("/recipes", methods=["GET"])
@login_required
def get_recipes():
    recipes = Recipe.query.filter_by(user_id = current_user.id).all()  

    return jsonify({"recipes": [s.toDict() for s in recipes]})

@app.route("/recipe/<int:id_recipe>", methods=["GET"])
@login_required
def get_recipe(id_recipe):
    recipe = Recipe.query.get(id_recipe)
    if recipe:
        if recipe.user_id != current_user.id:
            return jsonify({"message": "Operação não permitida"}), 403
        
        return jsonify({"recipe": recipe.toDict()})

    return jsonify({"message": "Receita não encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)


