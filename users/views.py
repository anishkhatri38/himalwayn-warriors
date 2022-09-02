import contextlib
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from .models import Profile, InboxMessage
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, InboxMessageForm
from django.db.models import Q
from .utils import searchProfiles,paginateProfiles
from .models import Contact
from datetime import datetime
from .decorators import allowed_users, unauthenticated_user,admin_only
from django.contrib.auth.models import Group

# Create your views here.
@unauthenticated_user
# @allowed_users(allowed_roles=['trainer'])
# @admin_only
def loginUser(request):
    page = 'login'

    if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
        
            try: 
              user = User.objects.get(username=username)

            except:
                
               messages.error(request, 'User does not exist')
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(request.GET['next'] if 'next' in request.GET else 'projects')
            else:
                messages.error(request, 'username or password is incorrect!! ')
    return render(request, 'users/login_register.html')



def logoutUser(request):
    logout(request)
    messages.info(request, 'User sucessfully loged out  ')
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            group = Group.objects.get(name='Trainer')
            user.groups.add(group)

            messages.success(request, 'User account is created! thank you ')

            login(request,user)
            return redirect('edit-account')

        else:
            messages.success(request,'An error has occured during registration.')




    context = {'page': page, 'form':form }
    return render (request, 'users/login_register.html', context )



# @login_required(login_url='login')

def profiles(request):
    profiles, search_query = searchProfiles(request)

    custom_range, profiles = paginateProfiles(request, profiles,3)
    
    context = {'profiles': profiles , 'search_query':search_query,'custom_range':custom_range}
    return render( request, 'users/profiles.html', context )

# @login_required(login_url='login')


def userProfile(request,pk):
    profile = Profile.objects.get(id = pk)
    topSkills = profile.skill_set.exclude(description__exact = "")
    otherSkills = profile.skill_set.filter(description = "")
    context = {'profile': profile, 'topSkills':topSkills, 'otherSkills':otherSkills}
    return render (request, 'users/user-profile.html', context )

@login_required(login_url = 'login')
def userAccount(request):
    profile = request.user.profile

    skills = profile.skill_set.all()
    projects = profile.project_set.all()


    context = {'profile':profile, 'skills':skills, 'projects':projects}
    return render(request, 'account.html', context)

@login_required(login_url = 'login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance = profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context = {'form':form}
    return render (request, 'users/profile_form.html', context)

@login_required(login_url = 'login')
def createSkill(request):
    profile = request.user.profile 
    form = SkillForm()

    if request.method =='POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit = False)
            skill.owner = profile
            skill.save()
            messages.success(request,'New skill added sucessfully')
            return redirect('account')
    context = {'form':form}
    return render(request, 'users/skill_form.html', context )


@login_required(login_url = 'login')
def updateSkill(request, pk):
    profile = request.user.profile 
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)

    if request.method =='POST':
        form = SkillForm(request.POST, instance= skill)
        if form.is_valid():
            skill.save()
            messages.success(request,'New skill updated sucessfully')
            return redirect('account')
    context = {'form':form}
    return render(request, 'users/skill_form.html', context )


def deleteSkill(request,pk):
    profile = request.user.profile
    skill = profile.skill_set.get (id = pk)
    if request.method == 'POST':
        skill.delete()
        return redirect('account')
        
    context = {'object': skill }
    return render(request, 'delete_template.html', context)

@login_required(login_url='login')
def contact(request):
    if request.method == "POST" :
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc= request.POST.get('desc')
        contact = Contact (name=name, email=email, phone=phone, desc=desc, date=datetime.today())
        contact.save()
        messages.success(request, 'Your message has been sent!.')
        return redirect('contact')
    return render (request,'contact.html' )

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['Admin', 'Trainer'])
def inbox(request):
    profile = request.user.profile
    messageRequest = profile.messages.all()
    unreadCount = messageRequest.filter(is_read  = False).count()
    context = {'messageRequest': messageRequest, 'unreadCount':unreadCount}
    return render(request, 'users/inbox.html',context )

@login_required(login_url = 'login')
def viewMessage(request,pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message':message}
    return render(request, 'users/message.html', context)


def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = InboxMessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = InboxMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            messages.success(request,'Your message was sucessfully sent')
            return redirect('user-profile',pk=recipient.id)


    context = {'recipient':recipient, 'form':form}
    return render(request, 'users/message_form.html',context)