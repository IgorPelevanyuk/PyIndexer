import time
from django.http import HttpResponse
from django.template import RequestContext, loader

from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def test(request):
    output = 'This is just a test'
    template = loader.get_template('./index.html')
    c = {}
    c.update(csrf(request))
    if request.session.get('ctime'):
        print 'Curtime true:', request.session["ctime"]
        #print 'Data', request.session.decode()
    request.session["ctime"] = str(time.time())
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def loginview(request):
    print 'basic index'
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)

def auth_and_login(request, onsuccess='/', onfail='/login/'):
    user = authenticate(username=request.POST['email'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        return redirect(onsuccess)
    else:
        return redirect(onfail) 

def sign_up_in(request):
    post = request.POST
    if not user_exists(post['email']): 
        user = create_user(username=post['email'], email=post['email'], password=post['password'])
        return auth_and_login(request)
    else:
        return redirect("/login/")

def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user
 
def user_exists(username):
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True

#@login_required(login_url='/login/')
def logout(request):
    print 'logout'
    logout(request)
    return redirect("/login/")
    


@login_required(login_url='/login/')
def secured(request):
    print 'Secured shown'
    return render_to_response("secure.html")
