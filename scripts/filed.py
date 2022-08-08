#!/usr/bin/env python
import math

def maxK(lista,K):
 valorMax = max(lista)
 listaL=[]
 for x in lista:
  listaL = listaL+[x-valorMax]
 valor = 0
 for x in listaL:
  valor=valor+math.exp(K*x)
 valor = valorMax+(1/K)*math.log(valor)
 return valor

def minK(lista,K):
 valorMin = min(lista)
 listaL=[]
 for x in lista:
  listaL = listaL+[x-valorMin]
 valor = 0
 for x in listaL:
  valor=valor+math.exp(-K*x)
 valor = valorMin-(1/K)*math.log(valor)
 return valor 

#Function H normal
def Hnormal(A0,A1,B0,B1,C,K,r,z):
  D0 = (A0-B0)*C 
  D1 = (A1-B1)*C
  U1 = (z/r-A0)/A1
  U2 = (z-(B0*r+D0))/(B1*r+D1)
  U3 = z
  return maxK([U1,U2,U3],K) 

#Function H shallow
def Hshallow(A0,A1,B0,B1,C,K,r,z):
  rKC = maxK([r,C],K)
  D0 = (A0-B0)*C 
  D1 = (A1-B1)*C 
  U1 = (z/r-A0)/A1
  U2 = (z-(B0*rKC+D0))/(B1*rKC+D1)
  U3 = z
  return maxK([minK([U1,U2],K),U3],K) 

#Field normal
def VFnorlmal(A0,A1,B0,B1,C,K,x,y,z):
  r=math.sqrt(x**2+y**2)
  delta=0.01
  H = Hnormal(A0,A1,B0,B1,C,K,r,z)
  pHpr = (Hnormal(A0,A1,B0,B1,C,K,r+delta,z)-H)/delta
  pHpz = (Hnormal(A0,A1,B0,B1,C,K,r,z+delta)-H)/delta
  a = alpha(x, y, z)
  Vx =  -x*a*pHpz
  Vy =  -y*a*pHpz
  Vz =   r*pHpr
  return [Vx,Vy,Vz]

#Field shallow 
def VFshallow(A0,A1,B0,B1,C,K,x,y,z):
  r=math.sqrt(x**2+y**2)
  delta=0.01
  H = Hshallow(A0,A1,B0,B1,C,K,r,z)
  pHpr = (Hshallow(A0,A1,B0,B1,C,K,r+delta,z)-H)/delta
  pHpz = (Hshallow(A0,A1,B0,B1,C,K,r,z+delta)-H)/delta
  a = alpha(x, y, z)
  Vx =  -x*a*pHpz
  Vy =  -y*a*pHpz
  Vz =   r*a*pHpr
  return [Vx,Vy,Vz]
