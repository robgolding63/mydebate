import datetime
from uuid import uuid4

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User

Poll = models.get_model("polling", "poll")

from polling.models import Poll

ROOM_MODE_CHOICES = (
	('conferencing', 'Conferencing'),
	('voting', 'Voting'),
)

class Room(models.Model):
	poll = models.ForeignKey(Poll, unique=True)
	current_members = models.ManyToManyField(User, related_name="member_of", editable=False)
	opened_by = models.ForeignKey(User, related_name="opened_rooms", db_index=True)
	opened_at = models.DateTimeField(auto_now_add=True, db_index=True)
	period_length = models.IntegerField(default=600)
	next_vote_at = models.DateTimeField(editable=False)
	slug = models.CharField(max_length=200, editable=False, unique=True, db_index=True)
	
	def get_and_mark(self, user):
		messages = self.messages.exclude(read_by=user)
		for message in messages:
			message.mark_for(user)
		return messages
	
	def get_unread(self, user):
		return self.messages.exclude(read_by=user)
	
	def get_mode(self):
		now = datetime.datetime.now()
		if now < self.next_vote_at:
			return "conferencing"
		else:
			if self.poll.get_num_votes() >= self.current_members.count():
				self.poll.reset()
				self.next_vote_at = now + datetime.timedelta(seconds=self.period_length)
				self.save()
				return "conferencing"
			return "voting"
	
	def get_time_to_next_vote(self):
		now = datetime.datetime.now()
		if self.next_vote_at < now:
			return 0
		else:
			return (self.next_vote_at - now).seconds
	
	def save(self, *args, **kwargs):
		if self.poll is not None:
			self.slug = slugify(self.poll.question)
		if not self.id:
			now = datetime.datetime.now()
			next_vote = now + datetime.timedelta(seconds=self.period_length)
			self.next_vote_at = next_vote
		super(Room, self).save(*args, **kwargs)
	
	@models.permalink
	def get_absolute_url(self):
		return ('rooms_conference_room', [self.slug])
	
	def __unicode__(self):
		return self.poll.question
	
class Message(models.Model):
	id = models.CharField(max_length=64, primary_key=True)
	room = models.ForeignKey(Room, related_name="messages")
	author = models.ForeignKey(User, related_name="messages")
	content = models.TextField()
	read_by = models.ManyToManyField(User, blank=True, related_name="read_messages")
	created = models.DateTimeField(auto_now_add=True)
	
	def mark_for(self, user):
		self.read_by.add(user)
	
	def save(self, *args, **kwargs):
		if not self.id:
			self.id = str(uuid4())
		super(Message, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return self.content