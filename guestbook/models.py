from django.db import models

# Guestbook Models

from datetime import datetime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from localflavor.us.models import USStateField
from localflavor.us.models import USZipCodeField

SERVICE_STATUS_QUEUED       = 500
SERVICE_STATUS_COMPLETED    = 501

SNAPSHOT_STATUS_ACTIVE    = 800
SNAPSHOT_STATUS_STALE     = 801
SNAPSHOT_STATUS_CLOSED    = 802

class LanguageResponse(models.Model):
    idlanguage = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey('self', on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=32)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class AffiliateResponse(models.Model):
    idaffiliate = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=32)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class RoleResponse(models.Model):
    idrole = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=24)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name
        
class YesNoResponse(models.Model):
    idyesno = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=16)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

#this is where we keep eduction & skills catalog
class SkillsExperienceResponse(models.Model):
    idSkillsExperience = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=64)
    points = models.IntegerField(null=True, default=0)
    def save(self, force_insert=False, force_update=False):
        self.name = self.name.upper()
        super(SkillsExperience, self).save(force_insert, force_update)
    def __str__(self):
        return self.name

class EthnicityResponse(models.Model):
    idethnicity = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=24)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class GenderResponse(models.Model):
    idgender = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=24)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class EducationResponse(models.Model):
    ideducation = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=64)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name
        
class HousingResponse(models.Model):
    idhousing = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=128)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class PhysicalHealthResponse(models.Model):
    idphysicalhealth = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=128)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name
        
class EmotionalHealthResponse(models.Model):
    idemotionalhealth = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=128)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class NumberRangeResponse(models.Model):
    idrange = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=32)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class HourRangeResponse(models.Model):
    idhourrange = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=32)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name
        
class CountResponse(models.Model):
    idcount = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=32)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name
        
class RatingResponse(models.Model):
    idrating = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=True)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    name = models.CharField(max_length=32)
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name
        
#Prompt is used as a way of asking the client a question
#  each instance is associated with an anchorField in the Person table  (e.g. isHomeless. isUnEmployed, email, telephone, etc.)
#  the form is dynamically generated depending on the Person field class (boolean, varchar, etc.)
#  if theRegexValidator is specified, the response will be validated before the Person field is updated
#  the form includes option to leave value alone, in effect to "Skip the Survey" 
class Prompt(models.Model):
    idprompt = models.BigAutoField(primary_key=True)
    isEnabled = models.NullBooleanField()    
    onscreenPrompt = models.CharField(max_length=256)
    intervalDays = models.IntegerField(default=0)
    anchorField = models.CharField(max_length=64, blank=True, null=True)
    responseType = models.CharField(max_length=64, blank=True, null=True)
    regexValidator = models.CharField(max_length=128, blank=True, null=True)
    targetRole = models.ForeignKey(RoleResponse, on_delete=models.PROTECT, blank=True, null=True)
    fencingPrompt = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    fencingResponse = models.CharField(max_length=64, blank=True, null=True)
    priority = models.IntegerField(default=1)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=4)
    def __str__(self):
       if self.isEnabled:
         return  self.onscreenPrompt
       else:
         return  self.onscreenPrompt
    class Meta:
       #query sorted on highest priority (negative sign yields descending order)
       ordering = ('-priority','idprompt')

class Person(models.Model):
    idperson = models.BigAutoField(primary_key=True)
    firstname = models.CharField(max_length=24)
    lastname = models.CharField(max_length=24)
    aliasname = models.CharField(max_length=8, unique=True, default='none')
    aliaspin = models.CharField( max_length=4, default='none')
    shortssn = models.CharField( max_length=4, default='none')
    birthdate = models.DateField(null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\d{3}-\d{3}-\d{4}$|^\d{10}$|^\d{3} \d{3} \d{4}$', message='Area code and number')
    #phone_regex = RegexValidator(regex=r'^\+?1?\d{10,12}$', message="Phone number must be entered in the format: '0001112222'. 10 digits are required.")
    telephone = models.CharField(validators=[phone_regex], max_length=10, blank=True, default='7045550000')
    canText = models.ForeignKey(YesNoResponse, related_name='yesno_cansmstext', on_delete=models.PROTECT, default=1)
    #email = models.EmailField(max_length=32, blank=True, default='no email record')
    email_regex = RegexValidator(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message='name@domain.com')
    email = models.CharField(validators=[email_regex], max_length=32, blank=True, default='you@somewhere.com')
    streetAddress = models.CharField(max_length=32,blank=True)
    city = models.CharField(max_length=16,blank=True)
    state = USStateField(blank=True)
    zip = USZipCodeField(blank=True)
    timelineStartDate = models.DateField(auto_now=True)
    gender = models.ForeignKey(GenderResponse,on_delete=models.PROTECT, default=1)
    ethnicity = models.ForeignKey(EthnicityResponse, on_delete=models.PROTECT, default=1)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=1)
    #default role is Client ----------------
    role = models.ForeignKey(RoleResponse,on_delete=models.PROTECT, null=True, default=2)
    affiliation = models.ForeignKey(AffiliateResponse,on_delete=models.PROTECT, default=1)
    education = models.ForeignKey(EducationResponse,on_delete=models.PROTECT, null=True, default=1)
    skills = models.ManyToManyField(SkillsExperienceResponse, blank=True)        
    veteran = models.ForeignKey(YesNoResponse, related_name='yesno_isveteran', on_delete=models.PROTECT, default=1)
    receivesSSiOrDisabilityIncome = models.ForeignKey(YesNoResponse, related_name='yesno_receivesssi', on_delete=models.PROTECT, default=1)
    receivesChildSupportIncome = models.ForeignKey(YesNoResponse, related_name='yesno_receiveschildsupport', on_delete=models.PROTECT, default=1)
    receivesOtherRetirementIncome = models.ForeignKey(YesNoResponse, related_name='yesno_receivesotherretirement', on_delete=models.PROTECT, default=1)
    receivesEmploymentIncome = models.ForeignKey(YesNoResponse, related_name='yesno_receivesemployment', on_delete=models.PROTECT, default=1)
    registeredSexOffender = models.ForeignKey(YesNoResponse, related_name='yesno_isregisteredsexoffender', on_delete=models.PROTECT, default=1)
    incidentLawEnforcement = models.ForeignKey(YesNoResponse, related_name='yesno_incidentlawenforcement', on_delete=models.PROTECT, default=1)
    incidentEmergencyMedical = models.ForeignKey(YesNoResponse, related_name='yesno_incidentemergencymedical', on_delete=models.PROTECT, default=1)
    
    housing = models.ForeignKey(HousingResponse, on_delete=models.PROTECT, default=1)    
    physicalHealth = models.ForeignKey(PhysicalHealthResponse, on_delete=models.PROTECT, default=1)
    emotionalHealth = models.ForeignKey(EmotionalHealthResponse, on_delete=models.PROTECT, default=1)    
    grossIncomeAllSources = models.ForeignKey( NumberRangeResponse, related_name='nrange_grossincomeallsources', on_delete=models.PROTECT, default=1)
    grossIncomeEmployment = models.ForeignKey( NumberRangeResponse, related_name='nrange_grossemploymentincome', on_delete=models.PROTECT, default=1)
    grossIncomeSsiorDisability = models.ForeignKey( NumberRangeResponse, related_name='nrange_grossssiordisabilityincome', on_delete=models.PROTECT, default=1)
    grossIncomeOtherRetirement = models.ForeignKey( NumberRangeResponse, related_name='nrange_ssorotherretirementincome', on_delete=models.PROTECT, default=1)
    grossIncomeChildSupport = models.ForeignKey( NumberRangeResponse, related_name='nrange_childsupportincome', on_delete=models.PROTECT, null=True, default=1)
    grossIncomeOther = models.ForeignKey( NumberRangeResponse, related_name='nrange_otherincome', on_delete=models.PROTECT, default=1)
    
    #situational metrics - these should be accumulated across a moving time window
    #the housing prompt is presented frequently - daily
    #the event prompts (law enforcement, medical emergency, religious and training) are presented less frequently - weekly?
    daysStableHousing = models.IntegerField(default=0)
    daysUnstableHousing = models.IntegerField(default=0)
    daysSheltered = models.IntegerField(default=0)
    daysUnsheltered = models.IntegerField(default=0)
    daysIncarcerated = models.IntegerField(default=0)
    numberMedicalEmergencies = models.IntegerField(default=0)
    numberLawEnforcementEvents = models.IntegerField(default=0)
    numberEducAndReligiousEvents = models.IntegerField(default=0)    
    #following field is for volunteers only
    lastHoursWorked = models.ForeignKey( HourRangeResponse, related_name='hrange_lasthoursworked', on_delete=models.PROTECT, null=True, blank=True)
        
    def save(self, force_insert=False, force_update=False):
        self.firstname = self.firstname.upper()
        self.lastname = self.lastname.upper()
        self.aliasname = self.aliasname.upper()
        self.email = self.email.upper()
        self.city = self.city.upper()
        self.streetaddress = self.streetAddress.upper()
        super(Person, self).save(force_insert, force_update)
    def __str__(self):
        return self.firstname + " " + self.lastname
    def get_foreign_keys(self):
        foreign_keys = []
        for field in self._meta.fields:
            if isinstance(self._meta.get_field(field.name), models.ForeignKey):
                foreign_keys.append(field.name)
        if not foreign_keys:
            return None
        return foreign_keys
    def get_mm_keys(self):
        mm_keys = []
        #for field in self._meta.fields:
        for field in self._meta.many_to_many:
            #if isinstance(self._meta.get_field(field.name), models.ManyToManyField):
            #if field.__class__.__name__ == 'ManyRelatedManager':
                mm_keys.append(field.name)
        if not mm_keys:
            return None
        return mm_keys

class Service(models.Model):
    idservice = models.BigAutoField(primary_key=True)
    isEnabled = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    isDiscretionary = models.BooleanField(default=False)
    isConstrained = models.BooleanField(default=False)
    unitsAvailable = models.IntegerField(default=0)
    #days of week
    SUN = models.BooleanField(default=False)
    MON = models.BooleanField(default=True)
    TUE = models.BooleanField(default=True)
    WED = models.BooleanField(default=True)
    THU = models.BooleanField(default=True)
    FRI = models.BooleanField(default=True)
    SAT = models.BooleanField(default=False)
    #for whom is this service intended?
    targetRole = models.ForeignKey(RoleResponse, on_delete=models.PROTECT, blank=True, null=True)
    def __str__(self):
        return self.name
        
class PersonSnapshot(models.Model):
    idsnapshot = models.BigAutoField(primary_key=True)
    #auto_now_add=True sets timestamp on record creation
    #auto_now=True updates timestamp each time save() is called
    timestamp = models.DateTimeField(("DateTime"),auto_now_add=True)
    person = models.ForeignKey(Person,on_delete=models.PROTECT, null=True)
    status = models.IntegerField(db_column='status', null=True)
    isSurveyComplete = models.BooleanField(default = False)
    promptsPresented = models.IntegerField(default=0)
    isArchived = models.BooleanField(default = False)
    def __str__(self):
        statusString = 'OPEN'
        if self.isArchived:
          statusString = 'CLOSED'
        return statusString + "-" + str(self.timestamp.strftime("%A - %B %d, %Y %I:%M%p")) + " with " + self.person.firstname + " " + self.person.lastname

class PersonServiceRequest(models.Model):
    idservice = models.BigAutoField(primary_key=True)
    connection = models.ForeignKey(PersonSnapshot, on_delete=models.PROTECT, null=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True)
    status = models.IntegerField(db_column='status', null=True)
    def __str__(self):
        return self.connection.person.firstname + " " + self.connection.person.lastname + "/" + self.connection.person.aliasname + " " + str(self.connection.timestamp.strftime("%I:%M%p"))
    class Meta:
       #query sorted on oldest first
       ordering = ('connection__timestamp','idservice')

class PersonSurvey(models.Model):
    idpersonsurvey = models.BigAutoField(primary_key=True)
    connection = models.ForeignKey(PersonSnapshot, on_delete=models.PROTECT, null=True)
    prompt = models.ForeignKey(Prompt,on_delete=models.PROTECT, null=True)
    response = models.CharField(max_length=64, null=True)
    content_type = models.ForeignKey(ContentType, related_name='content_type_timelines', null=True, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    points = models.IntegerField(null=True, default=0)
    def __str__(self):
       return self.connection.person.firstname + " " + self.connection.person.lastname + " responded to " + self.prompt.onscreenPrompt
    class Meta:
       #query sorted on oldest first
       ordering = ('connection__timestamp','idpersonsurvey')
       
class PersonNote(models.Model):
    idpersonnote = models.BigAutoField(primary_key=True)
    connection = models.ForeignKey(PersonSnapshot, on_delete=models.PROTECT, null=True)
    note = models.TextField(max_length=128)
    def __str__(self):
       return self.connection.person.firstname + " " + self.connection.person.lastname + " " +  str(self.connection.timestamp.strftime("%A - %B %d, %Y")) + "/" + self.note
       
class AppProperty(models.Model):
    idappproperty = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=32)
    def __str__(self):
       return self.name + "=" + self.value
       
class Preference(models.Model):
    idpreference = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    language = models.ForeignKey(LanguageResponse, on_delete=models.PROTECT, default=2)
    maxPrompts = models.PositiveIntegerField(default=2)
    snapshotTimeout = models.PositiveIntegerField(default=0)
    timewarp = models.PositiveIntegerField(default=1)
    def __str__(self):
       return self.name + "=" + self.language.name



