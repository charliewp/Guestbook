from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import operator
from django import forms
from django.db import models
from datetime import datetime
from random import sample, randint
from django.db import IntegrityError, DataError


from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth import authenticate

#models
from guestbook.models import Prompt
from guestbook.models import PersonNote
from guestbook.models import Person
from guestbook.models import PersonSurvey
from guestbook.models import RoleResponse
from guestbook.models import AffiliateResponse
#from guestbook.models import Response
from guestbook.models import PersonSnapshot
from guestbook.models import Service
from guestbook.models import PersonServiceRequest
from guestbook.models import AppProperty
from guestbook.models import Preference
from guestbook.models import LanguageResponse


from guestbook.forms import SurveyForm
from guestbook.forms import SurveyForm
from guestbook.forms import QueueForm
from guestbook.forms import StaffForm
from guestbook.forms import PersonNoteForm

#forms
from guestbook.forms import SignInForm
from guestbook.forms import AliasForm
from guestbook.forms import ServicesForm
from guestbook.forms import LoginForm
from guestbook.forms import ReporterForm

#from guestbook.forms import VolunteerForm
from django.forms import CharField, ModelChoiceField, RadioSelect, BaseForm

<<<<<<< HEAD
#from twilio.rest import Client
=======
from twilio.rest import Client
>>>>>>> d218e7b096339ce2f6f010f1c3faaf5de7d8c8de
import re
from django.apps import apps

#charts
from django.views.generic import TemplateView

# Your Account SID from twilio.com/console
account_sid = "ACf4e03c7158dfd7b1abafc77d830c606a"
# Your Auth Token from twilio.com/console
auth_token  = "b26623c93d3a50ed38cad1cc8769e167"

SERVICE_STATUS_QUEUED          = 500
SERVICE_STATUS_COMPLETED       = 501
SERVICE_STATUS_NOTCOMPLETED    = 502

SNAPSHOT_STATUS_ACTIVE         = 800
SNAPSHOT_STATUS_STALE          = 801
SNAPSHOT_STATUS_CLOSED         = 802

_ENV = 'DEVT'

#TIMEWARP_FACTOR = 1440
    #TIMEWARP_FACTOR
    #     1 -   Real-Time
    #  1440     1minute   = 1day   a prompt with intervalDays=90 will be re-queued  after 90minutes
    #   720     2minutes  = 1day
    #   288     5minutes  = 1day
    #   144     10minutes = 1day

#SNAPSHOT_TTL_MINUTES = 2
    #if 0:
    #  snapshots stale at midnight.
    #otherwise:
    #..snapshots stale after SNAPSHOT_TTL_MINUTES

def reporter(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    try:
      del request.session['aliasname']
      del request.session['aliaspin']
    except:
      pass
    error = False
    now = datetime.today()
    if request.method == 'POST':
      print('reporter post')
      #person = request.POST['persons'] 
      #prompt = request.POST['prompts']
      form = ReporterForm(request.POST)
      if form.is_valid():
        person = form.cleaned_data['persons']
        prompt = form.cleaned_data['prompts']
        fkResponseModel = prompt.responseType
        responses = []
        snapshots = PersonSnapshot.objects.all().filter(person=person)
        for snapshot in snapshots:
          surveys = PersonSurvey.objects.all().filter(connection=snapshot).filter(prompt=prompt)
          for survey in surveys:
            timeperiods = snapshot.timestamp - now
            hours = timeperiods.days * 24 + timeperiods.seconds/3600
            #datatuple = (int(hours), survey.points)
            datatuple = (snapshot.timestamp.timestamp()*1000, survey.points)
            responses.append(datatuple)
        responses = sorted(responses, key=lambda x: x[0], reverse=False)
        #data = view.get_context_data()
        labels = []
        values = []
        for response in responses:
          print('response=%s %s' % (response[0], response[1]))
          labels.append(response[0])
          values.append(response[1])
        #let's show the possible responses
        promptResponses = apps.get_model(app_label='guestbook', model_name=fkResponseModel).objects.all().filter(language=prompt.language)
        chartKeys = []
        for promptResponse in promptResponses:
          datatuple = (promptResponse.points, promptResponse.name)
          chartKeys.append(datatuple)
        form = ReporterForm()
        return render(request, 'reporter.html', {'form': form, 'labels': labels, 'values': values, 'chartkeys': chartKeys})
    else:
      labels = []
      values = []
      form = ReporterForm()
      return render(request, 'reporter.html', {'form': form, 'labels': labels, 'values': values})

def checksession(request):
    if request.session.has_key('username'):
      print('session-cookie found!')
      return True
    else:
      print('session-cookie not found')
      return False

def login(request):
    error = False
    message = ''
    if request.method == 'POST':
        print("post to login page")
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        
        if form.is_valid():
          print('login form is valid')
          username = request.POST['username'] #form.cleaned_data['username']
          password = request.POST['password'] #form.cleaned_data['password']
          form.cleaned_data['username'] = ''
          form.cleaned_data['password'] = ''
          
          user = authenticate(request, username=username, password=password)
          if user is not None:
            #create the session
            request.session['username'] = username
            return HttpResponseRedirect('/ophouse/select/')
          else:
            print('userid %s  / password are not-authorized.' % (username))
            error = True
            message = 'user ' + username + ' / password are not authorized.'
            request.session['username'] = None
            form = LoginForm()
            return HttpResponseRedirect('/ophouse/login/')
        else:
          error = True
          message = 'Check your input and try again!'
          print('problem with the login form')
          request.session['username'] = None
          form = LoginForm()
          return HttpResponseRedirect('/ophouse/login/')
    else:
        form = LoginForm()
        return render(request,'login.html', {'form': form, 'error': error, 'message': message,})

def staff(request):
    error = False
    message = ''
    if request.method == 'POST':
        print("post to login page")
        # create a form instance and populate it with data from the request:
        form = StaffForm(request.POST)
        if form.is_valid():
          print('staff form is valid')          
        else:
          print('problem with the staff form')
          form = StaffForm()
          return HttpResponseRedirect('/ophouse/staff/')
    else:
        snapshotLinks = []
        query_attributes = {}
        query_attributes['status'] = SNAPSHOT_STATUS_ACTIVE
        snapshots = PersonSnapshot.objects.all().filter(**query_attributes)
        for snapshot in snapshots:
          #only list the Clients
          if snapshot.person.role == RoleResponse.objects.all().filter(name='Client').first():
            snapshotTuple = (snapshot.pk, snapshot.person.pk, str(snapshot.person.firstname + " " + snapshot.person.lastname))
            snapshotLinks.append(snapshotTuple)
        servicetype_instance_pk = int(request.GET.get("servicetype", 1))
        if len(snapshotLinks)> 0:
          message = 'Select to Add or View Queued Services / Seleccione Agregar o Ver servicios en cola'
        else:
          message = 'There are no clients at present, come back later! / ¡No hay clientes en el presente, vuelve más tarde!'
        form = StaffForm(initial={'snapshotLinks': snapshotLinks}, query_attrs = query_attributes)
        form.fields["snapshots"].queryset = PersonSnapshot.objects.all().filter(**query_attributes) 
        return render(request,'staff.html', {'form': form, 'error': error, 'message': message, 'snapshotLinks': snapshotLinks})

def logout(request):
    try:
      del request.session['username']
      del request.session['password']
    except:
      pass
    return HttpResponseRedirect('/ophouse/')
   
def shorthelp(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    print("redirecting to shorthelp")
    return render(request, 'shorthelp.html')
    
def index(request):
    print("redirecting request through the login/ view")
    return HttpResponseRedirect('/ophouse/login/')
    
def select(request):
    #this is the entry point at the beginning of the day, let's clean-up old snapshots here
    # should we do lifecycle management here?
    snapshots = PersonSnapshot.objects.all().filter(status=SNAPSHOT_STATUS_ACTIVE)
    for snapshot in snapshots:
      #this call will archive old snapshots
      snapshot_lifecycle(snapshot.person, False)
        
    return render(request, 'select.html')

def sign_in(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    try:
      del request.session['aliasname']
      del request.session['aliaspin']
    except:
      pass
    error = False
    myDate = datetime.now()
    # Give a format to the date
    # Displays something like: Aug. 27, 2017, 2:57 p.m.
    formattedDate = myDate.strftime("%A %B %d")
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignInForm(request.POST)
        # check whether it's valid:
        aliasname = request.POST['aliasname']
        aliaspin = request.POST['aliaspin']
        print (aliasname + " " + aliaspin)
        if form.is_valid():
          #print('sign_in POST form is valid')
          createalias = int(request.GET.get("createalias", 0))
          if createalias==0:
            # find the Person, by aliasname and aliaspin
            query_attributes = {}
            query_attributes['aliasname'] = aliasname.upper()
            query_attributes['aliaspin'] = aliaspin.upper()
            persons = Person.objects.all().filter(**query_attributes)
            if persons:
              # Found them!
              print(aliasname + " was found in the DB, redirecting to the Services view.")
              person_instance = persons.first();
              # Wipe History?
              if request.POST.get('wipeHistory', False):
                #print('Wiping all traces related to %s %s' % (person_instance.firstname, person_instance.lastname))
                # get and delete all PersonNote instances
                query_attributes = {}
                query_attributes['person'] = person_instance
                personNotes = PersonNote.objects.all().filter(**query_attributes)
                for personNote in personNotes:
                  personNote.delete()
                #get all the PersonSnapshots for this person
                query_attributes = {}
                query_attributes['person'] = person_instance
                snapShots = PersonSnapshot.objects.all().filter(**query_attributes)
                for snapShot in snapShots:
                  # get and delete all PersonServiceRequest instances
                  query_attributes = {}
                  query_attributes['connection'] = snapShot.pk
                  serviceReqs = PersonServiceRequest.objects.all().filter(**query_attributes)
                  for serviceReq in serviceReqs:
                     serviceReq.delete()
                  # get and delete all Survey instances
                  surveys = PersonSurvey.objects.all().filter(**query_attributes)
                  for survey in surveys:
                     survey.delete()
                  timecards = TimeCard.objects.all().filter(**query_attributes)
                  for timecard in timecards:
                     timecard.delete()
                  # delete the PersonSnapshot instance
                  snapShot.delete()
                print('Wipe is complete!')
                form = SignInForm()
              return HttpResponseRedirect('/ophouse/services?person=%s' % (person_instance.pk))              
            else:
              error = True
              message = 'Try again!'
              form = SignInForm()
              #return HttpResponseRedirect('/ophouse/signin/')
              return render(request, 'sign_in.html', {'form': form, 'error': error, 'message': message, 'date': formattedDate})
        else:
          print('sign_in POST form is NOT valid')
          form = SignInForm()
          return render(request, 'sign_in.html', {'form': form, 'error': error, 'date': formattedDate})
    else:
      form = SignInForm()
      return render(request, 'sign_in.html', {'form': form})

def createalias(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    person_instance_pk = int(request.GET.get("person", 0))
    requestType = request.GET.get("fn", 0)
    print('requestType=%s' % (requestType))
    if request.method == 'POST':
         form = AliasForm(request.POST)
         firstname = request.POST['firstname']
         lastname = request.POST['lastname']
         aliasname = request.POST['aliasname']
         aliaspin = request.POST['aliaspin']
         shortssn = request.POST['shortssn']
         if form.is_valid():
           # aliasname must be unique - verify that it is now
           if Person.objects.all().filter(aliasname=aliasname.upper()).count()==0:
               #this aliasname is available
               print('CreateAlias - aliasname %s is available.' % (aliasname))
               if Person.objects.all().filter(firstname=firstname.upper()).filter(lastname=lastname.upper()).filter(shortssn=shortssn).count()==0:
                 #the firstname, lastname, and ssn are not in the DB, create the Person
                 print('CreateAlias - creating new person in the DB.')
                 person = Person()                 
                 person.role = RoleResponse.objects.all().filter(name='Client').first()
                 person.affiliate = AffiliateResponse.objects.all().filter(name='Unaffiliated').first()
                 person.firstname = firstname.upper()
                 person.lastname = lastname.upper()
                 person.aliasname = aliasname.upper()
                 person.aliaspin = aliaspin
                 person.shortssn = shortssn
                 person.save()
                 message = 'Welcome ' + aliasname + ', your PIN is ' + aliaspin + " Go Back and sign-In now!"
                 return render(request, 'createalias.html', {'form': form, 'message': message, 'person': person.pk})
               else:
                 #firstname, lastname, and ssn are already in the DB - ResetUsername should be used
                 print('CreateAlias - %s %s / SSN=%s already exist in the DB. Use Reset Username function.' % (firstname, lastname, shortssn))
                 message = 'Hmm, it looks like you already have a Username. Go Back and select Reset Username to change your Username or PIN!'
                 error = 'Use Reset Username'
           else:
               #this aliasname already exists, try another name
               print('CreateAlias - the aliasname %s already exists, try something else.' % (aliasname))
               message = 'The username ' + aliasname + ' already exists, try something else.'
               error = 'Try another username'
           return render(request, 'createalias.html', {'form': form, 'message': message, 'error': error})
         else:
           return render(request, 'createalias.html', {'form': form})
         return HttpResponseRedirect('/ophouse/services?person=%s' % (person_instance_pk))     
    else:
      # GET REQUEST      
      form = AliasForm()
      return render(request, 'createalias.html', {'form': form})
      
def resetalias(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    person_instance_pk = int(request.GET.get("person", 0))
    requestType = request.GET.get("fn", 0)
    print('requestType=%s' % (requestType))
    if request.method == 'POST':
         print("alias view POST")
         form = AliasForm(request.POST)
         firstname = request.POST['firstname']
         lastname = request.POST['lastname']
         aliasname = request.POST['aliasname']
         aliaspin = request.POST['aliaspin']
         shortssn = request.POST['shortssn']
         if form.is_valid():
           print('alias POST form validation passed')
           query_attributes = {}
           query_attributes['firstname'] = firstname.upper()
           query_attributes['lastname']  = lastname.upper()
           query_attributes['shortssn'] = shortssn
           person = Person.objects.all().filter(**query_attributes).first()
           if person :
             # Found them and they are requesting a RESET!
             print('%s %s found in the DB, updating aliasname and alias pin.' % (firstname, lastname))
             person.aliasname = aliasname.upper()
             person.aliaspin = aliaspin
             person.save()
             message = 'Got it!  ' +  aliasname + '  - your PIN is ' + aliaspin
             return render(request, 'resetalias.html', {'form': form, 'message': message, 'person': person.pk})
           else:
             print('Name and SSN are not in the DB')
             message = 'Hmm, You need to Create a shortname'
             error = 'the SSN is wonky!'
             #return render(request, 'resetalias.html', {'form': form, 'message': message, 'error': error})
             return HttpResponseRedirect('/ophouse/createalias/')
         else:
           print('resetalias POST form validation failed')
           return render(request, 'resetalias.html', {'form': form})
         return HttpResponseRedirect('/ophouse/services?person=%s' % (person_instance_pk))
    else:
      form = AliasForm()
      return render(request, 'resetalias.html', {'form': form })

def snapshot_lifecycle(person, autoCreate):
    # ############################################
    #
    # SNAPSHOT LIFECYCLE MANAGEMENT FUNCTION
    #
    # (called by the services view on GET request)
    # if not stale:
    #   returns the current snapshot
    # otherwise:
    #   creates and returns a new snapshot
    #
    # ############################################
    preference = Preference.objects.all().filter(name=_ENV).first()
    LANGUAGE = preference.language
    TIMEWARP_FACTOR = preference.timewarp
    SNAPSHOT_TTL_MINUTES = preference.snapshotTimeout
    unarchivedSnapshots = PersonSnapshot.objects.all().filter(person=person.pk).filter(isArchived=False)
    #print('Life-cycle management for %s unarchived PersonSnapshots.' % (unarchivedSnapshots.count()))
    now = datetime.today()
    activeSnapshot = None
    for snapshot in unarchivedSnapshots:
       snapshotDate = snapshot.timestamp.date()
       if SNAPSHOT_TTL_MINUTES > 0:
         staleBefore = now - timedelta(minutes=SNAPSHOT_TTL_MINUTES)
       else:
         #in normal operation we want to stale Snapshots at midnight
         staleBefore = now.replace(hour=0, minute=0, second=0)
       if snapshot.timestamp < staleBefore:
         #if there are any services not completed on the snapshot, set status to SERVICE_STATUS_NOTCOMPLETED
         query_attributes = {}
         query_attributes['connection'] = snapshot
         query_attributes['status'] = SERVICE_STATUS_QUEUED
         snapshotServices = PersonServiceRequest.objects.all().filter(**query_attributes)
         for snapshotService in snapshotServices:
           snapshotService.status = SERVICE_STATUS_NOTCOMPLETED
           snapshotService.save()
         print('Archiving STALE PersonSnapshot %s' % (snapshot))
         snapshot.isArchived = True
         snapshot.status = SNAPSHOT_STATUS_STALE
         snapshot.save()
       else:
         #there are either zero or one currently active snapshot
         activeSnapshot = snapshot
    if activeSnapshot:
      print('Using an OPEN PersonSnapshot instance %s PK=%s.' %(activeSnapshot,activeSnapshot.pk))
      #print('PersonSnapshot timestamp=%s' % (activeSnapshot.timestamp))
    elif autoCreate:
      print('Creating new PersonSnapshot instance.')
      activeSnapshot = PersonSnapshot()
      activeSnapshot.person = person
      activeSnapshot.date = datetime.now
      activeSnapshot.status = SNAPSHOT_STATUS_ACTIVE
      activeSnapshot.save()
    return activeSnapshot
    
def services(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    error = False
    today = datetime.today().weekday()
    if request.method == 'POST':
        connection_instance_pk = int(request.GET.get("connection", False))
        connection_instance = PersonSnapshot.objects.get(pk=connection_instance_pk)
        staffrequest = int(request.GET.get("staff", False))
        if staffrequest == False:
          showDiscretionaryServices = False
        else:
          showDiscretionaryServices = True
        serviceRoles = [connection_instance.person.role, RoleResponse.objects.all().filter(name='All').first()]
        form = ServicesForm(request.POST, query_filters=(showDiscretionaryServices, serviceRoles, today) )
        #connection_instance = PersonSnapshot.objects.get(pk=connection_instance_pk)
        print('Using PersonSnapshot pk=%s' % (connection_instance.pk))
        # check whether it's valid:
        if form.is_valid():
            #POST will pass the PersonSnapshot instance we should be using
            print('processing service request form input')
            # set the Services on the PersonSnapshot instance
            requestedServices = form.cleaned_data['services']
            for service in requestedServices:
              #have to be careful not to recreate Services that already exist on this connection
              print(service.name)
              #get reference to the ServiceName
              query_attributes = {}
              query_attributes['name'] = service.name
              serviceType = Service.objects.all().filter(**query_attributes).first()
              #Want to check if this service is already on the PersonSnapshot before creating it
              query_attributes = {}
              query_attributes['connection'] = connection_instance_pk
              query_attributes['service'] = serviceType.pk
              serviceAlreadyOnConnection = PersonServiceRequest.objects.all().filter(**query_attributes).first()
              if serviceAlreadyOnConnection:
                print('Service %s is already on this PersonSnapshot and will not be duplicated.' % (serviceType.pk))
              else:
                print('Service %s is being added to this PersonSnapshot.'% (serviceType.pk))
                requestedService = PersonServiceRequest()
                requestedService.service = serviceType
                requestedService.status = SERVICE_STATUS_QUEUED
                requestedService.connection = connection_instance
                requestedService.save()
            #Almost done, we now want to check if a client is removed a Service which in on the queue
            query_attributes = {}
            query_attributes['connection'] = connection_instance_pk
            queuedServices = PersonServiceRequest.objects.all().filter(**query_attributes)
            for queuedService in queuedServices:
              foundInRequest = False
              for service in requestedServices:
                  if queuedService.service.pk == service.pk:
                    foundInRequest = True
              if not foundInRequest:
                 queuedService.delete()
        else:
          print('Service form input is invalid - no services are selected')
          query_attributes = {}
          query_attributes['connection'] = connection_instance_pk
          #if any PersonServiceRequests exist we'll delete them now
          personServices = PersonServiceRequest.objects.all().filter(**query_attributes)
          for personService in personServices:
            personService.delete()
        if connection_instance.isSurveyComplete == True:
          if staffrequest:
            return HttpResponseRedirect('/ophouse/staff/')
          else:
            return HttpResponseRedirect('/ophouse/thankyou')
        else:
          #we send staff requests back to their home page
          if staffrequest:
            return HttpResponseRedirect('/ophouse/staff/')
          else:
            return HttpResponseRedirect('/ophouse/prompt?connection=%s' % (connection_instance.pk))
    else:
        #this is a GET request
        person_instance_pk = int(request.GET.get("person", False))
        staffrequest = int(request.GET.get("staff", 0))
        person_instance = Person.objects.get(pk=person_instance_pk)
     
        connection_instance = snapshot_lifecycle(person_instance, True)
        #query_attributes = {}
        #query_attributes['connection'] = connection_instance.pk
        #the services in the active Connection
        services = PersonServiceRequest.objects.all().filter(connection=connection_instance)
        
        if staffrequest == False:
          showDiscretionaryServices = False
        else:
          showDiscretionaryServices = True
        
        serviceRoles = [person_instance.role, RoleResponse.objects.all().filter(name='All').first()]
        serviceTypes = Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=showDiscretionaryServices).filter(targetRole__in=serviceRoles)
    
        serviceQueryFilters = (showDiscretionaryServices, serviceRoles, today)
        
        disabledList =[]
        #process constrained Services
        constrainedServices = Service.objects.all().filter(isConstrained=True)
        for constrainedService in constrainedServices:
          unitsAvailable = constrainedService.unitsAvailable
          unitsUsed = 0
          currentSnapshots = PersonSnapshot.objects.all().filter(status=SNAPSHOT_STATUS_ACTIVE)
          for currentSnapshot in currentSnapshots:
            unitsUsed += PersonServiceRequest.objects.all().filter(connection=currentSnapshot).filter(service=constrainedService).count()
          #if limit is reached we want to disable this selection, however not when the client has already selected this service
          #in this way the client is able to uncheck the service and return it to the pool for use by someone else
          if unitsUsed == unitsAvailable and  PersonServiceRequest.objects.all().filter(connection=connection_instance).filter(service=constrainedService).count()==0:
            disabledList.append(constrainedService.name)
         
        servicelist = [] 
        #we want to preselect the checkbox options for all QUEUED Services in the active Snapshot
        for serviceType in serviceTypes:
           for service in services:
              if service.status != SERVICE_STATUS_COMPLETED:
                if service.service.pk == serviceType.pk:
                   servicelist.append(serviceType.pk)
        form = ServicesForm(initial={'services': servicelist}, query_filters=serviceQueryFilters)
        if serviceTypes.count() == 0:
          return HttpResponseRedirect('/ophouse/prompt?connection=%s' % (connection_instance.pk))
        else:
          return render(request, 'services.html', {'form': form, 'error': error, 'connection': connection_instance.pk, 'staffrequest': staffrequest, 'disabledList': disabledList})

def inference_engine(person, snapshotTimestamp):
    preference = Preference.objects.all().filter(name=_ENV).first()
    LANGUAGE = preference.language
    TIMEWARP_FACTOR = preference.timewarp
    SNAPSHOT_TTL_MINUTES = preference.snapshotTimeout
    #all time deltas should be based on the current snapshot timestamp, not the current time
    #in this version we'll return the first prompt which has no response in the Person record
    ninetyDaysAgo =  snapshotTimestamp - timedelta(days=90)
    snapshots = PersonSnapshot.objects.all().filter(person=person, timestamp__gte=ninetyDaysAgo)
    #print('There are %s snapshots' % (snapshots.count()))
    
    #include all prompts for the person's role plus the 'All' role
    promptRoles = [person.role, RoleResponse.objects.all().filter(name='All').first()]
    #get all of the enabled + unfenced Prompts                            this is how we ask using FK
    #04-03-2018 Add Language specific function: get all prompts in the Clients language + all prompts in language=4(All)
    #           If clients language is Unknown - get the English prompts
    if person.language==LanguageResponse.objects.get(pk=1):
      language = LanguageResponse.objects.all().filter(name='English').first()
    else:
      language = person.language
    languages = [language, LanguageResponse.objects.all().filter(name='All').first()]  
    
    unfencedPrompts = Prompt.objects.all().filter(isEnabled=True).filter(fencingPrompt_id__isnull=True).filter(targetRole__in=promptRoles).filter(language__in=languages)
    #print('unfencedPrompt count=%s' % (unfencedPrompts.count()))
    #sorted by highest priority first
    #print('first prompt is %s' % (unfencedPrompts.first().onscreenPrompt))
    #get the most recent PersonSurvey for this prompt
    for prompt in unfencedPrompts:
        promptSurveys = []
        for snapshot in snapshots:
          #there should one instance, at most, of this prompt on any connection, so first() will do
          #survey = PersonSurvey.objects.all().filter(connection=snapshot, prompt=prompt).first()
          query_attributes = {}
          query_attributes['connection'] = snapshot.pk
          query_attributes['prompt'] = prompt.pk
          survey = PersonSurvey.objects.all().filter(**query_attributes).first()
          if survey:
            surveyTuple = (survey, snapshot.timestamp)
            promptSurveys.append(surveyTuple)
        #we now have all of the Surveys for this Prompt
        #print('\n%s' % (prompt.onscreenPrompt.encode("utf-8")))
        #now sort according to the timestamp        reverse=True is descending order
        if len(promptSurveys)>0:
          promptSurveys.sort(key = operator.itemgetter(1), reverse = True)
          #most recent promptSurvey is in the first position
          latestPromptSurvey = promptSurveys[0]
          #print('Most recent survey for this prompt is %s' % (latestPromptSurvey[0].connection.timestamp))
          if prompt.intervalDays>0:
            #is the latestPromptSurvey older than the intervalDays of the Prompt?
            #notBeforeTime = datetime.today() - timedelta(days=prompt.intervalDays)
            notBeforeTime = snapshotTimestamp - timedelta(minutes=prompt.intervalDays*24*60/TIMEWARP_FACTOR)
            if latestPromptSurvey[1] < notBeforeTime:
              print('...Expired - %s on %s' % (latestPromptSurvey[0].content_object, latestPromptSurvey[1]))
              return prompt.pk
          else:
            #this is a one-time prompt (intervaldays=0)
            print("One-time prompts are never reused.")
        else:
          return prompt.pk
          
    fencedPrompts = Prompt.objects.all().filter(isEnabled=True).filter(fencingPrompt_id__isnull=False).filter(targetRole__in=promptRoles).filter(language__in=languages)
    #print('fencedPrompt count=%s' % (fencedPrompts.count()))
    #get the most recent PersonSurvey for this prompt
    for prompt in fencedPrompts:
        #first, determine if the fence for this prompt has been satisfied
        fencePrompt = prompt.fencingPrompt
        personField = fencePrompt.anchorField
        #print('Fence prompt=%s references Person field=%s key=%s' % (fencePrompt, personField, prompt.fencingResponse))
        if getattr(person, personField).name == prompt.fencingResponse:
          #print('the fence %s is unlocked' % (prompt.onscreenPrompt))
          promptSurveys = []
          for snapshot in snapshots:
            #there should one instance, at most, of this prompt on any connection, so first() will do
            #survey = PersonSurvey.objects.all().filter(connection=snapshot, prompt=prompt).first()
            query_attributes = {}
            query_attributes['connection'] = snapshot.pk
            query_attributes['prompt'] = prompt.pk
            survey = PersonSurvey.objects.all().filter(**query_attributes).first()
            if survey:
              surveyTuple = (survey, snapshot.timestamp)
              promptSurveys.append(surveyTuple)
          #we now have all of the Surveys for this Prompt
          #print('\n%s' % (prompt.onscreenPrompt))
          #now sort according to the timestamp        reverse=True is descending order
          if len(promptSurveys)>0:
            promptSurveys.sort(key = operator.itemgetter(1), reverse = True)
            #most recent promptSurvey is in the first position
            latestPromptSurvey = promptSurveys[0]
            #is the latestPromptSurvey older than the intervalDays of the Prompt?
            #notBeforeTime = datetime.today() - timedelta(days=prompt.intervalDays)
            notBeforeTime = snapshotTimestamp - timedelta(minutes=prompt.intervalDays*5)
            if latestPromptSurvey[1] < notBeforeTime:
                print('...Expired - %s on %s' % (latestPromptSurvey[0].content_object, latestPromptSurvey[1]))
                return prompt.pk
          else:
            return prompt.pk
    #we've looked at all the prompts now
    return 0

def prompt(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    error = False
    connection_instance_pk = int(request.GET.get("connection", False))
    connection_instance = PersonSnapshot.objects.get(pk=connection_instance_pk)
    #if connection_instance:
    #  print('PersonSurvey results will be attached to PersonSnapshot with PK=%s' %(connection_instance_pk))
    # if this is a POST request we need to process the form data
    preference = Preference.objects.all().filter(name=_ENV).first()
    LANGUAGE = preference.language
    TIMEWARP_FACTOR = preference.timewarp
    SNAPSHOT_TTL_MINUTES = preference.snapshotTimeout
    MAXPROMPTS = preference.maxPrompts
    if request.method == 'POST':
        promptPk = int(request.GET.get('prompt', -1))
        fastTrack = request.POST.get('fastTrack', False)
        #if promptPk is False - Skip Survey has been selected
        print('promptPk=%s' % (promptPk))
        if promptPk > 0:
          prompt = Prompt.objects.get(pk=promptPk)
          print('request.POST=%s' % (request.POST))
          query_attributes = {}
          query_attributes['connection'] = connection_instance.pk
          #the services in the active Connection
          survey = PersonSurvey()
          survey.connection = connection_instance
          survey.prompt = prompt
          attribute = prompt.anchorField
          person = connection_instance.person
          if len(prompt.anchorField) > 0:
            print('attribute=%s' % (prompt.anchorField))
            if type(Person._meta.get_field(prompt.anchorField)) == models.fields.CharField:
              survey = PersonSurvey()
              survey.connection = connection_instance
              survey.prompt = prompt
              #the response is in the 'replaceText'
              replaceText = request.POST['replaceText']              
              regex = prompt.regexValidator              
              print('The new value is %s' % (replaceText))
              try:
                setattr(person, attribute, replaceText)
                survey = PersonSurvey(content_object=None)
                survey.connection = connection_instance
                survey.prompt = prompt
                survey.response = replaceText
                survey.save()
                person.save()
              except DataError as e:
                print('input data was not valid')
            elif isinstance(Person._meta.get_field(prompt.anchorField), models.ForeignKey):
              print('request.POST=%s' % (request.POST))
              choice = request.POST.get('choiceField')
              if not choice:        #if they don't select anything use default = Unknown
                choice = 1
              print('The choice is %s' % (choice))
              try:
                fkRelationship = prompt.responseType #re.sub(r'([_])', r' \1', prompt.anchorField).split()[1][1:]
                responseContent = apps.get_model(app_label='guestbook', model_name=fkRelationship).objects.get(pk=choice)
                print('responseContent.pk=%s' % (responseContent.pk))
                #need to record the response in the application language, normally English
                # to correlate we are using the points field of the response object
                languages = [LANGUAGE, LanguageResponse.objects.all().filter(name='All').first()]
                if responseContent.language not in languages:
                   responseContent = apps.get_model(app_label='guestbook', model_name=fkRelationship).objects.all().filter(language=LANGUAGE).filter(points=responseContent.points).first()
                print('responseContent.pk=%s' % (responseContent.pk))
                setattr(person, attribute, responseContent)
                survey = PersonSurvey(content_object=responseContent)
                survey.connection = connection_instance
                survey.prompt = prompt
                survey.response = 'fk'
                #save the point value of the response - it may be hard to recover
                survey.points = responseContent.points
                survey.save()
                person.save()
              except DataError as e:
                print('input data was not valid')
            elif isinstance(Person._meta.get_field(prompt.anchorField), models.ManyToManyField):
              print('POST on M2M Prompt')
              print('request.POST=%s' % (request.POST))
              #choices = request.POST.get('multichoice')
              choices =request.POST.getlist('multichoice')
              print('The choice is %s' % (choices))
              for choice in choices:
                print('choice=%s' % (choice))
              try:
                fkRelationship = prompt.responseType # re.sub(r'([_])', r' \1', prompt.anchorField).split()[1][1:]
                print('fkRelationship=%s' %(fkRelationship))                
                getattr(person, attribute).set(choices)
                # don't think we can save this one  --> survey = PersonSurvey(content_object=choices)
                survey.connection = connection_instance
                survey.prompt = prompt
                survey.response = 'fk'
                survey.save()
                person.save()
              except DataError as e:
                print('input data was not valid')
            else:
              print('Unknown Prompt type!')
            # redirect to a new URL:
        else:
          print('non-anchored prompt')
        
        #temporarily set the following to False during testing
        # isSurveyComplete=True indicates that the Client has been surveyed 
        # Only one Prompt is given for each Snapshot instance
        connection_instance.promptsPresented += 1;
        
        if fastTrack or connection_instance.promptsPresented < int(MAXPROMPTS):
          #keep going until we run out of prompts to ask
          print('We can queue %s more prompts.' % (MAXPROMPTS - connection_instance.promptsPresented))
          connection_instance.save()
          return HttpResponseRedirect('/ophouse/prompt?connection=%s' % (connection_instance.pk))
        else:
          #stop when we have reached the configured limit in maxPrompts property
          connection_instance.isSurveyComplete = True
          connection_instance.save()
          return HttpResponseRedirect('/ophouse/thankyou')
    # if a GET (or any other method) we'll create a blank form
    else:      
      query_attributes = {}
      query_attributes['isEnabled'] = True
      #call the inference_engine to determine which Prompt to use
      promptPk = inference_engine(connection_instance.person, connection_instance.timestamp)
      if promptPk > 0:
        survey = Prompt.objects.get(pk=promptPk)
      else:
        survey = None
      if survey == None:
        print('There are no enabled Prompt objects in the DB!')
        return HttpResponseRedirect('/ophouse/thankyou')
      else:
        prompt = str(survey)
        #determine the personField class
        if survey.anchorField and len(survey.anchorField) > 0:
          replString = getattr(connection_instance.person, survey.anchorField)
          print(replString)
          survey.currentValue = replString
        form = SurveyForm(survey=survey, person=connection_instance.person)
        return render(request, 'prompt.html', {'form': form, 'error': error, 'whichQuestion': survey , 'survey': survey.onscreenPrompt, 'response': survey, 'connection': connection_instance.pk})

def queue(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    error = False
    myDate = datetime.now()
    # Give a format to the date
    # Displays something like: Aug. 27, 2017, 2:57 p.m.
    formattedDate = myDate.strftime("%A %B-%d @ %I:%M%p")
    if request.method == 'POST':
      servicetype_instance_pk = int(request.GET.get("servicetype", 0))
      form = QueueForm(request.POST)
      if form.is_valid():
        #required for cleaned_data
        service = form.cleaned_data['services']        
        print('Service PK=%s' % (service.pk))
        serviceToComplete = service 
        #Service.objects.get(pk=service.pk)
        print('Service %s is marked for completion.' % (serviceToComplete))
        serviceToComplete.status = SERVICE_STATUS_COMPLETED
        serviceToComplete.save()
        #now. take care of the PersonSnapshot status
        query_attributes = {}
        query_attributes['connection'] = serviceToComplete.connection.pk
        query_attributes['status'] = SERVICE_STATUS_QUEUED
        numberOfOtherServicesOnConnectionNotCompleted = PersonServiceRequest.objects.all().filter(**query_attributes).count()
        if numberOfOtherServicesOnConnectionNotCompleted == 0:
          #Close the PersonSnapshot
          print('Setting SNAPSHOT_STATUS_CLOSED on the PersonSnapshot container')
          connectionToClose = PersonSnapshot.objects.get(pk=serviceToComplete.connection.pk)
          #Uncomment the following to Archive a snapshot once all of the Services have be dequeued
          #connectionToClose.status = SNAPSHOT_STATUS_CLOSED
          #connectionToClose.isArchived = True
          connectionToClose.save()
        return HttpResponseRedirect('/ophouse/queue?servicetype=%s' % (servicetype_instance_pk))
      else:
        print('POST form validation failed - no Client was selected')
        return HttpResponseRedirect('/ophouse/queue?servicetype=%s' % (servicetype_instance_pk))
    else:
      query_attributes = {}
      query_attributes['isDiscretionary'] = False
      serviceTypes = Service.objects.all().filter(**query_attributes)
      serviceLinks = []
      for serviceType in serviceTypes:
         query_attributes = {}
         query_attributes['service'] = serviceType.pk
         query_attributes['status'] = SERVICE_STATUS_QUEUED
         queueSize = PersonServiceRequest.objects.all().filter(**query_attributes).count()
         #if queueSize > 0:
         #  queueSizeString = '(%s)' % (queueSize)
         #else:
         #  queueSizeString = ''
         #serviceTuple = (str(serviceType.pk), serviceType.name, queueSizeString)
         if queueSize > 0:
           queueSizeString = '[%s]' % (queueSize)
         else:
           queueSizeString = ''
         
         if serviceType.isDiscretionary == True:
           isDiscretionary = 1
         else:
           isDiscretionary = 0
           
         serviceTuple = (serviceType.pk, serviceType.name, isDiscretionary, queueSizeString)
         serviceLinks.append(serviceTuple)
      servicetype_instance_pk = int(request.GET.get("servicetype", 1))      
      queuename = Service.objects.get(pk=servicetype_instance_pk)
      query_attributes = {}
      query_attributes['service'] = servicetype_instance_pk
      query_attributes['status'] = SERVICE_STATUS_QUEUED
      form = QueueForm()
      form.fields["services"].queryset = PersonServiceRequest.objects.all().filter(**query_attributes)
      queuesize = PersonServiceRequest.objects.all().filter(**query_attributes).count()
      if queuesize > 1:
        queuemessage = 'There are %s clients on the queue:' % (queuesize)
      elif queuesize > 0:
        queuemessage = 'There is 1 client on the queue:'
      else:
        queuemessage = 'The queue is empty.'
    return render(request, 'queue.html', {'form': form, 'error': error, 'queuesize': queuesize, 'queuemessage': queuemessage, 'servicetype': servicetype_instance_pk, 'queuename': queuename, 'servicelinks': serviceLinks, 'date': formattedDate})
    
def staffqueue(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    error = False
    myDate = datetime.now()
    # Give a format to the date
    # Displays something like: Aug. 27, 2017, 2:57 p.m.
    formattedDate = myDate.strftime("%A %B-%d @ %I:%M%p")
    if request.method == 'POST':
      servicetype_instance_pk = int(request.GET.get("servicetype", 0))
      form = QueueForm(request.POST)
      if form.is_valid():
        #required for cleaned_data
        service = form.cleaned_data['services']
        print('Service PK=%s' % (service.pk))
        serviceToComplete = service 
        #Service.objects.get(pk=service.pk)
        print('Service %s is marked for completion.' % (serviceToComplete))
        serviceToComplete.status = SERVICE_STATUS_COMPLETED
        serviceToComplete.save()
        #now. take care of the PersonSnapshot status
        query_attributes = {}
        query_attributes['connection'] = serviceToComplete.connection.pk
        query_attributes['status'] = SERVICE_STATUS_QUEUED
        numberOfOtherServicesOnConnectionNotCompleted = PersonServiceRequest.objects.all().filter(**query_attributes).count()
        if numberOfOtherServicesOnConnectionNotCompleted == 0:
          #Close the PersonSnapshot
          print('Setting SNAPSHOT_STATUS_CLOSED on the PersonSnapshot container')
          connectionToClose = PersonSnapshot.objects.get(pk=serviceToComplete.connection.pk)
          #Uncomment the following to Archive a snapshot once all of the Services have be dequeued
          #connectionToClose.status = SNAPSHOT_STATUS_CLOSED
          #connectionToClose.isArchived = True
          connectionToClose.save()
        return HttpResponseRedirect('/ophouse/staffqueue?servicetype=%s' % (servicetype_instance_pk))
      else:
        print('POST form validation failed - no Client was selected')
        return HttpResponseRedirect('/ophouse/staffqueue?servicetype=%s' % (servicetype_instance_pk))
    else:
      query_attributes = {}
      #query_attributes['isDiscretionary'] = False
      serviceTypes = Service.objects.all().filter(**query_attributes)
      serviceLinks = []
      for serviceType in serviceTypes:
         query_attributes = {}
         query_attributes['service'] = serviceType.pk
         query_attributes['status'] = SERVICE_STATUS_QUEUED
         queueSize = PersonServiceRequest.objects.all().filter(**query_attributes).count()
         
         if queueSize > 0:
           queueSizeString = '[%s]' % (queueSize)
         else:
           queueSizeString = ''
         
         if serviceType.isDiscretionary == True:
           isDiscretionary = 1
         else:
           isDiscretionary = 0
           
         serviceTuple = (serviceType.pk, serviceType.name, isDiscretionary, queueSizeString)
         serviceLinks.append(serviceTuple)
      servicetype_instance_pk = int(request.GET.get("servicetype", 1))      
      queuename = Service.objects.get(pk=servicetype_instance_pk)
      query_attributes = {}
      query_attributes['service'] = servicetype_instance_pk
      query_attributes['status'] = SERVICE_STATUS_QUEUED
      form = QueueForm()
      queuesize = PersonServiceRequest.objects.all().filter(**query_attributes).count()
      if queuesize > 1:
        queuemessage = 'There are %s clients on the queue:' % (queuesize)
      elif queuesize > 0:
        queuemessage = 'There is 1 client on the queue:'
      else:
        queuemessage = 'The queue is empty.'
      form.fields["services"].queryset = PersonServiceRequest.objects.all().filter(**query_attributes)
    return render(request, 'staffqueue.html', {'form': form, 'error': error, 'queuesize': queuesize, 'queuemessage': queuemessage, 'servicetype': servicetype_instance_pk, 'queuename': queuename, 'servicelinks': serviceLinks, 'date': formattedDate})
 
def note(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    error = False
    myDate = datetime.now()
    # Give a format to the date
    # Displays something like: Aug. 27, 2017, 2:57 p.m.
    formattedDate = myDate.strftime("%A %B-%d @ %I:%M%p")
    if request.method == 'POST':      
      form = PersonNoteForm(request.POST)
      if form.is_valid():
        connection_pk = int(request.GET.get('connection', -1))
        print('connection_pk for note is %s' % (connection_pk))
        snapshot = PersonSnapshot.objects.get(pk=connection_pk)
        print('processing note form for %s %s.' % (snapshot.person.firstname, snapshot.person.lastname))
        personNote = PersonNote()
        personNote.connection = snapshot
        personNote.note = form.cleaned_data['note']
        personNote.save()
      else:
        print('Note form is not valid')
      return HttpResponseRedirect('/ophouse/staff/')
    else:
      connection_pk = int(request.GET.get("connection", False))
      form = PersonNoteForm()
      snapshot = PersonSnapshot.objects.get(pk=connection_pk)
      person = snapshot.person
      displayname = person.firstname + " " + person.lastname
      timestamp = snapshot.timestamp.strftime("%A %B-%d")
      return render(request, 'note.html', {'form': form, 'connection': connection_pk, 'displayname': displayname, 'timestamp': timestamp})



def thankyou(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    return render(request, 'thankyou.html')