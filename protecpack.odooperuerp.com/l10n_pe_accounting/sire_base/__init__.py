from . import models

# Herramientas genericas
def getDateYYYYMM(date):
	if date:
		return '%s%s'%(date.split('-')[0],date.split('-')[1])
	else:
		return ''
def getDateYYYYMMDD(date):
	if date:
		return ''.join(date.split('-'))
	else:
		return ''