import meep as mp
import numpy as np
import matplotlib.pyplot as plt
import os
import h5py

class globalVariables():
    waveguideXSize = 60
    waveguideYSize = 60
    epsilonOfMaterial = 1
    epsilonOfBoundary = 1000
    blockXSize = 5
    blockYSize = 15
    numberOfSlitsForDiffractionGrating = 5
    diffractionGratingSlitSize = 6
    resolution = 10
    projectName = "diffractionSimulation"
    h5Name = "ez"
    imageStorageDirectory = projectName +'-out'

def generateDiffractionBlock(blockx,blocky):
    block = mp.Block(mp.Vector3(globalVariables.blockXSize,globalVariables.blockYSize,0),
             center=mp.Vector3(blockx,blocky,0),
             material=mp.Medium(epsilon=globalVariables.epsilonOfBoundary))
    return block

def createDiffractionSlit():
    cell = mp.Vector3(globalVariables.waveguideXSize, globalVariables.waveguideYSize, 0)

    geometry = [mp.Block(mp.Vector3(1e20, 1, 1e20),
                     center=mp.Vector3(0, 0),
                         material=mp.Medium(epsilon=globalVariables.epsilonOfMaterial)),
                mp.Block(mp.Vector3(globalVariables.blockXSize,globalVariables.blockYSize,0),
                         center=mp.Vector3(0,(globalVariables.blockYSize-globalVariables.waveguideYSize)/2.0,0),
                         material=mp.Medium(epsilon=globalVariables.epsilonOfBoundary)),
                mp.Block(mp.Vector3(globalVariables.blockXSize,globalVariables.blockYSize,0),
                         center=mp.Vector3(0,(globalVariables.waveguideYSize-globalVariables.blockYSize)/2.0,0),
                         material=mp.Medium(epsilon=globalVariables.epsilonOfBoundary))]


    sources = [mp.Source(mp.ContinuousSource(frequency=0.15),
                     component=mp.Ez,
                         center=mp.Vector3(-globalVariables.waveguideXSize/2+1,0,0))]

    pml_layers = [mp.PML(1.0)]

    return cell,geometry,sources,pml_layers

def diffractionGratingBlockSize():
    xSize  = globalVariables.blockXSize
    spaceLeftWithoutSlits = globalVariables.waveguideYSize-globalVariables.numberOfSlitsForDiffractionGrating*globalVariables.diffractionGratingSlitSize
    ySize = spaceLeftWithoutSlits/(globalVariables.numberOfSlitsForDiffractionGrating+1)
    return xSize , ySize

'''
Given the i^th block we want to find out what it's center will be
'''
def diffractionGratingBlockCenter(blockNumber):
    spaceLeftWithoutSlits = globalVariables.waveguideYSize-globalVariables.numberOfSlitsForDiffractionGrating*globalVariables.diffractionGratingSlitSize
    halfBlockSize = spaceLeftWithoutSlits/(2.0*(globalVariables.numberOfSlitsForDiffractionGrating+1))
    centerXValue = 0
    centerYValue = -0.5*globalVariables.waveguideYSize + halfBlockSize + globalVariables.diffractionGratingSlitSize*blockNumber + 2*halfBlockSize*blockNumber
    return centerXValue, centerYValue

def createDiffractionGrating():
    cell = mp.Vector3(globalVariables.waveguideXSize, globalVariables.waveguideYSize, 0)

    geometry = [mp.Block(mp.Vector3(1e20, 1, 1e20),
                     center=mp.Vector3(0, 0),
                         material=mp.Medium(epsilon=globalVariables.epsilonOfMaterial))]
    for i in range(globalVariables.numberOfSlitsForDiffractionGrating+1):
        centerXValue , centerYValue = diffractionGratingBlockCenter(i)
        #centerXValue = np.round(centerXValue)
        #centerYValue = np.round(centerYValue)
        blockXSize , blockYSize = diffractionGratingBlockSize()
        #blockXSize = np.round(blockXSize)
        #blockYSize = np.round(blockYSize)
        geometry.append(mp.Block(mp.Vector3(blockXSize,blockYSize,0),
                                 center=mp.Vector3(centerXValue,centerYValue,0),
                                 material=mp.Medium(epsilon=globalVariables.epsilonOfBoundary)))
    print(len(geometry),"THIS IS LEN GEOMEETRY")
    sources = [mp.Source(mp.ContinuousSource(frequency=0.15),
                     component=mp.Ez,
                         center=mp.Vector3(-globalVariables.waveguideXSize/2+1,0,0))]

    pml_layers = [mp.PML(1.0)]

    return cell,geometry,sources,pml_layers


def plot_data(sim,cell):
    eps_data = sim.get_array(center=mp.Vector3(), size=cell, component=mp.Dielectric)
    #plt.figure(dpi=100)
    #plt.imshow(eps_data.transpose(), interpolation='spline36', cmap='binary')
    #plt.axis('off')
    #plt.show()

    ez_data = sim.get_array(center=mp.Vector3(), size=cell, component=mp.Ez)
    plt.figure(dpi=100)
    plt.imshow(eps_data.transpose(), interpolation='spline36', cmap='binary')
    plt.imshow(ez_data.transpose(), interpolation='spline36', cmap='RdBu', alpha=0.9)
    plt.axis('off')
    plt.savefig("diffraction_grating.png")


def pngToGIF():
    gifCreationString = "convert " + globalVariables.imageStorageDirectory + "/" + globalVariables.projectName + "-" + globalVariables.h5Name + "-*.png " + globalVariables.imageStorageDirectory + "/" + globalVariables.projectName + ".gif"
    print(gifCreationString)
    os.system(gifCreationString)

def compressGIF(scalingFactor):
    print("Did I get here for GIF compression?")
    gifCompressionString = "gifsicle -O3 --colors=128 --scale=" + str(scalingFactor) + " -i " + globalVariables.imageStorageDirectory + "/" + globalVariables.projectName + ".gif" + " -o " + globalVariables.imageStorageDirectory + "/" + globalVariables.projectName + "compressed" + ".gif"
    print(gifCompressionString)
    os.system(gifCompressionString)

def countNumberOfPNG():
    pngCountString = "ls " + globalVariables.imageStorageDirectory + "/" + "*.png | wc -l"
    count = os.system(pngCountString)
    return int(count)

def deletePNG():
    print("Number of PNG Files in directory before is :" + str(countNumberOfPNG()))
    deletePNGString = "rm " + globalVariables.imageStorageDirectory + "/" + globalVariables.projectName + "*.png"
    os.system(deletePNGString)
    print("Number of PNG Files in directory after is :" + str(countNumberOfPNG()))

def deleteCompressedGIF():
    pass


'''
Creates a gif from the hdf5 file.
'''
def inPlaceGifCreation(compressGIFBool=True, compressGIFScale=0.5 ,deletePNGBool=True,generateGIF=True,deleteUncompressedGIF=False):
    pngToGIF()

    if(compressGIFBool==True):
        compressGIF(scalingFactor=compressGIFScale)

    if(deletePNGBool==True):
        deletePNG()


def removeH5Files():
    pass

if __name__=="__main__":
    #cell, geometry, sources, pml_layers = createDiffractionSlit()
    cell , geometry , sources , pml_layers = createDiffractionGrating()
    resolution = globalVariables.resolution
    sim = mp.Simulation(cell_size=cell,
                    boundary_layers=pml_layers,
                    geometry=geometry,
                    sources=sources,
                    resolution=resolution)
    sim.use_output_directory()
    #sim.run(mp.at_beginning(mp.output_epsilon),
       # mp.to_appended("ez", mp.at_every(0.6, mp.output_png(mp.Ez,"-Zc dkbluered"))),
       # until=200)
    sim.run(mp.at_every(0.6 , mp.output_png(mp.Ez, "-Zc dkbluered")), until=200)
    plot_data(sim,cell)
    inPlaceGifCreation()
