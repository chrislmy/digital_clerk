class MockUserProfile:
	def studentProfile1(self):
		return {
			'upi':'1',
			'status':'Student'
		}

	def studentProfile2(self):
		return {
			'upi':'4',
			'status':'Student'
		}

	def lecturerProfile(self):
		return {
			'upi':'2',
			'status':'Lecturer'
		}

	def assistantProfile(self):
		return {
			'upi':'3',
			'status':'Assistant'
		}
	def getNameFromId(self,id):
		if id == 1:
			return 'Christopher Lau'
		elif id == 2:
			return 'Tony Hunter'
		elif id == 3:
			return 'Mike Smith'
		elif id == 4:
			return 'LiLy Collins'

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
