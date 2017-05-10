from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

from .models import Agent
from del3.models import Invite
from orders.models import OrderInfo

import random
from datetime import datetime


def index(request):
	agent_list = Agent.objects.all()
	attribs = Agent._meta.fields
	codes = Invite.objects.all()
	try:
		agent = Agent.objects.get(agent_id=request.user.id)
		show_button = True
		return render(request, 'agents/index.html', {'codes': codes, 'show_button': show_button,'agent_list': agent_list, 'attribs': attribs})
	except Agent.DoesNotExist:
		return render(request, 'agents/index.html', {'codes': codes, 'agent_list': agent_list, 'attribs': attribs})

@staff_member_required
def delete_agent(request, agent_id):
	agent = Agent.objects.get(pk=agent_id)
	user = User.objects.get(pk=agent_id)
	user.delete()
	agent.delete()
	return HttpResponseRedirect(reverse('agents:index'))	

@staff_member_required
def generate(request):
	check = False
	while not check:
		code = random.randint(1, 100)
		try:
			Invite.objects.get(invite_code=code)
		except Invite.DoesNotExist:
			check = True
	invite = Invite(invite_code=code, used=False)
	invite.save()
	return HttpResponseRedirect(reverse("agents:index"))

def approve(request):
	try:
		agent = Agent.objects.get(pk=request.user.id)
		order_list = OrderInfo.objects.filter(agent_id=agent, issue_time=None, cart_ready=True)
		attribs = OrderInfo._meta.fields
		return render(request, 'agents/approve.html', {'order_list': order_list, 'attribs': attribs})
	except Agent.DoesNotExist:
		return HttpResponseRedirect(reverse('agents:index'))

def approve_order(request, order_id):
	try:
		agent = Agent.objects.get(pk=request.user.id)
		order = OrderInfo.objects.get(order_id=order_id)
		if order.cart_ready is True:
			order.issue_date = datetime.today()
			order.issue_time = datetime.now().time()
			order.delivery_date = datetime.today()
			order.delivery_time = datetime.now().time()
			order.save()
			return HttpResponseRedirect(reverse('agents:approve'))
		else:
			return HttpResponseRedirect(reverse('agents:approve'))
	except Agent.DoesNotExist:
		return HttpResponseRedirect(reverse('agents:index'))

