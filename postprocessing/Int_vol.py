# integration over a volume
# example computing the core mass

# coding: utf-8

from ester import *
from numpy import *
import argparse
import os

def main():
      a=star2d(os.path.abspath(ARGS.model))
      nc=a.conv
      print('nb of domains in the core',nc)

      # f is the quantity to integrate over the volume
      f=a.rho*a.r**2*a.rz

      ncore=sum(a.npts[0:nc])

      # Integrateur radial: I(1,nr)
      b=a.I.ravel() # 2D array with 1 column ==> 1D array
      Icheb=b[:ncore]

      dml=[]
      # We first integrate over theta on every radial grid point
      for  i in range(ncore):
            dm=dot(a.It,f[i,:])
            dml.append(dm)

      dma=2*pi*array(dml)
      # Then we integrate over 'r' on the first ncore grid points
      M=dot(dma,Icheb)


      rhoc=a.rhoc
      R=a.R
      Mcore=M*rhoc*R**3/M_SUN
      print('M core = %6.5f'%Mcore,' M sun')

def get_args():
      parser = argparse.ArgumentParser()
      parser.add_argument(
      "model",
      type=str,
      help="the path to the folder containing ESTER model",
      )

      return parser.parse_args()

if __name__ == '__main__':
      ARGS = get_args()
      main()
