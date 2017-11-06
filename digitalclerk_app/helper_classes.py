class MockUserProfile:
	@staticmethod
	def studentProfile():
		return {
			'upi':'1',
			'first_name':'Christopher',
			'last_name':'Lau',
			'status':'Student'
		}

	def lecturerProfile():
		return {
			'upi':'2',
			'first_name':'Tony',
			'last_name':'Hunter',
			'status':'Lecturer'
		}

	def assistantProfile():
		return {
			'upi':'3',
			'first_name':'Mike',
			'last_name':'Smith',
			'status':'Assistant'
		}

class MockModules:
	@staticmethod
	def listModules():
		return [{
			'code': 'COMP101P',
			'name': 'Principles of Programming'
		},
		{
			'code': 'COMP206P',
			'name': 'Maths and Stats'
		},
		{
			'code': 'COMP3096',
			'name': 'Artificial Intelligence and neural computing'
		},
		{
			'code': 'COMP310P',
			'name': 'Networked Systems'
		},
		{
			'code': 'COMP311P',
			'name': 'Internet of Things'
		}]
