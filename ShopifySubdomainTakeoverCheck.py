#!/usr/bin/python3

import sys
import requests
import dns.resolver

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SUBDOMAIN_TAKEOVER_ERROR_MESSAGE = 'Sorry, this shop is currently unavailable.'

def check_web_page(hostname):
	""" Return True if the page looks vulnerable to Subdomain Takeover otherwise return False """
	try:
		r = requests.get('https://%s' % hostname, verify=False)
	except requests.exceptions.ConnectionError:
		return False

	if SUBDOMAIN_TAKEOVER_ERROR_MESSAGE in r.text:
		return True
	else:
		return False

def get_shop_name(hostname):
	""" Return the shop name from the hostname. Return None is no CNAME found. """
	try:
		cnames = dns.resolver.query(hostname, 'CNAME')
	except:
		print("Unexpected error:", sys.exc_info()[0])
		return False

	for cname in cnames:
		cname = str(cname)[:-1]
		if '.myshopify.com' in cname:
			shop_name = cname.replace('.myshopify.com','')
			return shop_name

	return None

def check_shop_name_availability(shop_name):
	""" Return True if the shop name is available otherwise return False """
	r = requests.get('https://app.shopify.com//services/signup/check_availability.json?callback=jQuery32106011450060372039_1520363418444&shop_name=%s&email=test@example.comm&_=1520363418450' % shop_name, verify=False)

	# TODO: Fix this check because is super ugly :P
	if '"status":"available"' in r.text:
		return True
	else:
		return False

def check(hostname):
	""" Return True if the hostname is vulnerable to Subdomain Takeover, otherwise return False """
	if check_web_page(hostname):
		shop_name = get_shop_name(hostname)
		if shop_name == 'shops':
			print('%s - Vulnerable to Subdomain Takeover via DNS Mapping' % (hostname))
			return True
		else:
			if check_shop_name_availability(shop_name):
				print('%s - Vulnerable to Subdomain Takeover via Shop Name (%s)' % (hostname,shop_name))
				return True
	else:
		print('Hostname: %s is NOT vulnerable to Subdomain Takeover.' % (hostname))
		return False


def help():
	""" Display help """
	print('Use:')
	print('./%s hostname' % sys.argv[0])

if __name__ == '__main__':
	if (len(sys.argv) != 2):
		help()
	else:
		check(sys.argv[1])
