'''
-------------------------------------------------------------------------------
Assignment-2
Vivek Dnyaneshwar Surwase (EE20B153)
-------------------------------------------------------------------------------
'''

from numpy import *                       # Importing 'numpy' library
from sys import argv, exit                # Importing argv,exit from 'sys' library

# A function created to convert exponents to real numbers.
def converter(string):
	'''This function converts exponents to real numbers. '''          # doc string
	c = string.split('e')
	val = (float(c[0]))*(10**int(c[1]))
	return val

# Classes are declaired for each component.
class Resistor:                                    # Class for resistor
	def __init__(self,name,n1,n2,value):
		self.name = name
		self.n1 = n2
		self.n2 = n1
		self.value = value

class Capacitor:                                   # Class for capacitor
	def __init__(self,name,n1,n2,value):
		self.name = name
		self.n1 = n2
		self.n2 = n1
		self.value = value

class Inductor:                                    # Class for inductor
	def __init__(self,name,n1,n2,value):
		self.name = name
		self.n1 = n2
		self.n2 = n1
		self.value = value

class VoltageSource:                               # Class for voltage source
	def __init__(self,name,n1,n2,value):
		self.name = name
		self.n1 = n2
		self.n2 = n1
		self.value = value		

class CurrentSource:                              # Class for current source
	def __init__(self,name,n1,n2,value):
		self.name = name
		self.n1 = n2
		self.n2 = n1
		self.value = value		


# The program will throw in an error if there isn't exactly 2 arguments in the commandline.
if len(argv)!=2:
	print("Invalid number of arguments! Pass the netlist file as the second argument.")
	exit()

CIRCUIT = ".circuit"                              # Increasing readability of code
END = ".end"
AC = ".ac"

try:

# Opening the file mentioned in the commandline as file object.
	with open(argv[1]) as f:
		lines = f.readlines()

# These are parameters to check the errors in the file format. 		
		start = -1
		start_check = -1
		end = -2
		end_check = -1
		ac = -1
		ac_check = -1

# The program will traverse through the file and take out only the required part.
		for line in lines:
			if CIRCUIT == line[:len(CIRCUIT)]:
				start = lines.index(line)
				start_check = 0

			elif END == line[:len(END)]:
				end = lines.index(line)
				end_check = 0
#This part is to check if the circuit has an AC or a DC source. 	
			elif AC == line[:len(AC)]:
				ac = lines.index(line)
				ac_check = 1

# The program will throw in an error if the circuit definition format is not proper.		
		if start >= end or start_check == -1 or end_check == -1:
			print("Invalid circuit definition...")
			exit()
	
		l = []
		k=0
# In case of an AC circuit, the required information is collected.		
		try:
			if ac_check ==1:
				_,ac_name,frequency = lines[ac].split("#")[0].split()
				frequency = 2*3.1415926*converter(frequency)

			for line in (lines[start+1:end]):
				name,n1,n2,*value = line.split("#")[0].split()

				if name[0] == 'R':
					object = Resistor(name,n1,n2,value)

				elif name[0] == 'C':
					object = Capacitor(name,n1,n2,value) 

				elif name[0] == 'L':
					object = Inductor(name,n1,n2,value)
					
				elif name[0] == 'V':
					object = VoltageSource(name,n1,n2,value)
					k = k+1

				elif name[0] == 'I':
					object = CurrentSource(name,n1,n2,value)

# Converting the values of the components into real numbers by using the converter() function.
				if len(object.value) == 1:
					if object.value[0].isdigit() == 0:	
						object.value = float(converter(object.value[0]))
					else:
						object.value = float(object.value[0])	

# In case of an AC source, the voltage and phase are assigned properly.
				else:
					object.value = (float(object.value[1])/2)*complex(cos(float(object.value[2])),sin(float(object.value[2])))			

				l.append(object)

		except IndexError:            # The program will throw an error if the netlist is not written properly.
			print("Please make sure the netlist is written properly.")	
			exit()

# Nodes are created using a dictionary.
	node ={}
	for object in l:
		if object.n1 not in node:
			if object.n1 == 'GND':
				node['n0'] = 'GND'

			else:	
				name = "n" + object.n1
				node[name] = int(object.n1)

		if object.n2 not in node:
			if object.n2 == 'GND': 
				node['n0'] = 'GND'

			else:	
				name = "n" + object.n2 	
				node[name] = int(object.n2)

	node['n0'] = 0			
	n = len(node)

# Creating the M and b matrices for solving the equations.
	M = zeros(((n+k-1),(n+k-1)),dtype="complex_")
	b = zeros(((n+k-1),1),dtype="complex_")
	p=0

# This part of code will fill the matrices M and b taking into consideration if it is an AC or a DC source.
	for object in l:

# In case of a resistor, the matrix M is filled in a certain way as shown below.		
		if object.name[0] == 'R':
			if object.n2 == 'GND': 
				M[int(object.n1)-1][int(object.n1)-1] += 1/object.value

			elif object.n1 == 'GND':
				M[int(object.n2)-1][int(object.n2)-1] += 1/object.value
					
			else:	
				M[int(object.n1)-1][int(object.n1)-1] += 1/object.value
				M[int(object.n2)-1][int(object.n2)-1] += 1/object.value
				M[int(object.n1)-1][int(object.n2)-1] += -1/object.value
				M[int(object.n2)-1][int(object.n1)-1] += -1/object.value

# In case of a capacitor, the impedance is calculated first and then the matrix M is filled.
		elif object.name[0] == 'C':
			if ac_check ==1:
				Xc = -1/(float(object.value)*frequency)
				object.value = complex(0,Xc)

			if object.n2 == 'GND': 
				M[int(object.n1)-1][int(object.n1)-1] += 1/object.value
			elif object.n1 == 'GND':
				M[int(object.n2)-1][int(object.n2)-1] += 1/object.value
					
			else:	
				M[int(object.n1)-1][int(object.n1)-1] += 1/object.value
				M[int(object.n2)-1][int(object.n2)-1] += 1/object.value
				M[int(object.n1)-1][int(object.n2)-1] += -1/object.value
				M[int(object.n2)-1][int(object.n1)-1] += -1/object.value

# In case of an inductor, the impedance is calculated first and then the matrix M is filled.
		elif object.name[0] == 'L':
			if ac_check ==1:
				Xl = (float(object.value)*frequency)
				object.value = complex(0,Xl)

			if object.n2 == 'GND': 
				M[int(object.n1)-1][int(object.n1)-1] += 1/object.value
			elif object.n1 == 'GND':
				M[int(object.n2)-1][int(object.n2)-1] += 1/object.value
					
			else:	
				M[int(object.n1)-1][int(object.n1)-1] += 1/object.value
				M[int(object.n2)-1][int(object.n2)-1] += 1/object.value
				M[int(object.n1)-1][int(object.n2)-1] += -1/object.value
				M[int(object.n2)-1][int(object.n1)-1] += -1/object.value

# In case of a current source, the matrix b is filled as shown.
		elif object.name[0] == 'I':
			if object.n2 == 'GND':
				b[int(object.n1)-1][0] += object.value

			elif object.n1 == 'GND':
				b[int(object.n2)-1][0] += -object.value

			else:
				b[int(object.n1)-1][0] += object.value
				b[int(object.n2)-1][0] += -object.value

# In case of a voltage source, the matrices M and b are filled as shown.
		elif object.name[0] == 'V':
			if object.n2 == 'GND':
				M[int(object.n1)-1][n-1+p] += 1
				M[n-1+p][int(object.n1)-1] += 1
				b[n-1+p] += object.value
				p = p+1			
			elif object.n1 == 'GND':
				M[int(object.n2)-1][n-1+p] += -1
				M[n-1+p][int(object.n2)-1] += -1
				b[n-1+p] += object.value
				p = p+1			
			else:	
				M[int(object.n1)-1][n-1+p] += 1
				M[int(object.n2)-1][n-1+p] += -1
				M[n-1+p][int(object.n1)-1] += 1
				M[n-1+p][int(object.n2)-1] += -1
				b[n-1+p] += object.value
				p = p+1

# The linalg.solve() function is used to solve the circuit equations.
	V = linalg.solve(M,b)

	print(V,"\n")			

	for i in range(n-1):
		print("V",i+1,"=",V[i],"\n")
	for j in range(k):
		print("I",j+1,"=",V[j+n-1],"\n")

# The program will throw in this error if the name of the netlist file is not proper 
# or if the netlist file is not found in the same directory as the program.

except FileNotFoundError:
	print("Invalid File.")
	exit()
