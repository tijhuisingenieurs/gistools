e = '22'
e = int(e)
print e

print '33' in [1,2,33]



e = '22'
e = float(e)
print e

e = '22.4'
e = float(e)
print e

e = '2.2.3'
try:
    e = float(e)
except: print e

e = ''
try:
    e = float(e)
except: print e