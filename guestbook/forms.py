from django import forms
from django.db import models
from django.forms import ModelForm, Textarea, PasswordInput
from django.core.validators import RegexValidator

from guestbook.models import Person
from guestbook.models import PersonSnapshot
from guestbook.models import Service
from guestbook.models import PersonSurvey
from guestbook.models import PersonServiceRequest
#from guestbook.models import SurveyForm
from guestbook.models import HousingResponse
from guestbook.models import SkillsExperienceResponse
from guestbook.models import LanguageResponse
from guestbook.models import Prompt
from guestbook.models import Preference

from django.forms import Select
import re
from django.apps import apps

SERVICE_STATUS_QUEUED       = 500
SERVICE_STATUS_COMPLETED    = 501

SNAPSHOT_STATUS_ACTIVE    = 800
SNAPSHOT_STATUS_STALE     = 801
SNAPSHOT_STATUS_CLOSED    = 802

_ENV = 'PROD'

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class ReporterForm(forms.Form):
    preference = Preference.objects.all().filter(name=_ENV).first()
    LANGUAGE = preference.language
    persons = forms.ModelChoiceField(queryset=Person.objects.all(), empty_label=None)
    prompts = forms.ModelChoiceField(queryset=Prompt.objects.all().filter(language=LANGUAGE).filter(responseType__isnull=False), empty_label=None)

class LoginForm(forms.Form):
    user_regex = RegexValidator(regex=r'^[a-zA-Z0-9]{3,10}$', message="User must be a Guestbook Admin. Try again!")
    pass_regex = RegexValidator(regex=r'^[a-zA-Z0-9]{7,10}$', message="is your password correct?")
    #username = forms.CharField(label='Username', validators=[user_regex], min_length=5, max_length=10, widget=forms.TextInput(attrs={'size':'16', 'class':'inputText'}))
    #password = forms.CharField(label='Password', validators=[pass_regex], min_length=5, max_length=12, widget=forms.PasswordInput(attrs={'size':'16', 'class':'inputText'}))
    #username = forms.CharField(label='Username', validators=[user_regex], min_length=5, max_length=10, )
    #password = forms.CharField(label='Password')  #widget=PasswordInput())
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    def clean_username(self):
        data = self.cleaned_data['username']
        return data
    def clean_password(self):
        data = self.cleaned_data['password']
        return data

class SignInForm(forms.Form):
    pin_regex = RegexValidator(regex=r'^\+?1?\d{4,4}$', message="The PIN is a 4 digit number. Try again!")
    name_regex = RegexValidator(regex=r'^[a-zA-Z0-9]{3,8}$', message="The Shortname is 3 to 5 letters and numbers only. Try again!")
    #aliasname = forms.CharField(label='Shortname', validators=[name_regex], min_length=3, max_length=8, widget=forms.TextInput(attrs={'size':'8', 'class':'inputText'}))
    #aliaspin  = forms.CharField()
    aliasname = forms.CharField(validators=[name_regex], max_length=8, widget=forms.TextInput(attrs={'size':'8', 'class':'form-control','placeholder':'Username'}))
    aliaspin = forms.CharField(validators=[pin_regex], max_length=4, widget=forms.PasswordInput(attrs={'size':'4', 'class':'form-control','placeholder':'PIN'}))
    wipeHistory = forms.BooleanField(required=False)
    def clean_aliaspin(self):
        data = self.cleaned_data['aliaspin']
        # Remember to always return the cleaned data.
        return data
    def clean_aliasname(self):
        data = self.cleaned_data['aliasname']
        # Remember to always return the cleaned data.
        return data


class SurveyForm(forms.Form):
    fastTrack = forms.BooleanField(initial=True, required=False)
    def __init__(self, survey, person, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        if person.language==LanguageResponse.objects.get(pk=1):
          language = LanguageResponse.objects.all().filter(name='English').first()
        else:
          language = person.language
        languages = [language, LanguageResponse.objects.all().filter(name='All').first()]
        self.fields['prompt'] = forms.CharField(label=survey.onscreenPrompt,max_length=256)
        #self.fields['fastTrack'] = forms.BooleanField(initial=True, required=False)
        #print(type(Person._meta.get_field(survey.anchorField)))
        #print("processing survey form for %s." % (person.firstname))
        foreignKeyFields = Person.get_foreign_keys(person)
        mmKeyFields = Person.get_mm_keys(person)        
        if survey.anchorField and len(survey.anchorField) > 0:
          if survey.anchorField in mmKeyFields:
             m2mRelationship = survey.responseType
             #
             #
             # M2M PROMPT FORM
             # 
             # 
             #print('it is a M2M relationship with %s.' % (m2mRelationship))
             thePersonChoices = getattr(person, survey.anchorField).all()
             theChoices = apps.get_model(app_label='guestbook', model_name=m2mRelationship).objects.all().filter(language__in=languages)
             theSelections = []
             for theChoice in theChoices:
               #does this person currently have this choice selected
               for thePersonChoice in thePersonChoices:
                 if theChoice == thePersonChoice:
                    theSelections.append(theChoice.pk)
             #print('thePersonChoices=%s' % (thePersonChoices))
             #print('theSelections=%s' % (theSelections))
             self.initial['multiChoice'] = theSelections
             self.fields['multiChoice'] = forms.ModelMultipleChoiceField(queryset=apps.get_model(app_label='guestbook', model_name=m2mRelationship).objects.all().filter(language__in=languages), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
             #self.fields['multiChoice'].initial = person.hasSkillsExperience
          elif survey.anchorField in foreignKeyFields:
             # foreign key fields are named as follows:
             # lowercasedescriptor_UppercaseModel, e.g. currentHousing is a FK relationship with the Housing model
             fkRelationship = survey.responseType
             #print('fkRelationship=%s' % (fkRelationship))
             #
             #
             # FOREIGN KEY PROMPT FORM
             # 
             # 
             #print('it is a ForeignKey to %s' % (fkRelationship))
             thePersonChoice = getattr(person, survey.anchorField)
             #print('thePersonChoice=%s pk=%s' % (thePersonChoice, thePersonChoice.pk))
             self.initial['choiceField'] = thePersonChoice
             self.fields['choiceField'] = forms.ChoiceField(choices=[(choice.pk, choice) for choice in apps.get_model(app_label='guestbook', model_name=fkRelationship).objects.all().filter(isEnabled=True).filter(language__in=languages)], widget=forms.RadioSelect(attrs={'class': 'form-control'}))
          #elif type(Person._meta.get_field(survey.anchorField)) == models.fields.EmailField:
          #   print('it is an EmailField!')
          #   self.fields['replaceText'] = forms.EmailField(max_length=64, initial=survey.currentValue) # widget=forms.TextInput(attrs={'class': 'form-control'}))
          elif type(Person._meta.get_field(survey.anchorField)) == models.fields.CharField:
             #
             #
             # CHARFIELD PROMPT FORM
             # 
             # 
             personField = Person._meta.get_field(survey.anchorField)
             #self.fields['replaceText'] = forms.CharField(initial=survey.currentValue, max_length=256, widget=forms.TextInput(attrs={'class': 'form-control'}))
             self.fields['replaceText'] = forms.CharField(initial=getattr(person, survey.anchorField), max_length=256, widget=forms.TextInput(attrs={'class': 'form-control', 'size':64}))
             #print('it is a CharField!')
        else:
            #an unanchored Prompt
            print("Unanchored Prompt")

class ServicesForm(forms.Form):
    #we will show ONLY the Services that are currently Enabled
    #def __init__(self, service, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        #self.query_attributes = kwargs.pop('query_attrs')
        self.query_filters = kwargs.pop('query_filters')
        super(ServicesForm, self).__init__(*args, **kwargs)
        #Mon=0, Sun=6
        today = self.query_filters[2]
        if today==0:
          self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]).filter(MON=True), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
        elif today==1:
          self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]).filter(TUE=True), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
        elif today==2:
          self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]).filter(WED=True), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
        elif today==3:
          self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]).filter(THU=True), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
        elif today==4:
          self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]).filter(FRI=True), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
        elif today==5:
          self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]).filter(SAT=True), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
        else:
          self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]).filter(SUN=True), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
        
        #self.fields['services'] = forms.ModelMultipleChoiceField(queryset=Service.objects.all().filter(isEnabled=True).filter(isDiscretionary=self.query_filters[0]).filter(targetRole__in=self.query_filters[1]), widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
    
class Meta:
        model = Service
        fields = ['name']

class AliasForm(forms.Form):
    firstname = forms.CharField(max_length=24,widget=forms.TextInput(attrs={'size':'24', 'class':'form-control','placeholder':'Firstname'}))
    lastname = forms.CharField(max_length=24,widget=forms.TextInput(attrs={'size':'24', 'class':'form-control','placeholder':'Lastname'}))
    pin_regex = RegexValidator(regex=r'^\+?1?\d{4,4}$', message="The PIN is a 4 digit number. Try again!")
    name_regex = RegexValidator(regex=r'^[a-zA-Z0-9]{3,8}$', message="The Shortname is 3 to 8 letters and numbers only. Try again!")
    ssn_regex = RegexValidator(regex=r'^\+?1?\d{4,4}$', message="The last 4 digits of your SSN are numeric.. Try again!")
    aliasname = forms.CharField(validators=[name_regex], max_length=8, widget=forms.TextInput(attrs={'size':'8','class':'form-control','placeholder':'Nickname'}))
    aliaspin  = forms.CharField(validators=[pin_regex], max_length=4, widget=forms.TextInput( attrs={'size':'4','class':'form-control','placeholder':'PIN'}))
    shortssn  = forms.CharField(validators=[ssn_regex], max_length=4, widget=forms.TextInput( attrs={'size':'4','class':'form-control','placeholder':'last 4 SSN'}))

class StaffForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.query_attributes = kwargs.pop('query_attrs')
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['snapshots'] = forms.ModelChoiceField(queryset=PersonSnapshot.objects.all().filter(**self.query_attributes), empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))

class QueueForm(forms.Form):
    #services = forms.ModelMultipleChoiceField(queryset=PersonServiceRequest.objects.all().order_by('connection__timestamp'),widget=forms.CheckboxSelectMultiple)
    #was services = forms.ModelMultipleChoiceField(queryset=PersonServiceRequest.objects.all().order_by('connection__timestamp'),widget=forms.CheckboxSelectMultiple(attrs={'name':'charlie'}))
    services = forms.ModelChoiceField(queryset=PersonServiceRequest.objects.all().order_by('connection__timestamp'), empty_label=None, widget=forms.RadioSelect(attrs={'class': 'form-control'}))

class PersonNoteForm(forms.Form):
    note = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control', 'size':64}))



