from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField # query represents query expression with kw and v. F-field - compare two fields
from django.db.models.aggregates import Count, Max, Min, Avg, Sum # For practicing aggregation
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from store.models import Product, OrderItem, Customer, Order, Collection
from tags.models import TaggedItem
from django.core.mail import EmailMessage, BadHeaderError # send_mail, mail_admins
from templated_mail.mail import BaseEmailMessage
from .tasks import notify_customers

# @transaction.atomic()
# def say_hello456(request):
#   query_set = Product.objects.all()
#   try:
#     product = Product.objects.get(pk=1)
#   except ObjectDoesNotExist:
#     pass
#   exists = Product.objects.filter(pk=0).exists()
#   queryset = Product.objects.filter(unit_price__gt=20) # gt, gte, lt, lte, in, (i)exact
#   queryset1 = Product.objects.filter(unit_price__range=(20, 30))
#   queryset2 = Product.objects.filter(collection__id__range=(1, 2, 3)) # isnull, (i)regex
#   queryset3 = Product.objects.filter(title__icontains='coffee') # (i)contains, (i)startswith, (i)endswith, date, year

#   # using AND, OR - Q, F classes
#   queryset4 = Product.objects.filter(inventory__lt=10, unit_price__lt=20) # gives AND in SQL statement
#   queryset4 = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20) # another way of writing the same statement
#   queryset4 = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20)) # gives OR in SQL. Can interpret logical (&, |, ~(not)) operators
#   queryset5 = Product.objects.filter(inventory=F('unit_price')) # or collection__id... compares two fields

#   # sorting data
#   queryset6 = Product.objects.order_by('unit_price', 'title') # for DESC '-title' or call .reverse() method
#   # can use list methods to get the first element [0] or slice [:5] etc.
#   queryset7 = Product.objects.earliest('unit_price') # or use .latest('unit_price') for getting the last [-1] element.

#   # limiting results
#   quryset8 = Product.objects.all()[:5] # shows first 5 records (SQL - LIMIT) or [5:10] (LIMIT=5 SKIP=5)

#   # selecting fields
#   queryset9 = Product.objects.values('id', 'title', 'collection__title') # selects only chosen fields in db. returns dict
#   queryset9 = Product.objects.values_list('id', 'title', 'collection__title') # returns a list, i.e. tupple

#   # task - select products that have been ordered and sort them by title
#   queryset_task = Product.objects.filter(id__in=OrderItem.objects.values('product__id').distinct()).order_by('title') # distinct excludes duplicates

#   # defering fields
#   queryset10 = Product.objects.only('id', 'title') # can take up resources when joining queries.
#   queryset10 = Product.objects.defer('description') # excludes fields from queries

#   # selecting related fields
#   # select related when object has one instance | prefetch_related when there are (n) objects
#   queryset11 = Product.objects.select_related('collection').all() # preloads related fields with instant display
#   # SQL - SELECT all fields from product and collection table, and applying INNER JOIN store_collection ON (store_product.collection_id = store_collection_id)
#   # using prefetch_related
#   queryset11 = Product.objects.prefetch_related('promotions').all() # 2 SQL queries - reading products, reading promos and joining them
#   queryset11 = Product.objects.prefetch_related('promotions').select_related('collection').all()

#   # task 2 - get the last 5 orders with their customer and items (including product)
#   # rename related variables to orders in hello.html and add {{ order.id }} - {{ order.customer.first_name }}
#   # add related_name='items' in OrderItem model in store.models in order field or django will set 'orderitem_set' automatically
#   queryset_task2 = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]

#   # Aggregate method
#   result = Product.objects.aggregate(Count('id'), min_price=Min('unit_price'))

#   # Annotate
#   queryset12 = Customer.objects.annotate(is_new=Value(True))
#   queryset12 = Customer.objects.annotate(new_id=F('id') + 1) # use one field to annotate a new one and perform operations here.

#   # Database functions using Func
#   queryset13 = Customer.objects.annotate(full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT'))
#   # Using shorter version - Concat class Django
#   queryset13 = Customer.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))

#   # grouping data
#   queryset14 = Customer.objects.annotate(
#     orders_count=Count('order')
#   )
#   # ExpressionWrapper
#   discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
#   queryset15 = Product.objects.annotate(discounted_price=discounted_price)

#   # Querying Generic relationships
#   content_type = ContentType.objects.get_for_model(Product)

#   queryset16 = TaggedItem.objects.select_related('tag').filter(
#     content_type=content_type,
#     object_id=1
#   ) # set 'tags': list(queryset16) to render method
#   # Or simply use this line with the change in the tags model
#   queryset16 = TaggedItem.objects.get_tags_for(Product, 1)

#   # Creating Objects
#   collection = Collection( )
#   collection.title = 'Video Games'
#   collection.featured_product = Product(pk=1)
#   collection.save()
#   # the same but with less code
#   Collection.objects.create(titlel='a', featured_product_id=1)

#   # Updating objects - have to read data first before updating it
#   collection = Collection.objects.get(pk=11)
#   collection.featured_product = Product(pk=1)
#   collection.save()
#   # Shorthand
#   Collection.objects.filter(pk=11).update(featured_product=None) # it will update all data

#   # Deleting objedts
#   collection = Collection(pk=11)
#   collection.delete()
#   # Shorthand
#   Collection.objects.filter(id__gt=5).delete()

#   # Transactions
#   with transaction.atomic():
#     order = Order()
#     order.custormer_id = 1
#     order.save()

#     item = OrderItem()
#     item.order = order
#     item.product_id = 1
#     item.quantity = 1
#     item.unit_price = 10
#     item.save()

#     # Executing raw SQL queries
#     queryset17 = Product.objects.raw('SELECT id, title FROM store_product')
#     # or with connection module
#     cursor = connection.cursor()
#     cursor.execute('')
#     cursor.close()
#     # using with block
#     with connection.cursor() as cursor:
#       cursor.callproc('get_customers', [1, 2, 'a'])



def say_hello(request):
  # try:
  #   # send_mail('subject', 'message', 'info@moshbuy.com', ['mail@mail.me'])
  #   # mail_admins('subject', 'message', html_message='message')
  #   ## message = EmailMessage('subject', 'message', 'from@bojan.me', ['mail@mail.me'])
  #   ## message.attach_file('playground/static/images/dog.jpg')
  #   ## message.send()
  #   message = BaseEmailMessage(template_name='emails/hello.html', context={'name': 'Bojan'})
  #   message.send(['info@bojan.me'])
  # except BadHeaderError:
  #   pass
  # return render(request, 'hello.html', {'name': 'Bojan'})
  notify_customers.delay('Hello')
  return render(request, 'hello.html', {'name': 'Bojan'})
