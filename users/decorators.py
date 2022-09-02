from django.http import HttpResponse
from django.shortcuts import redirect 

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
       if request.user.is_authenticated:
           return redirect('projects')
       else:
           return view_func(request,*args, **kwargs)
        
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request,*args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request,*args, **kwargs)
            else:
                return HttpResponse("Your are not authorized to view this page")

            
            
        return wrapper_func
    return decorator



def admin_only(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request,*args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group == 'active':
                return redirect('Products/products_home.html')

            if group == 'trainer':
                return redirect('staff')

            if group == 'superuser':
                return redirect('projects')

  
            else:
                return HttpResponse("Your are not authorized to view this page")

            
            
        return wrapper_func