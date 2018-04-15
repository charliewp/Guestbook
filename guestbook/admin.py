from django.contrib import admin

# Register your models here.
from .models import  AffiliateResponse
from .models import  RoleResponse
from .models import  EducationResponse
from .models import  Person
from .models import  Prompt
from .models import  PersonSurvey
from .models import  PersonNote
from .models import  SkillsExperienceResponse
from .models import  PersonServiceRequest
from .models import  PersonSnapshot
from .models import  Service
#from .models import  Response
from .models import  EthnicityResponse
from .models import  GenderResponse
from .models import  RoleResponse
#from .models import  PersonTimeCard
from .models import  HousingResponse
from .models import  NumberRangeResponse
from .models import  YesNoResponse
from .models import  CountResponse
from .models import  AppProperty
from .models import  Preference
from .models import  LanguageResponse

admin.site.register (AffiliateResponse)
admin.site.register (EducationResponse)
admin.site.register (Person)
admin.site.register (Prompt)
admin.site.register (PersonSurvey)
admin.site.register (PersonNote)
admin.site.register (SkillsExperienceResponse)
admin.site.register (PersonServiceRequest)
admin.site.register (PersonSnapshot)
admin.site.register (Service)
#admin.site.register (Response)
admin.site.register (EthnicityResponse)
admin.site.register (GenderResponse)
#admin.site.register (PersonTimeCard)
admin.site.register (HousingResponse)
admin.site.register (NumberRangeResponse)
admin.site.register (YesNoResponse)
admin.site.register (CountResponse)
admin.site.register (RoleResponse)
admin.site.register (AppProperty)
admin.site.register (LanguageResponse)
admin.site.register (Preference)



# to create the superuser python manage.py createsuperuser