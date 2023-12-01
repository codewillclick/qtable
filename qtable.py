#!/bin/env python3

import time
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

class Query:
	class All(str):
		pass
	class Script(str):
		@staticmethod
		def format(s):
			return '''
				function $r(...r)   { return Array.from(...r) }
				function $q(...r)   { return document.querySelector(...r) }
				function $qq(...r)  { return document.querySelectorAll(...r) }
				function $qqr(...r) { return $r($qq(...r)) }
			''' + s
		pass

class TimeoutException(Exception):
	pass

class Wait:
	@staticmethod
	def sleep(secs):
		time.sleep(secs)
	@staticmethod
	def until(check,interval=.25,timeout=10):
		start = time.time()
		for i in range(int(float(timeout) / interval)+1):
			if time.time()-start > timeout:
				break
			v = check()
			if not (v is None):
				return v
			time.sleep(interval)
		raise TimeoutException( \
			'Wait.until timeout: %i, %i' % (interval,timeout))

class Act:
	@staticmethod
	def click(z,n):
		print('clicking',n)
		z.execute_script('arguments[0].click()',n)
		return n
	@staticmethod
	def focus(z,n):
		z.execute_script('arguments[0].focus()',n)
		return n
	@staticmethod
	def value(z,n):
		return z.execute_script('arguments[0].value',n)
	@staticmethod
	def repeat(f,interval=.1,count=10):
		err = None
		for i in range(count):
			try:
				return f()
			except Exception as e:
				err = e
			time.sleep(interval)
		raise err

class qtable:
	_driver = None
	_table = {}
	
	def __init__(self,driver,table={},**kw):
		self._driver = driver
		self.add(table,**kw)
	
	def __getitem__(self,k):
		return getattr(self,k)
	
	def __setitem__(self,k,v):
		return setattr(self,k,v)
	
	def __getattr__(self,k):
		if not (k in self._table):
			raise AttributeError('(%s) not found in table:\n%s' % (
				k,
				'\n'.join(self._table.keys())
			))
		q = self._table[k]
		if k == 'query':
			return q
		if isinstance(q,Query.All):
			try:
				#return self._driver.find_elements_by_css_selector(q)
				return self._driver.find_elements(By.CSS_SELECTOR,q)
			except NoSuchElementException:
				return None
		elif isinstance(q,Query.Script):
			script = Query.Script.format(q)
			return self._driver.execute_script(script)
		else:
			try:
				#return self._driver.find_element_by_css_selector(q)
				return self._driver.find_element(By.CSS_SELECTOR,q)
			except NoSuchElementException:
				return None
	
	def __setattr__(self,k,v):
		#print('setattr',k,v)
		if not self._ownattr(k):
			return super().__setattr__(k,v)
		n = self[k]
		if isinstance(n,WebElement):
			self._driver.execute_script('arguments[0].value = arguments[1]',n,v)
		else:
			raise AttributeError()
	
	def _ownattr(self,k):
		return (k in self._table) or k == 'query'
	
	def add(self,table={},**kw):
		for k,v in table.items():
			self._table[k] = v
		for k,v in kw.items():
			self._table[k] = v


