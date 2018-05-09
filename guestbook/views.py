from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import operator
from django import forms
from django.db import models
from datetime import datetime
from random import sample, randint
from django.db import IntegrityError, DataError
from django.conf import settings

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

from twilio.rest import Client
import re
import django
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

import logging
log = logging.getLogger('GBLOGGER')

_ENV = 'PROD'

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
      log.debug('reporter post')
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
          log.debug('response=%s %s' % (response[0], response[1]))
          labels.append(response[0])
          values.append(response[1])
        #let's show the possible responses to the selected prompt in the graph legend
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
      log.debug('session-cookie found!')
      return True
    else:
      log.debug('session-cookie not found')
      return False
      
def mobile(request):
    #Return True if the request comes from a mobile device."""
    log.info('HTTP_USER_AGENT=%s' % (request.META['HTTP_USER_AGENT']))
    #log.info('DEVICE=%s' % (request.META['DEVICE_TYPE']))
    MOBILE_AGENT_RE=re.compile(r".*(HpEnvy2.0)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        log.debug('Touch')
        return True
    else:
        log.debug('Desktop')
        return False

def login(request):
    error = False
    message = ''
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
    #key_variable = request.session.pop('username')  
    #if key_variable:
    #  del key_variable
    if request.method == 'POST':
        log.debug("post to login page")
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        
        if form.is_valid():
          log.debug('login form is valid')
          username = request.POST['username'] #form.cleaned_data['username']
          password = request.POST['password'] #form.cleaned_data['password']
          form.cleaned_data['username'] = ''
          form.cleaned_data['password'] = ''
          
          user = authenticate(request, username=username, password=password)
          if user is not None:
            #create the session
            request.session['username'] = username
            log.info('Guestbook Admin login complete. This is Django version= %s.%s.%s' % (django.VERSION[0], django.VERSION[1], django.VERSION[2]))
            return HttpResponseRedirect('/ophouse/select/')
          else:
            log.warn('userid %s  is not-an authorized.Guestbook Admin.' % (username))
            error = True
            message = 'userid %s  is not-an authorized Guestbook Admin.' % (username)
            request.session['username'] = None
            form = LoginForm()
            #return HttpResponseRedirect('/ophouse/login/')
            return render(request,'login.html', {'form': form, 'device': device, 'error': error, 'message': message,})
        else:
          error = True
          message = 'Check your input and try again!'
          log.debug('problem with the login form')
          request.session['username'] = None
          form = LoginForm()
          #return HttpResponseRedirect('/ophouse/login/')
          return render(request,'login.html', {'form': form, 'device': device, 'error': error, 'message': message,})
    else:
        form = LoginForm()
        return render(request,'login.html', {'form': form, 'device': device, 'error': error, 'message': message,})

def staff(request):
    error = False
    message = ''
    if request.method == 'POST':
        log.debug("post to login page")
        # create a form instance and populate it with data from the request:
        form = StaffForm(request.POST)
        if form.is_valid():
          log.debug('staff form is valid')          
        else:
          log.debug('problem with the staff form')
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
    log.debug("redirecting to shorthelp")
    return render(request, 'shorthelp.html')
    
def index(request):
    log.debug("redirecting request through the login/ view")
    return HttpResponseRedirect('/ophouse/login/')
    
def select(request):
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
    #this is the entry point at the beginning of the day, let's clean-up old snapshots here
    # should we do lifecycle management here?
    snapshots = PersonSnapshot.objects.all().filter(status=SNAPSHOT_STATUS_ACTIVE)
    for snapshot in snapshots:
      #this call will archive old snapshots
      snapshot_lifecycle(snapshot.person, False)
        
    return render(request, 'select.html', {'device': device})

def sign_in(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
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
        log.debug (aliasname + " " + aliaspin)
        if form.is_valid():
          #log.debug('sign_in POST form is valid')
          createalias = int(request.GET.get("createalias", 0))
          if createalias==0:
            # find the Person, by aliasname and aliaspin
            query_attributes = {}
            query_attributes['aliasname'] = aliasname.upper()
            query_attributes['aliaspin'] = aliaspin.upper()
            persons = Person.objects.all().filter(**query_attributes)
            if persons:
              # Found them!
              log.debug(aliasname + " was found in the DB, redirecting to the Services view.")
              person_instance = persons.first();
              # Wipe History?
              if request.POST.get('wipeHistory', False):
                #log.debug('Wiping all traces related to %s %s' % (person_instance.firstname, person_instance.lastname))
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
                log.debug('Wipe is complete!')
                form = SignInForm()
              return HttpResponseRedirect('/ophouse/services?person=%s' % (person_instance.pk))              
            else:
              error = True
              log.warn('Username %s/%s is not authorized for the Client Kiosk.' % (aliasname, aliaspin))
              message = 'Don\'t know that one, try again!'
              form = SignInForm()
              #return HttpResponseRedirect('/ophouse/signin/')
              return render(request, 'sign_in.html', {'form': form, 'error': error, 'message': message, 'device': device, 'date': formattedDate})
        else:
          log.debug('sign_in POST form is NOT valid')
          error = True
          message = 'Don\'t know that one, try again!'
          form = SignInForm()
          return render(request, 'sign_in.html', {'form': form, 'error': error, 'message': message, 'device': device, 'date': formattedDate})
    else:
      form = SignInForm()
      return render(request, 'sign_in.html', {'form': form, 'device': device})

def createalias(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
    person_instance_pk = int(request.GET.get("person", 0))
    requestType = request.GET.get("fn", 0)
    log.debug('requestType=%s' % (requestType))
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
               log.debug('CreateAlias - aliasname %s is available.' % (aliasname))
               if Person.objects.all().filter(firstname=firstname.upper()).filter(lastname=lastname.upper()).filter(shortssn=shortssn).count()==0:
                 #the firstname, lastname, and ssn are not in the DB, create the Person
                 log.debug('CreateAlias - creating new person in the DB.')
                 person = Person()                 
                 person.role = RoleResponse.objects.all().filter(name='Client').first()
                 person.affiliate = AffiliateResponse.objects.all().filter(name='Unaffiliated').first()
                 person.firstname = firstname.upper()
                 person.lastname = lastname.upper()
                 person.aliasname = aliasname.upper()
                 person.aliaspin = aliaspin
                 person.shortssn = shortssn
                 person.save()
                 log.info('%s %s has created Username=%s from the Client Kiosk.' % (person.firstname, person.lastname, person.aliasname))
                 message = 'Welcome ' + aliasname + ', your PIN is ' + aliaspin + " Go Back and sign-In now!"
                 return render(request, 'createalias.html', {'form': form, 'device': device, 'message': message, 'person': person.pk})
               else:
                 #firstname, lastname, and ssn are already in the DB - ResetUsername should be used
                 log.debug('CreateAlias - %s %s / SSN=%s already exist in the DB. Use Reset Username function.' % (firstname, lastname, shortssn))
                 message = 'Hmm, it looks like you already have a Username. Go Back and select Reset Username to change your Username or PIN!'
                 error = 'Use Reset Username'
           else:
               #this aliasname already exists, try another name
               log.debug('CreateAlias - the aliasname %s already exists, try something else.' % (aliasname))
               message = 'The username ' + aliasname + ' already exists, try something else.'
               error = 'Try another username'
           return render(request, 'createalias.html', {'form': form, 'device': device, 'message': message, 'error': error})
         else:
           return render(request, 'createalias.html', {'form': form})
         return HttpResponseRedirect('/ophouse/services?person=%s' % (person_instance_pk))     
    else:
      # GET REQUEST      
      form = AliasForm()
      return render(request, 'createalias.html', {'form': form, 'device': device})
      
def resetalias(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
    person_instance_pk = int(request.GET.get("person", 0))
    requestType = request.GET.get("fn", 0)
    log.debug('requestType=%s' % (requestType))
    if request.method == 'POST':
         log.debug("alias view POST")
         form = AliasForm(request.POST)
         firstname = request.POST['firstname']
         lastname = request.POST['lastname']
         aliasname = request.POST['aliasname']
         aliaspin = request.POST['aliaspin']
         shortssn = request.POST['shortssn']
         if form.is_valid():
           log.debug('alias POST form validation passed')
           query_attributes = {}
           query_attributes['firstname'] = firstname.upper()
           query_attributes['lastname']  = lastname.upper()
           query_attributes['shortssn'] = shortssn
           person = Person.objects.all().filter(**query_attributes).first()
           if person :
             # Found them and they are requesting a RESET!
             log.debug('%s %s found in the DB, updating aliasname and alias pin.' % (firstname, lastname))
             person.aliasname = aliasname.upper()
             person.aliaspin = aliaspin
             person.save()
             message = 'Got it!  ' +  aliasname + '  - your PIN is ' + aliaspin
             log.info('%s %s has reset a Username=%s from the Client Kiosk.' % (person.firstname, person.lastname, person.aliasname))
             return render(request, 'resetalias.html', {'form': form, 'device': device, 'message': message, 'person': person.pk})
           else:
             log.debug('Name and SSN are not in the DB')
             message = 'Hmm, You need to Create a shortname'
             error = 'the SSN is wonky!'
             #return render(request, 'resetalias.html', {'form': form, 'message': message, 'error': error})
             return HttpResponseRedirect('/ophouse/createalias/')
         else:
           log.debug('resetalias POST form validation failed')
           return render(request, 'resetalias.html', {'form': form})
         return HttpResponseRedirect('/ophouse/services?person=%s' % (person_instance_pk))
    else:
      form = AliasForm()
      return render(request, 'resetalias.html', {'form': form , 'device': device})

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
    #log.debug('Life-cycle management for %s unarchived PersonSnapshots.' % (unarchivedSnapshots.count()))
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
         log.info('Archiving STALE PersonSnapshot %s' % (snapshot))
         snapshot.isArchived = True
         snapshot.status = SNAPSHOT_STATUS_STALE
         snapshot.save()
       else:
         #there are either zero or one currently active snapshot
         activeSnapshot = snapshot
    if activeSnapshot:
      log.debug('Using an OPEN PersonSnapshot instance %s PK=%s.' %(activeSnapshot,activeSnapshot.pk))
      #log.debug('PersonSnapshot timestamp=%s' % (activeSnapshot.timestamp))
    elif autoCreate:
      log.debug('Creating new PersonSnapshot instance.')
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
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
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
        log.debug('Using PersonSnapshot pk=%s' % (connection_instance.pk))
        # check whether it's valid:
        if form.is_valid():
            #POST will pass the PersonSnapshot instance we should be using
            log.debug('processing service request form input')
            # set the Services on the PersonSnapshot instance
            requestedServices = form.cleaned_data['services']
            for service in requestedServices:
              #have to be careful not to recreate Services that already exist on this connection
              log.debug(service.name)
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
                log.debug('Service %s is already on this PersonSnapshot and will not be duplicated.' % (serviceType.pk))
              else:
                log.debug('Service %s is being added to this PersonSnapshot.'% (serviceType.pk))
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
          log.debug('Service form input is invalid - no services are selected')
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
          #if limit is reached we want to disable this selection, however not when the client has already selected this service, and it is still queued
          #in this way the client is able to uncheck the service and return it to the pool for use by someone else
          if unitsUsed == unitsAvailable and  PersonServiceRequest.objects.all().filter(connection=connection_instance).filter(service=constrainedService).filter(status=SERVICE_STATUS_QUEUED).count()==0:
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
          return render(request, 'services.html', {'form': form, 'error': error, 'device': device, 'connection': connection_instance.pk, 'staffrequest': staffrequest, 'disabledList': disabledList})

def inference_engine(person, snapshotTimestamp):
    preference = Preference.objects.all().filter(name=_ENV).first()
    LANGUAGE = preference.language
    TIMEWARP_FACTOR = preference.timewarp
    SNAPSHOT_TTL_MINUTES = preference.snapshotTimeout
    #all time deltas should be based on the current snapshot timestamp, not the current time
    #in this version we'll return the first prompt which has no response in the Person record
    
    #next, we'll get all of the PersonSnapshots that are less than 90days old
    ninetyDaysAgo =  snapshotTimestamp - timedelta(days=90)
    snapshots = PersonSnapshot.objects.all().filter(person=person, timestamp__gte=ninetyDaysAgo)
    #log.debug('There are %s snapshots' % (snapshots.count()))
    
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
    
    #next, we'll get all <Enabled> <Unfenced> prompts for the oersons specifice <Role> and the "All" Role
    unfencedPrompts = Prompt.objects.all().filter(isEnabled=True).filter(fencingPrompt_id__isnull=True).filter(targetRole__in=promptRoles).filter(language__in=languages)
    #log.debug('unfencedPrompt count=%s' % (unfencedPrompts.count()))
    #sorted by highest priority first
    if unfencedPrompts:
      log.debug('The highest priority prompt is %s' % (unfencedPrompts.first().onscreenPrompt))
      #get the most recent PersonSurvey for each of these prompts
      for prompt in unfencedPrompts:
          promptSurveys = []
          #next, we'll iterate over the most recent snapshots to determine if it is time for this prompt to be presented again
          log.debug('The prompt is: %s' % (prompt.onscreenPrompt))
          for snapshot in snapshots:
            #there should one instance, at most, of this prompt on any Snapshot
            query_attributes = {}
            query_attributes['connection'] = snapshot.pk
            query_attributes['prompt'] = prompt.pk
            survey = PersonSurvey.objects.all().filter(**query_attributes).first()
            if survey:
              #we've found a response to this prompt in the snapshot, nominalize the snapshot date to 00:00:00 
              #in this way we are not bound to a strict 24hours=1day 
              surveyTuple = (survey, snapshot.timestamp.replace(hour=0, minute=0, second=0))
              promptSurveys.append(surveyTuple)
          if len(promptSurveys)>0:
            #we now have all of the Surveys for this Prompt, sort according to the timestamp  reverse=True is descending order, most recent is first
            promptSurveys.sort(key = operator.itemgetter(1), reverse = True)
            #most recent promptSurvey is in the first position
            latestPromptSurvey = promptSurveys[0]
            log.debug('The most recent survey for this prompt is %s' % (latestPromptSurvey[0].connection.timestamp))
            if prompt.intervalDays>0:
              #is the latestPromptSurvey older than the intervalDays of the Prompt?
              #for the daily prompts we have to do some time arithmetic, rounding the times to days
              notBeforeTime = snapshotTimestamp - timedelta(minutes=prompt.intervalDays*24*60/TIMEWARP_FACTOR)
              if latestPromptSurvey[1] < notBeforeTime:
                log.debug('...the most recent response is stale, %s on %s' % (latestPromptSurvey[0].content_object, latestPromptSurvey[1]))
                #this is the prompt we're going to use!
                log.info('Username %s is asked -- %s' % (person.aliasname, prompt.onscreenPrompt))
                return prompt.pk
            #else:
              #this is a one-time prompt (intervaldays=0)
              #log.debug("One-time prompts are never reused!")
          else:
            log.info('Username %s is asked -- %s' % (person.aliasname, prompt.onscreenPrompt))
            return prompt.pk
          
    fencedPrompts = Prompt.objects.all().filter(isEnabled=True).filter(fencingPrompt_id__isnull=False).filter(targetRole__in=promptRoles).filter(language__in=languages)
    if fencedPrompts:
      #log.debug('fencedPrompt count=%s' % (fencedPrompts.count()))
      #get the most recent PersonSurvey for this prompt
      for prompt in fencedPrompts:
          #first, determine if the fence for this prompt has been satisfied
          fencePrompt = prompt.fencingPrompt
          personField = fencePrompt.anchorField
          #log.debug('Fence prompt=%s references Person field=%s key=%s' % (fencePrompt, personField, prompt.fencingResponse))
          if getattr(person, personField).name == prompt.fencingResponse:
            #log.debug('the fence %s is unlocked' % (prompt.onscreenPrompt))
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
            #log.debug('\n%s' % (prompt.onscreenPrompt))
            #now sort according to the timestamp        reverse=True is descending order
            if len(promptSurveys)>0:
              promptSurveys.sort(key = operator.itemgetter(1), reverse = True)
              #most recent promptSurvey is in the first position
              latestPromptSurvey = promptSurveys[0]
              #is the latestPromptSurvey older than the intervalDays of the Prompt?
              #notBeforeTime = datetime.today() - timedelta(days=prompt.intervalDays)
              notBeforeTime = snapshotTimestamp - timedelta(minutes=prompt.intervalDays*5)
              if latestPromptSurvey[1] < notBeforeTime:
                  log.debug('...Expired - %s on %s' % (latestPromptSurvey[0].content_object, latestPromptSurvey[1]))
                  log.info('Username %s is asked -- %s' % (person.aliasname, prompt.onscreenPrompt))
                  return prompt.pk
            else:
              log.info('Username %s is asked -- %s' % (person.aliasname, prompt.onscreenPrompt))
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
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
    error = False
    connection_instance_pk = int(request.GET.get("connection", False))
    connection_instance = PersonSnapshot.objects.get(pk=connection_instance_pk)
    #if connection_instance:
    #  log.debug('PersonSurvey results will be attached to PersonSnapshot with PK=%s' %(connection_instance_pk))
    # if this is a POST request we need to process the form data
    preference = Preference.objects.all().filter(name=_ENV).first()
    LANGUAGE = preference.language
    TIMEWARP_FACTOR = preference.timewarp
    SNAPSHOT_TTL_MINUTES = preference.snapshotTimeout
    MAXPROMPTS = preference.maxPrompts
    if request.method == 'POST':
        promptPk = int(request.GET.get('prompt', -1))
        fastTrack = request.POST.get('fastTrack', False)
        #if promptPk is -1 - Skip Survey has been selected
        log.debug('promptPk=%s' % (promptPk))
        if promptPk > 0:
          prompt = Prompt.objects.get(pk=promptPk)
          log.debug('request.POST=%s' % (request.POST))
          query_attributes = {}
          query_attributes['connection'] = connection_instance.pk
          #the services in the active Connection
          survey = PersonSurvey()
          survey.connection = connection_instance
          survey.prompt = prompt
          attribute = prompt.anchorField
          person = connection_instance.person
          if len(prompt.anchorField) > 0:
            log.debug('attribute=%s' % (prompt.anchorField))
            if type(Person._meta.get_field(prompt.anchorField)) == models.fields.CharField:
              survey = PersonSurvey()
              survey.connection = connection_instance
              survey.prompt = prompt
              #the response is in the 'replaceText'
              replaceText = request.POST['replaceText']              
              regex = prompt.regexValidator              
              log.debug('The new value is %s' % (replaceText))
              try:
                setattr(person, attribute, replaceText)
                survey = PersonSurvey(content_object=None)
                survey.connection = connection_instance
                survey.prompt = prompt
                survey.response = replaceText
                survey.save()
                person.save()
              except DataError as e:
                log.debug('input data was not valid')
            elif isinstance(Person._meta.get_field(prompt.anchorField), models.ForeignKey):
              log.debug('request.POST=%s' % (request.POST))
              choice = request.POST.get('choiceField')
              if not choice:        #if they don't select anything use default = Unknown
                choice = 1
              log.debug('The choice is %s' % (choice))
              try:
                fkRelationship = prompt.responseType #re.sub(r'([_])', r' \1', prompt.anchorField).split()[1][1:]
                responseContent = apps.get_model(app_label='guestbook', model_name=fkRelationship).objects.get(pk=choice)
                log.debug('responseContent.pk=%s' % (responseContent.pk))
                #need to record the response in the application language, normally English
                # to correlate we are using the points field of the response object
                languages = [LANGUAGE, LanguageResponse.objects.all().filter(name='All').first()]
                if responseContent.language not in languages:
                   responseContent = apps.get_model(app_label='guestbook', model_name=fkRelationship).objects.all().filter(language=LANGUAGE).filter(points=responseContent.points).first()
                log.debug('responseContent.pk=%s' % (responseContent.pk))
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
                log.debug('input data was not valid')
            elif isinstance(Person._meta.get_field(prompt.anchorField), models.ManyToManyField):
              log.debug('POST on M2M Prompt')
              log.debug('request.POST=%s' % (request.POST))
              #choices = request.POST.get('multichoice')
              choices =request.POST.getlist('multichoice')
              log.debug('The choice is %s' % (choices))
              for choice in choices:
                log.debug('choice=%s' % (choice))
              try:
                fkRelationship = prompt.responseType # re.sub(r'([_])', r' \1', prompt.anchorField).split()[1][1:]
                log.debug('fkRelationship=%s' %(fkRelationship))                
                getattr(person, attribute).set(choices)
                # don't think we can save this one  --> survey = PersonSurvey(content_object=choices)
                survey.connection = connection_instance
                survey.prompt = prompt
                survey.response = 'fk'
                survey.save()
                person.save()
              except DataError as e:
                log.debug('input data was not valid')
            else:
              log.debug('Unknown Prompt type!')
            log.info('Username %s has responded to the survey prompt.' % (connection_instance.person.aliasname))
        else:
          log.info('Username %s is skipping the survey prompt.' % (connection_instance.person.aliasname))
        
        #temporarily set the following to False during testing
        # isSurveyComplete=True indicates that the Client has been surveyed 
        # Only one Prompt is given for each Snapshot instance
        connection_instance.promptsPresented += 1;
        
        if fastTrack or connection_instance.promptsPresented < int(MAXPROMPTS):
          #keep going until we run out of prompts to ask
          log.debug('We can queue %s more prompts.' % (MAXPROMPTS - connection_instance.promptsPresented))
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
        log.warn('There are no enabled Prompt objects in the DB!')
        return HttpResponseRedirect('/ophouse/thankyou')
      else:
        prompt = str(survey)
        #determine the personField class
        if survey.anchorField and len(survey.anchorField) > 0:
          replString = getattr(connection_instance.person, survey.anchorField)
          log.debug(replString)
          survey.currentValue = replString
        form = SurveyForm(survey=survey, person=connection_instance.person)
        return render(request, 'prompt.html', {'form': form, 'error': error, 'device': device, 'whichQuestion': survey , 'survey': survey.onscreenPrompt, 'response': survey, 'connection': connection_instance.pk})

def queue(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
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
        log.debug('Service PK=%s' % (service.pk))
        serviceToComplete = service 
        #Service.objects.get(pk=service.pk)
        log.debug('Service %s is marked for completion.' % (serviceToComplete))
        log.info('Service %s has been completed for Username %s.' % (serviceToComplete.service.name, serviceToComplete.connection.person.aliasname ))
        serviceToComplete.status = SERVICE_STATUS_COMPLETED
        serviceToComplete.save()
        #now. take care of the PersonSnapshot status
        query_attributes = {}
        query_attributes['connection'] = serviceToComplete.connection.pk
        query_attributes['status'] = SERVICE_STATUS_QUEUED
        numberOfOtherServicesOnConnectionNotCompleted = PersonServiceRequest.objects.all().filter(**query_attributes).count()
        if numberOfOtherServicesOnConnectionNotCompleted == 0:
          #Close the PersonSnapshot
          log.info('All requested services have now been completed for Username %s.' % (serviceToComplete.connection.person.aliasname))
          log.debug('Setting SNAPSHOT_STATUS_CLOSED on the PersonSnapshot container')
          connectionToClose = PersonSnapshot.objects.get(pk=serviceToComplete.connection.pk)
          #Uncomment the following to Archive a snapshot once all of the Services have be dequeued
          #connectionToClose.status = SNAPSHOT_STATUS_CLOSED
          #connectionToClose.isArchived = True
          connectionToClose.save()
        return HttpResponseRedirect('/ophouse/queue?servicetype=%s' % (servicetype_instance_pk))
      else:
        log.debug('POST form validation failed - no Client was selected')
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
    return render(request, 'queue.html', {'form': form, 'device': device, 'error': error, 'queuesize': queuesize, 'queuemessage': queuemessage, 'servicetype': servicetype_instance_pk, 'queuename': queuename, 'servicelinks': serviceLinks, 'date': formattedDate})
    
def staffqueue(request):
    #Security
    if not checksession(request):
       return HttpResponseRedirect('/ophouse/login/')
    else:
       username = request.session['username']
    #End-Security
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
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
        log.debug('Service PK=%s' % (service.pk))
        serviceToComplete = service 
        #Service.objects.get(pk=service.pk)
        log.debug('Service %s is marked for completion.' % (serviceToComplete))
        serviceToComplete.status = SERVICE_STATUS_COMPLETED
        serviceToComplete.save()
        #now. take care of the PersonSnapshot status
        query_attributes = {}
        query_attributes['connection'] = serviceToComplete.connection.pk
        query_attributes['status'] = SERVICE_STATUS_QUEUED
        numberOfOtherServicesOnConnectionNotCompleted = PersonServiceRequest.objects.all().filter(**query_attributes).count()
        if numberOfOtherServicesOnConnectionNotCompleted == 0:
          #Close the PersonSnapshot
          log.debug('Setting SNAPSHOT_STATUS_CLOSED on the PersonSnapshot container')
          connectionToClose = PersonSnapshot.objects.get(pk=serviceToComplete.connection.pk)
          #Uncomment the following to Archive a snapshot once all of the Services have be dequeued
          #connectionToClose.status = SNAPSHOT_STATUS_CLOSED
          #connectionToClose.isArchived = True
          connectionToClose.save()
        return HttpResponseRedirect('/ophouse/staffqueue?servicetype=%s' % (servicetype_instance_pk))
      else:
        log.debug('POST form validation failed - no Client was selected')
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
    return render(request, 'staffqueue.html', {'form': form, 'device': device, 'error': error, 'queuesize': queuesize, 'queuemessage': queuemessage, 'servicetype': servicetype_instance_pk, 'queuename': queuename, 'servicelinks': serviceLinks, 'date': formattedDate})
 
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
        log.debug('connection_pk for note is %s' % (connection_pk))
        snapshot = PersonSnapshot.objects.get(pk=connection_pk)
        log.debug('processing note form for %s %s.' % (snapshot.person.firstname, snapshot.person.lastname))
        personNote = PersonNote()
        personNote.connection = snapshot
        personNote.note = form.cleaned_data['note']
        personNote.save()
      else:
        log.debug('Note form is not valid')
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
    if mobile(request):
      device='Touch'
    else:
      device='Laptop'
    return render(request, 'thankyou.html', {'device': device})