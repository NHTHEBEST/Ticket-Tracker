from flask import(
    Blueprint,  g, redirect, request
)

from flaskr.db import get_db
import datetime, json, secrets

from .helpers import dict_from_row, json_addons

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('api', __name__, url_prefix='/api')

# perm levels
# 0 full acsess
# 1 all but user
# 2 read only
# 0-2 can change own password
# 3 own files only (for customers)
def check_key(key, perm_level):    
    # initialize database connection
    db = get_db() 
    
    # check if key exists
    user = db.execute(
        'SELECT * FROM users WHERE authkey = ? ', (key,)
    ).fetchone()
    
    if user is None:
        return 1#False
    
    # Check if permissions
    if user["perm"] > perm_level:
        return 2#False
    
    # Check if key expired
    if user["key_exp"] >= datetime.datetime.now():
        return 3#False

    # update key
    try: 
        db.execute(
            "UPDATE users SET key_exp = ? WHERE id = ?", 
            (datetime.datetime.now()+datetime.timedelta(hours=50), user['id'])
        )
        db.commit() 
    except db.IntegrityError:
        return False
    #close db
    db.close()
    #Auth user
    return True

def AUTH(perm):
    if 'AUTH' in request.headers:
        return check_key(request.headers['AUTH'], perm)
    return False

@bp.route('/test')
def test():
    return str(check_key(request.headers['AUTH'],0))

@bp.route('/create_order', methods=['POST'])
def create_order():
    if not AUTH(1):
        return "AUTH ERROR",403
    req = request.json
    
    if 'customer' not in req.keys():
        return "No Customer"
    if 'invoice' not in req.keys():
        return "No Invoice"
    if 'order' not in req.keys():
        return "No Order"
    if 'due' not in req.keys():
        return "No Due Date"
    
    inv_no = req['invoice']
    cust_no = req['customer']
    contents = json.dumps(req['order'])
    status = "New Order (Getting Matterials)"
    due = datetime.datetime.strptime(req['due'], "%d/%m/%y").date()#"2024-07-04 20:49:15.110090"
    
    db = get_db()
    
    # check if customer is real
    customer = db.execute(
        'SELECT * FROM customers WHERE id = ? ', (cust_no,)
    ).fetchone()
    if customer is None:
        return "No customer in DB"
    
    try:
        db.execute(
            "INSERT INTO orders (invoice_no, cutomer_id, contents, order_stat, due_date, expected_date) VALUES (?,?,?,?,?,?)",
            (inv_no, cust_no, contents, status, due, due)
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError"
    
    return "OK"
    


@bp.route('/create_customer')
def create_customer():
    # auth
    # usertype
    #order number
    if not AUTH(1):
        return "AUTH ERROR",403

@bp.route('/get_order')
def get_order():
    # auth
    # usertype
    #order number
    # only able to get own orders
    if not AUTH(3):
        return "AUTH ERROR",403

@bp.route('/get_customer')
def get_customer():
    if not AUTH(2):
        return "AUTH ERROR",403
    db = get_db()
    # auth
    # usertype
    #order number



@bp.route('/update_order_status', methods=['POST'])
def update_order_status():
    if not AUTH(1):
        return "AUTH ERROR",403

@bp.route('/todo', methods=['GET'])
def todo():
    if not AUTH(2):
        return "AUTH ERROR",403
    db = get_db()
    #data = db.execute("SELECT * FROM users").fetchall()
    #data = db.execute("SELECT * FROM orders").fetchall()
    data = db.execute("SELECT * FROM orders WHERE done = 0").fetchall()
    ret = []
    for x in data:
        ret.append(dict_from_row(x))
    return json.dumps(ret, default=json_addons)
    

@bp.route('/auth', methods=['POST'])
def AUTH():
    req = request.json
    
    if 'user' not in req.keys():
        return "No User"
    if 'pass' not in req.keys():
        return "No Pass"
    
    user = req['user']
    passw = req['pass']
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (user,)
    ).fetchone()
    
    if user is None:
        return "No User"
    elif not check_password_hash(user['password'], passw):
        return "Wrong Pass"
    
    key = secrets.token_hex(42)
    db = get_db()
    try: 
        db.execute(
            "UPDATE users SET authkey = ?, key_exp = ? WHERE id = ?", 
            (key, datetime.datetime.now()-datetime.timedelta(hours=50), user['id'])
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError"
    
    return key
    
    
@bp.route("/new_user", methods=['POST'])
def new_user():
    if not AUTH(0):
        return "AUTH ERROR",403
    req = request.json
    if 'user' not in req.keys():
        return "No User"
    if 'pass' not in req.keys():
        return "No Pass"
    if 'perm' not in req.keys():
        return "No Perm"
    db = get_db()
    
    try: 
        db.execute(
            "INSERT INTO users (username, password, perm) VALUES (?, ?, ?)", 
            (req['user'], generate_password_hash(req['pass']), req['perm'])
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError"
    
    return "OK"

@bp.route('/change_user', methods=['POST'])
def cheange_user():
    if not AUTH(1):
        return "AUTH ERROR",403
    req = request.json
    if 'user' not in req.keys():
        return "No User"
    if 'pass' not in req.keys():
        return "No Pass"
    if 'perm' not in req.keys():
        return "No Perm"
    # only allow to change current user
    return "inop" , 500



# perm levels
# 0 full acsess
# 1 all but user
# 2 read only
# 0-2 can change own password
# 3 own files only (for customers)