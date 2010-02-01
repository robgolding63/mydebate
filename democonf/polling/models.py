from django.db import models

class Poll(models.Model):
	question = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.question
	
class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name="choices")
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()
    
    def __unicode__(self):
    	return self.choice
