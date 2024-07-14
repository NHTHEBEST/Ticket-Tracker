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
    database = 'users'
    # check if key exists
    user = db.execute(
        'SELECT * FROM ? WHERE authkey = ? ', (key,)
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


# add order price and amount paid
@bp.route('/create_order', methods=['POST'])
def create_order():
    if not AUTH(1):
        return "AUTH ERROR",403
    req = request.json
    
    if 'customer' not in req.keys():
        return "No Customer",400
    if 'invoice' not in req.keys():
        return "No Invoice",400
    if 'order' not in req.keys():
        return "No Order",400
    if 'due' not in req.keys():
        return "No Due Date",400
    if 'price' not in req.keys():
        return "No Price",400
    if 'paid' not in req.keys():
        return "No Paid",400
    
    
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
        return "No customer in DB",400
    
    try:
        db.execute(
            "INSERT INTO orders (invoice_no, cutomer_id, contents, order_stat, due_date, expected_date, price, paid) VALUES (?,?,?,?,?,?,?,?)",
            (inv_no, cust_no, contents, status, due, due, req['price'], req['paid'])
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError",500
    
    return "OK"
    


@bp.route('/create_customer', methods=['POST'])
def create_customer():
    if not AUTH(1):
        return "AUTH ERROR",403
    
    req = request.json
    if 'name' not in req.keys():
        return "No Name",400
    if 'email' not in req.keys():
        return "No Email",400
    if 'phone' not in req.keys():
        return "No Phone",400
    
    seckey = secrets.token_urlsafe(64)
    
    db = get_db()
    try:
        db.execute(
            "INSERT INTO customers (name, email, phone, authkey) VALUES (?,?,?,?)",
            (req['name'], req['email'], req['phone'], seckey)
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError",500
    return 'OK'
    return "inop" , 501

@bp.route('/get_order')
def get_order():
    # auth
    # usertype
    #order number
    # only able to get own orders
    if not AUTH(3):
        return "AUTH ERROR",403
    return "inop" , 501

@bp.route('/get_customer') # INOP
def get_customer():
    if not AUTH(2):
        return "AUTH ERROR",403
    db = get_db()
    # auth
    # usertype
    #order number
    return "inop" , 501

# list all customers

"""
oderd should contain price and amount paid
"""

# get orders from all customers

@bp.route('/update_order', methods=['POST'])
def update_order():
    if not AUTH(1):
        return "AUTH ERROR",403
    req = request.json
    
    if 'invoice' not in req.keys():
        return "No Invoice",400
    if 'order' not in req.keys():
        return "No Order",400
    if 'expected' not in req.keys():
        return "No Due Date",400
    if 'price' not in req.keys():
        return "No Price",400
    if 'paid' not in req.keys():
        return "No Paid",400
    if 'status'  not in req.keys():
        return "No Status", 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO orders (invoice_no, contents, order_stat, expected_date, price, paid) VALUES (?,?,?,?,?,?)",
            (req['invoice'], req['order'], req['status'], req['expected'], req['price'], req['paid'])
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError",500
    return "OK"


#mark done call
@bp.route('/done', methods=['POST'])
def done():
    if not AUTH(1):
        return "AUTH ERROR", 403
    req = request.json
    if 'order' not in req.keys():
        return "No Invoice",400
    db = get_db()
    row = db.execute('SELECT * FROM orders WHERE id = ?', req['order']).fetchone()
    
    # check inv no
    
    # check paid
    if row['paid'] != row['price']:
        return 'Not Paid', 304
    
    try: 
        db.execute(
            "UPDATE order SET done = 1 WHERE id = ?", req['order']
        )
        db.commit() 
    except db.IntegrityError:
        return "DB Integrity Error", 500
    return 'OK'
    
    
    


@bp.route('/todo', methods=['GET'])
def todo(): # order by due date
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
def AUTH_site():
    req = request.json
    
    if 'user' not in req.keys():
        return "No User",400
    if 'pass' not in req.keys():
        return "No Pass",400
    
    user = req['user']
    passw = req['pass']
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (user,)
    ).fetchone()
    
    if user is None:
        return "No User",400
    elif not check_password_hash(user['password'], passw):
        return "Wrong Pass",403
    
    key = secrets.token_hex(42)
    db = get_db()
    try: 
        db.execute(
            "UPDATE users SET authkey = ?, key_exp = ? WHERE id = ?", 
            (key, datetime.datetime.now()-datetime.timedelta(hours=50), user['id'])
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError",500
    
    return key
    
    
@bp.route("/new_user", methods=['POST'])
def new_user():
    if not AUTH(0):
        return "AUTH ERROR",403
    req = request.json
    if 'user' not in req.keys():
        return "No User",400
    if 'pass' not in req.keys():
        return "No Pass",400
    if 'perm' not in req.keys():
        return "No Perm",400
    db = get_db()
    
    try: 
        db.execute(
            "INSERT INTO users (username, password, perm) VALUES (?, ?, ?)", 
            (req['user'], generate_password_hash(req['pass']), req['perm'])
        )
        db.commit()
    except db.IntegrityError:
        return "db IntegrityError",500
    
    return "OK"

@bp.route('/change_user', methods=['POST'])
def cheange_user():
    if not AUTH(1):
        return "AUTH ERROR",403
    req = request.json
    if 'user' not in req.keys():
        return "No User",400
    if 'pass' not in req.keys():
        return "No Pass",400
    if 'perm' not in req.keys():
        return "No Perm",400
    # only allow to change current user
    return "inop" , 501



# perm levels
# 0 full acsess
# 1 all but user
# 2 read only
# 0-2 can change own password
# 3 own files only (for customers)



"""
add customers
to each customer add order
to each order add notes.
orders have internal todo list
view all orders

everything search

go from order to cust visvers

inv no optional but required to complete (done to 1)


bybass everything?


XERO intergration
"""