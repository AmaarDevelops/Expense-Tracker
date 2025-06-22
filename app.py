from flask import Flask,render_template,redirect,request,session,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = "Actually_secret"

users = {}

@app.route("/")
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("Username already exists",'danger')
        else:
            users[username] = generate_password_hash(password)
            flash('Registered Successfully. Please Log in','success')
            return redirect(url_for('login'))   
        
    return render_template('register.html')   

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user_hash = users.get(username)

        if user_hash and check_password_hash(user_hash,password):
            session['user'] = username
            flash('Login Successful!','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials!','danger') 
    return render_template('login.html')        

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    expenses = session.get("expense",[])
    for e in expenses:
        if 'id' not in e:
            e['id'] = str(uuid.uuid4())
    session['expense'] = expenses    
    total = sum(expense["amount"] for expense in session.get("expense", []))    
    return render_template('dashboard.html',user = session['user'],expenses = expenses,total = total)


@app.route("/add",methods=["POST","GET"])
def add_expense():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        amount = request.form.get('amount')
        category = request.form.get('category')
        description = request.form.get('description')

        if not amount or not category:
            flash("Amount and category are required.","danger")
            return render_template('add_expense.html')
        
        if 'expense' not in session:
            session['expense'] = []

        session['expense'].append({
            "id" : str(uuid.uuid4()),
            "amount":float(amount),
            "category":category,
            "description":description
        })    
        flash("Expense added successfully",'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_expense.html')

@app.route("/delete/<expense_id>", methods=['POST'])
def delete_expense(expense_id):
    if 'user' not in session or 'expense' not in session:
        return redirect(url_for('login'))
    
    expenses = session.get('expense',[])
    update_expenses = [e for e in expenses if e.get('id') != expense_id]
    session['expense'] = update_expenses
    flash("Expense deleteed successfully",'info')
    print("deleting id :", expense_id)
    return redirect(url_for('dashboard'))

    


@app.route("/logout")
def logout():
    session.pop('user',None)
    flash('You have been logged out','info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

 