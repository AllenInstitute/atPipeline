
package at_modules;

import ij.ImagePlus;
import ij.process.ImageProcessor;
import ij.IJ;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.Writer;
import java.io.File;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.lang.StringBuilder;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;
import java.util.Collection;
import java.lang.Math;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import java.awt.AlphaComposite;
import java.awt.Graphics;
import java.awt.*;
import java.net.URI;
import java.net.URISyntaxException;
import mpicbg.imagefeatures.Feature;
import mpicbg.imagefeatures.FloatArray2DSIFT;
import mpicbg.ij.SIFT;
import mpicbg.models.CoordinateTransform;
import mpicbg.models.CoordinateTransformList;
import mpicbg.models.InterpolatedCoordinateTransform;
import mpicbg.models.AffineModel2D;
import mpicbg.models.TranslationModel2D;
import mpicbg.models.InvertibleBoundable;
import mpicbg.models.CoordinateTransformMesh;
import mpicbg.ij.TransformMeshMapping;
import ij.process.ImageStatistics;
import ij.measure.Calibration;
import ij.measure.Measurements;
import ij.plugin.ContrastEnhancer;
import ij.io.FileSaver;
import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;
import net.imglib2.img.Img;
import net.imglib2.img.array.ArrayImgFactory;
import net.imglib2.type.numeric.real.FloatType;
import net.imglib2.type.numeric.integer.UnsignedShortType;
import net.imglib2.type.numeric.integer.UnsignedByteType;
import mpicbg.stitching.fusion.Fusion;
import mpicbg.stitching.ImageCollectionElement;
import mpicbg.stitching.StitchingParameters;
import mpicbg.stitching.ImagePlusTimePoint;
import java.util.HashMap;
import java.util.Map;
import java.util.*;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import org.janelia.alignment.spec.*;
import org.janelia.alignment.json.JsonUtils;
import org.janelia.alignment.spec.TileSpec;
import org.janelia.alignment.spec.LeafTransformSpec;
import org.janelia.alignment.spec.ReferenceTransformSpec;
import org.janelia.alignment.spec.ListTransformSpec;
import org.janelia.alignment.*;
import org.janelia.alignment.util.*;
import org.janelia.render.client.RenderDataClient;
import org.janelia.render.client.RenderDataClientParameters;
import org.janelia.render.client.FileUtil;
import org.janelia.render.client.TilePairClient;
import org.janelia.render.client.ImportJsonClient;
import org.janelia.alignment.spec.stack.StackMetaData.StackState;
import org.janelia.alignment.spec.stack.StackMetaData;
import org.janelia.alignment.spec.stack.StackVersion;
import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;

/**
 *
 * @author Sharmishtaa Seshamani
 */
public class StitchImagesByCC
{
	@Parameters
	static private class Params
	{


				@Parameter( names = "--baseDataUrl", description = "Render base data url", required = false )
				public String baseDataUrl = null;

				@Parameter( names = "--owner", description = "Render owner", required = false )
				public String owner = null;

				@Parameter( names = "--project", description = "Render project", required = false )
				public String project = null;

				@Parameter( names = "--input_json", description = "Input Json", required = true )
				private String input_json = null;

				@Parameter( names = "--stack", description = "Input Stack", required = false )
				public String stack = null;

				@Parameter( names = "--outputStack", description = "Input Stack", required = false )
				public String outputStack = null;

				@Parameter( names = "--section", description = "Section z value", required = false )
				private Double section = 100.0;

				@Parameter( names = "--help", description = "Display this note", help = true )
        private final boolean help = false;

        @Parameter( names = "--imageFiles", description = "path to image files", required = false )
        private List<String> files;

        @Parameter( names = "--outputLayout", description = "path to save the layout file for these frames", required = false )
        private String outputLayout = null;

        @Parameter( names = "--outputImage", description = "Path to save image file", required = false )
        public String outputImage = null;

        @Parameter( names = "--outputtilespec", description = "Path to save Json file", required = false )
        public String outputtilespec = null;

        @Parameter( names = "--outputtransformspec", description = "Path to save Json file", required = false )
        public String outputtransformspec = null;

        @Parameter( names = "--addChannel", description = "Channel to add", required = false )
        public List<String> addChannel = null;

        @Parameter( names = "--channelWeights", description = "Weights of channels to add", required = false )
        public List<Float> channelWeights = null;

        @Parameter( names = "--inputtilespec", description = "Json file containing tile specs", required = false)
        public String inputtilespec = null;

	}

	private StitchImagesByCC() {}

	public static ArrayList<ImagePlus> read_images(List<String> filepaths)
	{
	    	ArrayList<ImagePlus> images = new ArrayList();

		    for ( final String filepath : filepaths )
		    {
		        ImagePlus img = IJ.openImage(filepath);
		        images.add(img);
		    }
		    return images;
	}


	public static ImagePlus generateImageForZ(RenderDataClient renderDataClient,  String stack, Double scale, TileSpec t)
					throws Exception {

				t.deriveBoundingBox(t.getMeshCellSize(), true);
				TileBounds layerBounds = new TileBounds(t.getTileId(), t.getLayout().getSectionId(),t.getZ(), t.getMinX(), t.getMinY(), t.getMaxX(), t.getMaxY());
				Double z = t.getZ();
				final String parametersUrl =
								renderDataClient.getRenderParametersUrlString(stack,
																															layerBounds.getMinX(),
																															layerBounds.getMinY(),
																															z,
																															(int) (layerBounds.getDeltaX() + 0.5),
																															(int) (layerBounds.getDeltaY() + 0.5),
																															scale);

				final RenderParameters renderParameters = RenderParameters.loadFromUrl(parametersUrl);
				renderParameters.setDoFilter(false);

				final BufferedImage sectionImage = renderParameters.openTargetImage();

				// set cache size to 50MB so that masks get cached but most of RAM is left for target image
				final int maxCachedPixels = 50 * 1000000;
				final ImageProcessorCache imageProcessorCache;
				imageProcessorCache = new ImageProcessorCache(maxCachedPixels, false, false);
				Render.render(renderParameters, sectionImage, imageProcessorCache);

				String fullfilename = t.getFirstMipmapEntry().getValue().getImageFilePath();
				String delims = "[/]";
				String[] tokens = fullfilename.split(delims);
				ImagePlus I = new ImagePlus(tokens[tokens.length-1], sectionImage);

				return I;
	}

	public static ArrayList<ImagePlus> read_images(RenderDataClient r, String stack, ResolvedTileSpecCollection tileSpecs)
	{
		    ArrayList<ImagePlus> images = new ArrayList();
				Collection c = tileSpecs.getTileSpecs();
	      Iterator<TileSpec> itr = c.iterator();
	      while (itr.hasNext())
	      {
	        TileSpec t = (TileSpec)itr.next();
					ImagePlus img = new ImagePlus();
					try
					{
							img = generateImageForZ(r, stack, 1.0,t);
					}
					catch ( final Exception e )
					{
							e.printStackTrace();
					}
					images.add(img);
	      }
		    return images;
	}

	public static void calculatediffs(ArrayList<ImageCollectionElement> elements, ArrayList<ImagePlus> imagesR, ArrayList<ImagePlus> images, Map<String,Integer> connects, Map<String,Integer> filehash, Map<String,Integer> rawelementshash, ArrayList <ImagePlusTimePoint> originaloptimized, ArrayList <ImagePlusTimePoint> optimized,ArrayList <InvertibleBoundable> models, Params params, StitchingParameters stitchparams, ArrayList<Float> rawx, ArrayList<Float> rawy)
	{
				Integer i = 0;
				Integer j = 0;
				Integer r = rawelementshash.get(originaloptimized.get(0).getImagePlus().getTitle()); //reference element
				ImagePlusTimePoint imtref = originaloptimized.get(0);
				TranslationModel2D modref = (TranslationModel2D)imtref.getModel();
				Integer k = 0;
				double[] pt = new double[ 2 ]; pt[0] = 0; pt[1] = 0;
				double[] tr = new double[2]; tr[0] = 0; tr[1] = 0;
				double[] raw = new double[2];

				// Calculate diffs for debugging and force images that the optimization throws out to come back
				ArrayList<Double> diffs = new ArrayList();

		    try
				{
		    		String newLine = System.getProperty("line.separator");
		    		while (i < imagesR.size())
		    		{
							ImagePlus ip = 	imagesR.get(i);
							images.add(ip);
							if (connects.containsKey( ip.getTitle() ))
							{
								j = filehash.get(ip.getTitle());
								ImagePlusTimePoint imt = originaloptimized.get(j);
								optimized.add(imt);
				        models.add((InvertibleBoundable) imt.getModel());
				        //check for difference
				        k = rawelementshash.get(ip.getTitle());
			          raw[0] = rawx.get(k) - rawx.get(r);
			          raw[1] = rawy.get(k) - rawy.get(r);
			          TranslationModel2D mod = (TranslationModel2D)imt.getModel();
			          tr = mod.apply(pt);
			          double diffx = (tr[0]-raw[0])*(tr[0]-raw[0]);
			          double diffy = (tr[1]-raw[1])*(tr[1]-raw[1]);
			          double diff = Math.sqrt(diffx+diffy);
								diffs.add(diff);
							}

							else
							{
								ImageCollectionElement element= elements.get(i); // set it to anything
								k = rawelementshash.get(ip.getTitle());
								final ImagePlusTimePoint imt = new ImagePlusTimePoint( element.open( stitchparams.virtual ), element.getIndex(), 1, element.getModel(), element ); //initialize
								final TranslationModel2D model = (TranslationModel2D)imt.getModel();	// relate the model to the imt
								tr = modref.apply(pt);
								model.set( rawx.get(k)-rawx.get(r)+tr[0], rawy.get(k) -rawy.get(r)+tr[1]);
								optimized.add(imt);
					        	models.add((InvertibleBoundable) imt.getModel());
								diffs.add(-1.0);
							}
							i++;
		    		}//end while

				}//end try

		    catch(Exception e)
		    {
		    		e.printStackTrace();
		    }
	}

	public static void adjustmodels_nonnegative(ArrayList<TranslationModel2D> translation_models)
	{
				double minx = 0.0f;
				double miny = 0.0f;
				ArrayList<Double> tx = new ArrayList();
				ArrayList<Double> ty = new ArrayList();

				for (int i = 0; i < translation_models.size(); i++)
				{
					double [] l = {0,0};
					translation_models.get(i).applyInPlace(l);
					tx.add(l[0]);
					ty.add(l[1]);
					if (l[0] < minx)
						minx = l[0];
					if (l[1] < miny)
						miny = l[1];
				}

				for (int i = 0; i < translation_models.size(); i++)
					translation_models.get(i).set(tx.get(i)-minx, ty.get(i)-miny);

	}

	public static List<TileSpec> settilespecs(ResolvedTileSpecCollection r)
	{
				List<TileSpec> ts =new ArrayList() ;
				Collection c = r.getTileSpecs();
				Iterator<TileSpec> itr = c.iterator();
				while (itr.hasNext())
				{
					TileSpec t = (TileSpec)itr.next();
					ts.add(t);
				}
				return ts;
	}


	public static void ensureStackExists(final RenderDataClient renderDataClient,
																			 final String acquireStackName,
																			 final StackMetaData acquisition) throws Exception {
			StackMetaData stackMetaData;
			try
			{
					stackMetaData = renderDataClient.getStackMetaData(acquireStackName);
			}
			catch (final Throwable t)
			{

					List<Double> l = acquisition.getCurrentResolutionValues();
					renderDataClient.saveStackVersion(acquireStackName,
																								new StackVersion(new Date(),
																																 null,
																																 null,
																																 null,
																																 l.get(0),
																																 l.get(1),
																																 l.get(2),
																																 null,
																																 null));

					stackMetaData = renderDataClient.getStackMetaData(acquireStackName);
			}

	}


	public  static ResolvedTileSpecCollection outputtotilespec(ArrayList<ImagePlus> imagesR, ArrayList<TranslationModel2D> translation_models, Map<String,Integer> rawelementshash, List<TileSpec> tileSpecs,Params params)
	{


				List<TransformSpec> transformlist = new ArrayList();

				for (int w = 0; w < imagesR.size(); w++)
        {
      		String fname = imagesR.get(w).getTitle();
      		Integer p = rawelementshash.get(fname);
      		double [] l = {0,0};
      		TranslationModel2D mod = translation_models.get(w); //translation_models.get(w);
      		mod.applyInPlace(l);
      		LeafTransformSpec lts = (LeafTransformSpec)tileSpecs.get(p).getLastTransform();
      		String olddatastring = lts.getDataString();
      		String [] op = lts.getDataString().split(" ");
      		op[4] = Double.toString(l[0]); op[5] = Double.toString(l[1]);
      		String newdatastring = "";
      		for (int q = 0; q < op.length; q++)
      			newdatastring = newdatastring + op[q] + " ";

      		// Add the transform with ID to transformspec and reference in tilespec

      		String id = "trans_"+ tileSpecs.get(p).getTileId().toString();
					final TransformSpecMetaData md = new TransformSpecMetaData();
					LeafTransformSpec newlts = new LeafTransformSpec(id,md,lts.getClassName(), newdatastring);
					transformlist.add(newlts);
      		ReferenceTransformSpec newreflts = new ReferenceTransformSpec(id);
      		ListTransformSpec mylist = new ListTransformSpec();
      		mylist.addSpec(newreflts);
      		//set the tilespec's transform to the new one
      		tileSpecs.get(p).setTransforms(mylist);
        }

        final ResolvedTileSpecCollection resTiles = new ResolvedTileSpecCollection(transformlist,tileSpecs);

				return resTiles;

	}

	public static ArrayList<String> readandsetinput(List<TileSpec> tileSpecs, ArrayList<ImageCollectionElement> elements,Map<String,Integer> rawelementshash, ArrayList<Float> rawx, ArrayList<Float> rawy )
	{
				//Input Files
        ArrayList<String> allfiles = new ArrayList<String> ();
        for (int i = 0; i < tileSpecs.size(); i++)
        {
	        	String fullfname = tileSpecs.get(i).getFirstMipmapEntry().getValue().getImageUrl().toString();
	        	int pos = fullfname.lastIndexOf("/");
	        	String filenameonly = fullfname.substring(pos+1);
	        	String [] fnames = fullfname.split(":");
	          File file = new File(fnames[1]);
	          ImageCollectionElement element=new ImageCollectionElement(file,i);
	        	element.setDimensionality( 2 );
	        	LeafTransformSpec lts = (LeafTransformSpec)tileSpecs.get(i).getLastTransform();
	        	String [] sltsparams = lts.getDataString().split(" ");
	        	float[] offsets = {Float.parseFloat(sltsparams[4]),Float.parseFloat(sltsparams[5])};
	        	element.setOffset(offsets);
	        	element.setModel(new TranslationModel2D() );
	        	elements.add(element);
	        	rawx.add(Float.parseFloat(sltsparams[4]));
	        	rawy.add(Float.parseFloat(sltsparams[5]));
	        	rawelementshash.put(filenameonly,i);
	        	allfiles.add(fnames[1]);
        }
        return allfiles;
	}


	public static ResolvedTileSpecCollection stitch_tilespecs(List<TileSpec> tileSpecs,ArrayList<ImagePlus> imagesR, Params params)
	{
				//Stitching Parameters
				StitchingParameters stitchparams=new StitchingParameters();
				stitchparams.dimensionality = 2;
				stitchparams.channel1 = 0;
				stitchparams.channel2 = 0;
				stitchparams.timeSelect = 0;
				stitchparams.checkPeaks = 5;
				stitchparams.regThreshold = 0.4f;
				stitchparams.computeOverlap = true;
				stitchparams.subpixelAccuracy = true;
				stitchparams.fusionMethod = 2;

				//raw element storage and initialization

				ArrayList<ImageCollectionElement> elements=new ArrayList();
				ArrayList<ImageCollectionElement> rawelements = new ArrayList();
				ArrayList<Float> rawx = new ArrayList();
				ArrayList<Float> rawy = new ArrayList();
				Map<String,Integer> rawelementshash = new HashMap<String,Integer> ();
				params.files= readandsetinput(tileSpecs, elements,rawelementshash,rawx,rawy);

				//registration
				ImageCollectionandHashContainer cont =new ImageCollectionandHashContainer();
				cont = CollectionStitchingImgLibCC.stitchCollectionandcalculateconnections( elements, stitchparams );
				ArrayList <ImagePlusTimePoint> originaloptimized = cont.getIPTPArray();
				Map<String,Integer> connects = cont.getconnections();
				ArrayList <ImagePlusTimePoint> optimized = new ArrayList();
				Map<String,Integer> filehash = new HashMap<String,Integer> ();

				//create hashes
				ArrayList<ImagePlus> images = new ArrayList<ImagePlus> ();
				ArrayList <InvertibleBoundable> models = new ArrayList();
				Integer i = 0, j = 0;
				while (i < originaloptimized.size())
				{
					connects.put(originaloptimized.get(i).getImagePlus().getTitle(),i);
					i++;
				}
				i = 0;
				while (i < imagesR.size())
				{
					if (connects.containsKey( imagesR.get(i).getTitle() ))
					{
						j = connects.get(imagesR.get(i).getTitle());
						filehash.put(imagesR.get(i).getTitle(), j);
					}
					i++;
				}

				calculatediffs(elements, imagesR, images, connects, filehash, rawelementshash, originaloptimized, optimized,models,params, stitchparams, rawx, rawy);

				// add translation models
				final ArrayList<TranslationModel2D> translation_models = new ArrayList();
				for (final InvertibleBoundable model : models)
				translation_models.add((TranslationModel2D) model);

				if (params.outputImage != null)
				{
						ImagePlus imp = Fusion.fuse(new UnsignedShortType(), imagesR, models, 2, true, 0,null, false, false, false);
						FileSaver fs = new FileSaver( imp );
						fs.saveAsTiff(params.outputImage);
				}

				adjustmodels_nonnegative(translation_models);
				ResolvedTileSpecCollection resTiles = outputtotilespec(imagesR, translation_models, rawelementshash, tileSpecs, params);
				return resTiles;
	}

	public static void stitch(Params params)
	{

				final RenderDataClient r ;
				r = new RenderDataClient(params.baseDataUrl,params.owner,params.project);
				ResolvedTileSpecCollection resTileSpecs = new ResolvedTileSpecCollection();

				try
				{
					resTileSpecs = r.getResolvedTiles(params.stack,params.section);
				}
				catch (Exception ex)
				{
					throw new RuntimeException(ex);
				}

				List<TileSpec> tileSpecs = settilespecs(resTileSpecs);
				ArrayList<ImagePlus> imagesR = read_images(r,params.stack,resTileSpecs);
				ResolvedTileSpecCollection resTiles = stitch_tilespecs(tileSpecs,imagesR,params);

				try
				{
		        final StackMetaData smd = r.getStackMetaData(params.stack);
		        ensureStackExists(r,params.outputStack,smd);
		        r.setStackState(params.outputStack,StackState.LOADING);
		        r.saveResolvedTiles(resTiles,params.outputStack,null);
		        r.setStackState(params.outputStack,StackState.COMPLETE);
				}
				catch ( final Exception e )
      	{
          	return;
      	}

	}

	public static void main( final String[] args )
	{

			  Params params = new Params();
				try
				{
						final JCommander jc = new JCommander( params, args );
				    if ( params.help )
				    {
				    		jc.usage();
				        return;
				   	}
			  }
       	catch ( final Exception e )
        {
        		e.printStackTrace();
           	final JCommander jc = new JCommander( params );
        		jc.setProgramName( "java [-options] -cp /home/sharmishtaas/allen_SB_code/render/render-app/target/render-app-0.3.0-SNAPSHOT-jar-with-dependencies.jar org.janelia.alignment.StitchImagesByCC" );
        		jc.usage();
        		return;
        }

				final Gson gson = new Gson();
		    try
				{
	     			params = gson.fromJson( new FileReader( params.input_json ), Params.class );
		    }
		    catch ( final Exception e )
		    {
		          return;
		    }

				stitch(params);


   	}
}
