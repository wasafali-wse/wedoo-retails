# Accounts App

This directory contains the code for the Accounts application, which manages user accounts and authentication.

## understand the module 

The Accounts module is responsible for handling user accounts and authentication. It provides the following features:

- User registration
- User login
- User profile management
- User password reset
- User account deactivation
- it manages the entire accounting of the pos-erp system 

## structure
```plain text
accounts/
|-admin.py
|-models.py
|-views.py
```
the admin.py file is resposible to visual .client side request and send response to the client side .the we can perform the CRUD to the model if we add them to admin file

the models.py file is resposible to define the data models for the accounts app .
we define models in this file . the models are used to store the data for the accounts app .

the views.py file is resposible to define the views for the accounts app .
we can define the views in this file . the views are used to handle the requests from the client side .

just these 3 files are importent for the accounts app .or any 

## Work flow

1. the user sends a request to the server .
2. the server receives the request and forwards it to the appropriate view .
3. the view processes the request and returns a response .
4. the server sends the response back to the user .
5. the user receives the response and can use the data in the response to perform further actions .

## How does this work behind the scenes ?

when user make any request .it is sent to the server .the server recieves the request and check it which url it is like (/any/url/to/any/view/).

then it check the url and forwards the request to the appropriate view like (/any/url/to/any/view/ this url will be handled by the view function ).

then the view function processes the request and returns a response .the response is then sent back to the user in html page .

but in our project we havily rely on django's admin panel .we dont create any view not and html page .we use django's admin panel to handle the requests .we just make models in model.py means we just create tables for the database. and we import these model in admin and just register themwith a decorator. that it we are ready to perform crud.

