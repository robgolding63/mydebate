## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.conf.urls.defaults import *

urlpatterns = patterns('',
	
	url(r'^$', 'django.views.generic.simple.direct_to_template', { 'template': 'faq/index.html' }, name="faq_index"),
	
)
