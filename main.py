from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import stripe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

stripe.api_key = "sk_test_51LYVtLAWFjVS1bLLLewgZ9tR8hGQPIUvymfthzat2wYqk0017yJeZySA11lrjwClG3K7FCQCBLtEI3pxyxkhfMst00qplzQMnm "

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=True, nullable=False)
    basket = db.relationship('Basket', backref='user', lazy=True)


class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ProductCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_file_name = db.Column(db.String(300), nullable=False)


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    line_items = []
    cart_products = []
    total = 0
    names = ProductCatalog.query.all()
    for name in names:
        product = request.cookies.get(name.name)
        if product is not None:
            cart_products.append([ProductCatalog.query.filter_by(name=name.name).first(), product])
            total += int(product) * ProductCatalog.query.filter_by(name=name.name).first().price
            line_items.append({
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': name.name,
                    },
                    'unit_amount': name.price,
                },
                'quantity': product, })

    session = stripe.checkout.Session.create(
        line_items=line_items,
        mode='payment',
        success_url=request.host_url + 'thankyou',
        cancel_url=request.host_url + 'checkout',
    )
    return redirect(session.url, code=303)


@app.route('/delete_product/<int:pid>')
def delete_product(pid):
    resp = make_response(redirect(url_for('cart')))
    product = ProductCatalog.query.filter_by(id=pid).first()
    resp.set_cookie(product.name, value='1', domain='127.0.0.1', expires=0)
    return resp


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/cart')
def cart():
    names = ProductCatalog.query.all()
    products = []
    total = 0
    for name in names:
        product = request.cookies.get(name.name)
        if product is not None:
            products.append(ProductCatalog.query.filter_by(name=name.name).first())
            total += int(product) * ProductCatalog.query.filter_by(name=name.name).first().price
    total = total / 100
    return render_template('cart.html', products=products, total=total)


@app.route('/update_cookie', methods=['POST', 'GET'])
def update_cookie():
    products = {}
    if request.method == 'POST':
        for field in request.form:
            products[field] = request.form[field]
    resp = make_response(redirect('checkout'))
    for product in products:
        resp.set_cookie(product, value=products[product], domain='127.0.0.1')
    return resp


@app.route('/checkout')
def checkout():
    cart_products = []
    total = 0
    names = ProductCatalog.query.all()
    for name in names:
        product = request.cookies.get(name.name)
        if product is not None:
            cart_products.append([ProductCatalog.query.filter_by(name=name.name).first(), product])
            total += int(product) * ProductCatalog.query.filter_by(name=name.name).first().price
    return render_template('checkout.html', cart_products=cart_products, total=total)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/shop')
def shop():
    product_list = ProductCatalog.query.all()
    return render_template('shop.html', products=product_list)


@app.route('/thankyou')
def thankyou():
    resp = make_response(render_template('thankyou.html'))
    names = ProductCatalog.query.all()
    for name in names:
        resp.set_cookie(name.name, value='1', domain='127.0.0.1', expires=0)
    return resp


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/getcookie')
def getcookie():
    names = ProductCatalog.query.all()
    products = []
    for name in names:
        product = request.cookies.get(name.name)
        if product is not None:
            products.append(ProductCatalog.query.filter_by(id=product).first())
    return 'hello'


@app.route('/update_cart', methods=['POST', 'GET'])
def update_cart():
    resp = make_response(redirect(url_for('cart')))
    products = {}
    for field in request.form:
        products[field] = request.form[field]
    return resp


@app.route('/cookies/<int:pid>')
def cookies(pid):
    resp = make_response(redirect(url_for('shop')))
    name = ProductCatalog.query.filter_by(id=str(pid)).first()
    resp.set_cookie(name.name, value='1', domain='127.0.0.1')
    return resp


if __name__ == '__main__':
    app.run(debug=True)
