import os
#from ij.io import DirectoryChooser

def run(self):
    # run on its own:
    dc = DirectoryChooser("Select Exported Sections Folder")
    dc.setDefaultDirectory("/Volumes/Experiments/NickForrest/2011_0426 J1/AT/R12/exported-sessions/test")
    layoutfiles = convert_metadata_dir(dc.getDirectory())
    print layoutfiles



def get_freeframe_pix_coords(metafiles,rescale=1.000):#,scale=0.099937):

        coord_list=[]
        metadata_list = []
        for metafile in metafiles:
          #read the metadata and pixel coordinates from each metadata file
          #print 'metafile', metafile
          #[metadata,norm_coords]=get_section_metadata(os.path.join(dir, metafile),normalize=True,rescale=rescale)
          [metadata,coords]=get_section_metadata(os.path.join(dir, metafile), normalize = False, px_scale = False, rescale = 1.0)
          #append the pixel coordinates to a list
          #print 'coords',coords
          coord_list.append(coords[0])
          metadata_list.append(metadata)

        #normalize: subtract the coordinates of the first tile from all the tiles (the first tile becomes [0, 0])
        norm_coords = []
        first_coord=coord_list[0]
        for coord in coord_list: 
            norm_coords.append([coord[0]-first_coord[0],coord[1]-first_coord[1]])
            

        #scale: divide micrometer measurement by microns/px scale
        (channel, width, height, mosaic_x, mosaic_y, scale_x, scale_y, exposure) = metadata_list[0][1].split()
        scale = [float(scale_x)*rescale, float(scale_y)*rescale]

        
        px_norm_coords = []
        for coord in norm_coords:
            px_norm_coord = [coord[0]/scale[0], coord[1]/scale[1]]
            px_norm_coords.append(px_norm_coord)
    
        print 'px_norm_coords', px_norm_coords
        #layout_suffix = "_TileLayout.txt"
        #write a layout file for this section based upon the list of tiles and list of pixel coordinates
        #layout_file = write_layout(os.path.join(dir, sect+layout_suffix), tiles, px_norm_coords)
        #layout_files.append(layout_file)
        
        return (metadata_list,px_norm_coords)

def convert_metadata_dir_freeframe(dir,rescale=1.000):#,scale=0.099937):
    #get a list of all the metadata files in the directory
    sections=set()
    for filename in os.listdir(dir):
        if "_metadata.txt" in filename:
            #find the name of the sections associated with each metadata file,
            #given the naming convention from zviunpackall_freeframe of 
            #metafilename = "%s-S%03d_F%03d_metadata.txt" %(self.channeldict[channels[i]], sectionnumber,framenumber)
            [sectionname,underF,junk]=filename.rpartition("_F")
            #group the results so you have a list of the unique sections represented in this directory    
            if sectionname not in sections:
                sections.add(sectionname)
    
    layout_files=[]
    #loop through each of the section names (random order, I guess)
    for sect in sections:
        #list the tiles associated with this section
        tiles=[file for file in os.listdir(dir) if (sect in file and '_metadata' not in file and '.tif' in file)]
        #tiles.sort()
        metafiles=[file for file in os.listdir(dir) if (sect in file and '_metadata.txt' in file)]
        #metafiles.sort()
        #loop through those tiles
        coord_list=[]
        metadata_list = []
        for metafile in metafiles:
            #read the metadata and pixel coordinates from each metadata file
            print 'metafile', metafile
            #[metadata,norm_coords]=get_section_metadata(os.path.join(dir, metafile),normalize=True,rescale=rescale)
            [metadata,coords]=get_section_metadata(os.path.join(dir, metafile), normalize = False, px_scale = False, rescale = 1.0)
            #append the pixel coordinates to a list
            #print 'coords',coords
            coord_list.append(coords[0])
            metadata_list.append(metadata)

        #normalize: subtract the coordinates of the first tile from all the tiles (the first tile becomes [0, 0])
        norm_coords = []
        first_coord=coord_list[0]
        for coord in coord_list: 
            norm_coords.append([coord[0]-first_coord[0],coord[1]-first_coord[1]])
        #print 'norm_coords', norm_coords
        
        #scale: divide micrometer measurement by microns/px scale
        (channel, width, height, mosaic_x, mosaic_y, scale_x, scale_y, exposure) = metadata_list[0][1].split()
        scale = [float(scale_x)*rescale, float(scale_y)*rescale]
        #print 'scale', scale
        
        px_norm_coords = []
        for coord in norm_coords:
            px_norm_coord = [coord[0]/scale[0], coord[1]/scale[1]]
            px_norm_coords.append(px_norm_coord)
        
        #print 'px_norm_coords', px_norm_coords
        layout_suffix = "_TileLayout.txt"
        #write a layout file for this section based upon the list of tiles and list of pixel coordinates
        layout_file = write_layout(os.path.join(dir, sect+layout_suffix), tiles, px_norm_coords)
        layout_files.append(layout_file)
        
    return layout_files
 
def convert_metadata_dir (dir,rescale=1.000):
    
    # metafile_names: list of section-metafile names
    #metafile_names = [file for file in os.listdir(dir) if "_metadata.txt" in file]
    #layoutfiles = []
    #for filename in metafile_names:
    #    layout_file = convert_metadata_file(os.path.join(dir, filename), get_tiles(dir, filename))
    #    layoutfiles.append(os.path.join(dir, layout_file))
        
    return [convert_metadata_file(os.path.join(dir, filename), get_tiles(dir, filename),rescale=rescale) for filename in os.listdir(dir) if "_metadata.txt" in filename]
        
        
def get_tiles(dir, metafile_name):
    return [file for file in os.listdir(dir) if get_section_name(metafile_name)+'_tile-' in file]
        
        
def get_section_name(metafile_name):
    return metafile_name[:metafile_name.find("_metadata.txt")]

def get_section_metadata(metafile,normalize=True,px_scale = True, rescale=1.000):
    # get data from section metadata file
    # this function can return raw coordinates for later processing,
    # or automatically normalize (ie. relative to tile 1) 
    # and/or scale (ie. in pixels rather than microns) the coordinates before return
    
    try:
        f = open(metafile, 'r')
    except IOError:
        print "Could not open meta-data file: %s" %metafile
        return None
    metadata = f.readlines()
    f.close()
    
    #print "Extracting metadata from %s\n\t%s\n\t%s" %(metafile, metadata[0].split(), metadata[1].split())
    (channel, width, height, mosaic_x, mosaic_y, scale_x, scale_y, exposure) = metadata[1].split()
    
    # tile_coords is a list of tile coordinates [x, y] for each tile in the order they are read from the metafile
    # NB: not including z/focus
    tile_coords = []
    for i in range(3,len(metadata)):
        tile_coords.append(metadata[i].split()[:2])
        
    #if normalizing subtract the coordinates of the first tile from all the tiles (the first tile becomes [0, 0])
    # NB: coords is strings, but norm_coords is floats
    norm_coords = []
    offset_coord = None
    for coord in tile_coords:
        if offset_coord is None:
            # normalize all coords by first
            offset_coord = coord
        # this is the equivalent of matrix arithmetic
        if normalize:
            norm_coords.append([float(coord[i])-float(offset_coord[i]) for i in range(len(coord))])
        else:
            norm_coords.append([float(coord[i]) for i in range(len(coord))])
 
    if px_scale == True:
        # px_norm_coords transforms norm_coords to pixel coordinates
        px_norm_coords= []
        scale = [float(scale_x)*rescale, float(scale_y)*rescale]
        for coord in norm_coords:
            px_norm_coord = [coord[0]/scale[0], coord[1]/scale[1]]
            px_norm_coords.append(px_norm_coord)
    
        #print tile_coords
        #print norm_coords
        #print 'px_norm_coords', px_norm_coords
        
        return (metadata, px_norm_coords)
    
    else:
        #print 'norm_coords', norm_coords
        return (metadata, norm_coords)


def write_layout(layout_file, tiles, px_norm_coords):
    
    layout_preamble = "# Define the number of dimensions we are working on\ndim = 2\n\n# Define the image coordinates\n"
    (dir, layout_filename) = os.path.split(layout_file)
    try:
        f = open (layout_file, 'w')
    except IOError:
        print "Could not write to layout file: %s" %layout_file
        return None
    f.write(layout_preamble)
    print "layout writing"
    print tiles
    print px_norm_coords
    
    for i in range(len(tiles)):
        f.write("%s; ; (%s, %s)\n" %(os.path.join(dir, tiles[i]), px_norm_coords[i][0], px_norm_coords[i][1]))
    
    f.close()
    return layout_file


def convert_metadata_file(metafile, tiles,rescale=1.000):
    #takes metadata file path and list of tile images and returns layout file path
    
    layout_suffix = "_TileLayout.txt"
    (dir, metafile_name) = os.path.split(metafile)
    section_name = get_section_name(metafile_name)

    (metadata, px_norm_coords) = get_section_metadata(metafile,rescale)
    
    # output to TileLayout File
    print "Writing layout file %s in dir %s" %(section_name+layout_suffix, dir)
    layout_file = write_layout(os.path.join(dir, section_name+layout_suffix), tiles, px_norm_coords)
    return layout_file
