from Models import Loyalty, User, Order_item
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_admin.contrib.sqla import ModelView
from wtforms import ValidationError
from flask_admin.form import FileUploadField, rules
from Controllers import get_user_by_id, get_order_by_id
from app import db
import re
from flask_admin import expose
from flask import request, flash
from wtforms import BooleanField, StringField, PasswordField
from datetime import datetime


def password_validator(form, password, new=True):
    
    if new:
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must contain at least one special character.")
    # else:
    #     if password:
    #         password_validator(form, password, False)

class UserView(ModelView):
    
    form_extra_fields = {'new_password': StringField('Naujas slaptazodis')
    }

    form_columns = (
        'first_name', 
        'last_name', 
        'email',
        'password',
        'verified_at',
        'is_admin',
        'is_deleted',
        'loyalty',
        'token',
        'new_password'
        )

    column_list = (
        'first_name', 
        'last_name', 
        'email', 
        'is_admin', 
        'verified_at', 
        'is_deleted', 
        'blocked_until', 
        'loyalty', 
        'orders'
        )

    form_widget_args = {
        'token': {'readonly': True}
    }

    column_filters = ['is_deleted']

    column_formatters = {
        'loyalty': lambda view, context, model, name: model.loyalty.name if model.loyalty else '-',
        'orders': lambda view, context, model, name: len(model.orders),
        'verified_at': lambda view, context, model, name: 'Yes' if model.verified_at else 'No',
        'blocked_until': lambda view, context, model, name: f'Yes({model.blocked_until})' if model.blocked_until else 'No',
    }


    def delete_model(self, model):

        result = True
        if model.orders:  # Check if there are any children
            flash(f"Cannot delete {model.email} because it has orders.", "error")
            result = False
        if model.cart_products:
            flash(f"Cannot delete {model.email} because it has items in cart.", "error")
            result = False
        if model.wallet_transactions:
            flash(f"Cannot delete {model.email} because it has wallet transactions.", "error")
            result = False
        if result:
            return super().delete_model(model)
        else:
            self.session.rollback()
            return result


    form_overrides = {
        'loyalty': QuerySelectField
    }
    form_args = {
        'loyalty': {
            'query_factory': lambda: Loyalty.query.all(),
            'allow_blank': False,
            'get_label': 'name'
        }
    }

    

    def edit_form(self, obj=None):
        form = super().edit_form(obj)         
        del form.password
        return form
    
    def create_form(self, obj=None):
        form = super().edit_form(obj)         
        del form.new_password
        return form


    form_labels = {
        'first_name' : 'First name', 
        'last_name' : 'Last name', 
        'email' : 'Email',
        'password' : 'password',
        'is_admin' : 'Admin',
        'verified_at' : 'Verified',
        'is_deleted' : 'Deleted',
        'loyalty' : 'Loyalty status',
        'token' : 'Token'
    }

    column_labels = {
        'first_name':'First Name', 
        'last_name' : 'Last Name', 
        'email' : 'Email', 
        'is_admin' : 'Admin', 
        'verified_at' : 'Verified', 
        'is_deleted' : 'Disabled', 
        'blocked_until' : 'Blocked login', 
        'loyalty' : 'Loyalty status', 
        'orders' : 'Num of orders'
    }
    
    def on_model_change(self, form, model, is_created):
        # Only set the password if a new one is entered
        if is_created:
            password_validator(form, form.password.data)
            model.set_password(form.password.data)
        else:
            if form.new_password.data:
                password_validator(form, form.new_password.data)
                model.set_password(form.new_password.data)

    

class LoyaltyView(ModelView):
    form_columns = ('name', 'discount')
    column_list = ('name', 'discount')

    @staticmethod
    def validate_discount(form, field):
        if field.data <= 0:
            raise ValidationError("Discount must be greater than 0")
        
    form_args = {
        'discount': {
            'validators': [validate_discount]
        }
    }
    def delete_model(self, model):
        if model.users:  # Check if there are any children
            flash("Cannot delete Loyalty because it has assigned users.", "error")
            return False
        return super().delete_model(model)

    # def create_model(self, *args, **kwargs):
    #     print(args,kwargs)
    #     # return super().create_model(form)
    # def index_view(self,*args, **kwargs):
    #     print(args,kwargs)
    #     return super().index_view()

class WalletView(ModelView):
    
    column_filters = ['user']

    form_columns = (
        'user', 
        'amount', 
        ) 

    column_formatters = {
        'user': lambda view, context, model, name: f"{model.user.first_name} {model.user.last_name} ({model.user.email})",
    }
    
    form_overrides = {
        'user': QuerySelectField,
    }

    form_args = {
        'user': {
            'query_factory': lambda: User.query.all(),
            'allow_blank': False,
            'get_label': lambda u: f"{u.first_name} {u.last_name} ({u.email})"
        }
    }

    form_labels = {
        'user' : 'User', 
        'amount' : 'Amount', 
    }


class ProductView(ModelView):
    
    form_columns = (
        'title', 
        'description', 
        'price',
        'image',
        'stock',
        'is_active'
        )  

    form_overrides = {
        'image': FileUploadField
    }

    @staticmethod
    def validate_stock(form, field):
        if field.data < 1:
            raise ValidationError("Stock must be 1 or greater")
    
    @staticmethod
    def validate_price(form, field):
        if field.data <= 0:
            raise ValidationError("Price must be greater than 0")
        
    form_args = {
        'stock': {
            'validators': [validate_stock]
        },
        'price': {
            'validators': [validate_price]
        },
        'image': {
            'base_path': 'static/uploads/',
            'allow_overwrite': False  
        }
    }

    form_labels = {
        'title':'Title', 
        'description':'Description', 
        'price':'Price',
        'image':'Image',
        'stock':'Stock',
        'is_active':'Enabled'
    }


class OrderModelView(ModelView):

    column_filters = ['user']

    edit_template = "admin/order.html"

    column_formatters = {
        'items': lambda view, context, model, name: len(model.order_items),
        'user': lambda view, context, model, name: model.user.email
    }
    
    column_list = ('id','user', 'total_amount', 'items')
    form_columns = (
        'user',
        'total_amount'
        ) 

    form_overrides = {
        'user': QuerySelectField,
    }

    form_args = {
        'user': {
            'query_factory': lambda: User.query.all(),
            'allow_blank': False,
            'get_label': lambda u: f"{u.first_name} {u.last_name} ({u.email})"
        }
    }

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
         order_id = request.args.get('id', type=int)
         self._template_args['order'] = get_order_by_id(db, order_id)
         return super(OrderModelView, self).edit_view()


class ReviewModel(ModelView):

    form_create_rules = ('order_item', 'content', 'rating') 
    form_edit_rules = ('content', 'rating') 
    column_list = ('order_id','order_item', 'content', 'rating', 'created_at') 

    form_overrides = {
        'order_item': QuerySelectField,
    }

    column_formatters = {
        'order_item': lambda view, context, model, name: model.order_item.product_name,
        'order_id': lambda view, context, model, name: model.order_item.order_id
    }


    form_args = {
        'order_item': {
            'query_factory': lambda: Order_item.query.all(),
            'allow_blank': False,
            'get_label': lambda u: f"({u.id}) {u.product_name}"
        },
        'rating': {
            'label': 'Rating',
            'render_kw': {'type': 'number', 'min': 1, 'max': 5},
        }
    }

    form_labels = {
        'order_item' : 'Product', 
        'content' : 'Comment', 
        'rating' : 'Rating (1-5)'
    }
    column_labels = {
        'id': 'ID',
        'order_item' : 'Product', 
        'content' : 'Comment', 
        'rating' : 'Rating',
        'created_at' : 'Date'
    }