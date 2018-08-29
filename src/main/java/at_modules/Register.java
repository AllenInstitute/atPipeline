package at_modules;

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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Collection;
import java.lang.Math;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import java.awt.*;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.*;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.awt.geom.Rectangle2D;
import java.awt.Rectangle;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.FileSystems;
import java.lang.*;
import java.util.Collection;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import com.beust.jcommander.Parameters;

import net.imglib2.img.Img;
import net.imglib2.img.array.ArrayImgFactory;
//import net.imglib2.io.ImgIOException;
//import net.imglib2.io.ImgOpener;
//import net.imglib2.type.numeric.real.FloatType;
//import net.imglib2.type.numeric.RealType;
import net.imglib2.type.numeric.integer.UnsignedShortType;
//import net.imglib2.type.numeric.integer.UnsignedByteType;

import ij.ImagePlus;
import ij.process.ImageProcessor;
import ij.IJ;
import ij.process.ImageStatistics;
import ij.measure.Calibration;
import ij.measure.Measurements;
import ij.plugin.ContrastEnhancer;
import ij.io.FileSaver;
import ij.gui.Roi;
import ij.process.ImageConverter;


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
import mpicbg.stitching.fusion.Fusion;
import mpicbg.stitching.ImageCollectionElement;
import mpicbg.stitching.StitchingParameters;
import mpicbg.stitching.ImagePlusTimePoint;
import mpicbg.stitching.CollectionStitchingImgLib;
//import mpicbg.stitching.ImageCollectionandHashContainer;
import mpicbg.models.PointMatch;
import mpicbg.ij.FeatureTransform;
import mpicbg.models.AbstractModel;
import mpicbg.models.TranslationModel2D;
import mpicbg.models.AffineModel2D;
import mpicbg.models.SimilarityModel2D;
import mpicbg.models.RigidModel2D;
import mpicbg.models.HomographyModel2D;
import mpicbg.models.NotEnoughDataPointsException;
import mpicbg.stitching.PairWiseStitchingImgLib;
import mpicbg.stitching.PairWiseStitchingResult;
import mpicbg.imglib.algorithm.fft.PhaseCorrelation;
import mpicbg.imglib.algorithm.fft.PhaseCorrelationPeak;
import mpicbg.imglib.algorithm.scalespace.DifferenceOfGaussianPeak;
import mpicbg.imglib.algorithm.scalespace.SubpixelLocalization;
import mpicbg.imglib.type.numeric.integer.UnsignedByteType;
//import mpicbg.imglib.type.numeric.integer.UnsignedShortType;
import mpicbg.imglib.type.numeric.real.FloatType;
import mpicbg.imglib.image.Image;
import mpicbg.imglib.image.ImagePlusAdapter;
import mpicbg.imglib.type.numeric.RealType;
import mpicbg.stitching.Peak;

import org.janelia.alignment.*;
import org.janelia.alignment.json.*;
import org.janelia.alignment.spec.*;
import org.janelia.alignment.match.*;
import org.janelia.alignment.util.*;
import org.janelia.render.client.RenderDataClient;
//import org.janelia.render.client.RenderDataClientParameters;
//import org.janelia.render.client.FileUtil;
import org.janelia.render.client.TilePairClient;
import org.janelia.render.client.ImportJsonClient;
import org.janelia.alignment.spec.stack.StackMetaData.StackState;
import org.janelia.alignment.spec.stack.StackMetaData;
import org.janelia.alignment.spec.stack.StackVersion;


import org.json.simple.parser.JSONParser;
import org.json.simple.JSONObject;
import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;

public class Register
{

  @Parameters
	static private class Params
	{

		@Parameter( names = "--help", description = "Display this note", help = true )
        private final boolean help = false;

				//render parameters

				@Parameter( names = "--baseDataUrl", description = "Render base data url", required = false )
        public String baseDataUrl = null;

				@Parameter( names = "--owner", description = "Render owner", required = false )
        public String owner = null;

				@Parameter( names = "--project", description = "Render project", required = false )
        public String project = null;

				@Parameter( names = "--stack", description = "Input Stack", required = false )
        public String stack = null;

				@Parameter( names = "--referencestack", description = "Reference Stack", required = false )
        public String referencestack = null;

        @Parameter( names = "--outputStack", description = "Output Stack", required = false )
        public String outputStack = null;

				@Parameter( names = "--section", description = "Section z value", required = false )
        private Double section = 100.0;

        @Parameter( names = "--input_json", description = "Input Json", required = true )
        private String input_json = null;

        @Parameter( names = "--tileDistance", description = "Threshold of distance between overlapping tiles", required = false )
        private Double tileDistance = 5000.0;

				//file input params (old)

        /*@Parameter( names = "--outputJson", description = "Path to save Json file", required = false)
        public String outputJson = null;

        @Parameter( names = "--referencetilespec", description = "Json file containing tile specs", required = false)
        public String referencetilespec = null;

        @Parameter( names = "--inputtilespec", description = "Json file containing stitching estimates", required = false)
        public String inputtilespec = null;

        @Parameter( names = "--referencetransformspec", description = "Json file containing tile specs", required = false)
        public String referencetransformspec = null;

        @Parameter( names = "--inputtransformspec", description = "Json file containing tile specs", required = false)
        public String inputtransformspec = null;

        @Parameter( names = "--outputtilespec", description = "Json file containing stitching estimates", required = false)
        public String outputtilespec = null;*/



        //sift parameters
        @Parameter( names = "--initialSigma", description = "Initial Gaussian blur sigma", required = false )
        private float initialSigma = 1.6f;

        @Parameter( names = "--percentSaturated", description = "Percentage of pixels to saturate when normalizing contrast before extracting features", required = false )
        private float percentSaturated = 0.5f;

        @Parameter( names = "--steps", description = "Steps per scale octave", required = false )
        private int steps = 3;

        @Parameter( names = "--minOctaveSize", description = "Min image size", required = false )
        private int minOctaveSize = 64;

        @Parameter( names = "--maxOctaveSize", description = "Max image size", required = false )
        private int maxOctaveSize = 0;

        @Parameter( names = "--fdSize", description = "Feature descriptor size", required = false )
        private int fdSize = 8;

        @Parameter( names = "--fdBins", description = "Feature descriptor bins", required = false )
        private int fdBins = 8;

        @Parameter( names = "--contrastEnhance", description = "Flag for contrast enhancement", required = false )
        private boolean contrastEnhance = false;

        //matching parameters
        @Parameter( names = "--modelType", description = "type of model (0=translation,1=rigid,2=similarity,3=affine", required = false )
        public int modelType = 2;

        @Parameter( names = "--rod", description = "ROD", required = false )
        public float rod = 0.95f;

        @Parameter( names = "--minNumInliers", description = "Minimum number of inliers to output a model/inliers", required = false )
        public int minNumInliers = 10;

        @Parameter( names = "--maxEpsilon", description = "Maximum distance to consider a point an inlier after fitting transform", required = false )
        public float maxEpsilon = 2.5f;

        @Parameter( names = "--Niters", description = "max number of iterations for ransac", required = false )
        public int Niters = 1000;

        @Parameter( names = "--minInlierRatio", description = "minimum ratio of inliers/total features to consider it a fit", required = false )
        public float minInlierRatio = 0.0f;

        @Parameter( names = "--referenceID", description = "referenceID for transform that is computed", required = false)
        public String referenceID = null;


	}

  private Register() {}

    public static RigidModel2D calculateCC(ImagePlus img1, ImagePlus img2, RigidModel2D initmodel)
    {
      System.out.println("Now calculating CC.....");
      RigidModel2D model = new RigidModel2D();
      float [] offset = {0.0f, 0.0f};
      float maxvalue = 0;

      double [] array = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

      initmodel.toArray(array);
      double rot = Math.atan(array[2]/array[3]);
      ImageProcessor ip = img2.getProcessor();
      //ip.translate(array[4],array[5]);
      ip.rotate(rot);

      System.out.println(array.toString());
      System.out.println(rot);

      PairWiseStitchingResult p = computePhaseCorrelation(img1,img2,5,true);
      offset = p.getOffset();

      model.set(rot,  -1*offset[0], -1*offset[1]);
      return model;

    }



    public static AbstractModel<?> calculatetransform(List <TileSpec> reftileSpecs, List <TileSpec> inputtileSpecs, Params params, RigidModel2D initmodel, RenderDataClient r)
  	{

  		  //initialize

  		  AbstractModel<?> model;
  		  final List< Feature > inputfs = new ArrayList< Feature >();
    		final List< Feature > referencefs = new ArrayList< Feature >();
    		ArrayList <InvertibleBoundable> inputmodels = new ArrayList();
    		ArrayList <InvertibleBoundable> refmodels = new ArrayList();

        //extract features

      	ImagePlus inputImage = new ImagePlus();
      	ImagePlus refImage = new ImagePlus();

        inputImage = createSection(r,params.section,params.stack,inputtileSpecs);
        extractfeatures(inputImage, inputfs, params);

      	refImage = createSection(r,params.section,params.referencestack,reftileSpecs);
      	extractfeatures(refImage,referencefs, params);

        FileSaver f = new FileSaver(inputImage);
        f.saveAsTiff("/home/sharmishtaas/input.tif");

        FileSaver ff = new FileSaver(refImage);
        ff.saveAsTiff("/home/sharmishtaas/ref.tif");


    		//match
    		final List< PointMatch > candidates = new ArrayList< PointMatch >();
  		FeatureTransform.matchFeatures( inputfs,referencefs, candidates, params.rod );
  		ArrayList<PointMatch> inliers = new ArrayList< PointMatch >();
  		switch ( params.modelType )
  		{
  			case 0:
  				model = new TranslationModel2D();
  				break;
  			case 1:
  				model = new RigidModel2D();
  				break;
  			case 2:
  				model = new SimilarityModel2D();
  				break;
  			case 3:
  				model = new AffineModel2D();
  				break;
  			case 4:
  				model = new HomographyModel2D();
  				break;
  			default:
  				model = new RigidModel2D();
  				return model;
  		}
  	    boolean modelFound;
  		try
  		{
  			int numinliers = 0;
  			int numrounds = 0;
  			while (numinliers < 1  & numrounds < 3)
  			{
  					modelFound = model.filterRansac(
  							candidates,
  							inliers,
  							params.Niters,
  							params.maxEpsilon + numrounds*10,
  							params.minInlierRatio,
  							10 );
  					System.out.println("model found with " + inliers.size() + " inliers");
  					numinliers = inliers.size();
  					numrounds = numrounds + 1;
  			}
  		}
  		catch ( final NotEnoughDataPointsException e )
  		{
  		  System.out.println("no model found..");
  			modelFound = false;
  		}

  		//if (inliers.size() ==0)
  		//public static RigidModel2D createInverseModel(RigidModel2D initmodel)
  		//model = createInverseModel((RigidModel2D)model);
  		if (inliers.size() < 20)
  			model = calculateCC(inputImage, refImage, initmodel);

  		//check what the model has calculated
  		double [] initarray = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  		initmodel.toArray(initarray);
  		RigidModel2D newmodel = new RigidModel2D();
  		newmodel = (RigidModel2D)model;
  		double [] modelarray = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  		newmodel.toArray(modelarray);

  		System.out.println("Printing model and init model: ");
  		System.out.println(model2datastring(model));
  		System.out.println(model2datastring(initmodel));
  		//commented out by sharmi on may 2 2017, while running on santacruz data
  		if (Math.abs(initarray[4]-modelarray[4]) > 1000 || Math.abs(initarray[5]-modelarray[5]) > 1000) // if translation is too large, usually caused by dust particles...
  		{
  			model = initmodel;
  		}
      //model = initmodel;

  		System.out.println(modelarray[4]);
  		System.out.println(initarray[4]);
  		System.out.println(modelarray[5]);
  		System.out.println(initarray[5]);
  		System.out.println("final model: ");
  		System.out.println(model2datastring(model));

  		return model;

  	}



    public static AbstractModel<?> calculatetransform(ResolvedTileSpecCollection resolvedtileSpecsref, ResolvedTileSpecCollection resolvedtileSpecs,   Params params, RenderDataClient r)
  	{

      //scale for feature extraction
      int sc = 1;

      //inits
      AbstractModel<?> model = new TranslationModel2D();
  		final List< Feature > inputfs = new ArrayList< Feature >();
    	final List< Feature > referencefs = new ArrayList< Feature >();
    	ArrayList <InvertibleBoundable> inputmodels =new ArrayList();
    	ArrayList <InvertibleBoundable> refmodels = new ArrayList();

    	//read tilespecs
    	//ArrayList<String> inputfilenames = readandsetinput(resolvedtileSpecs);
    	//ArrayList<String> reffilenames = readandsetinput(resolvedtileSpecsref);
    	//ArrayList<ImagePlus> inputimages =  read_images(inputfilenames);
    	//ArrayList<ImagePlus> refimages =  read_images(reffilenames);


    	//extract features

    	ImagePlus inputImage = new ImagePlus();
    	ImagePlus refImage = new ImagePlus();

      Bounds refBounds = new Bounds();
      try
      {
        final StackMetaData smd = r.getStackMetaData(params.referencestack);
        refBounds = smd.getStats().getStackBounds();
      }
      catch(Exception e)
      {

        System.out.println("Cannot calculate stack bounds!");
      }
    	refImage = createSection(r,params.section,params.referencestack,refBounds);
    	extractfeatures(refImage,referencefs, params);

      inputImage = createSection(r,params.section,params.stack,refBounds);
      extractfeatures(inputImage, inputfs, params);


    	//match
    	final List< PointMatch > candidates = new ArrayList< PointMatch >();
  		FeatureTransform.matchFeatures( inputfs,referencefs, candidates, params.rod );
  		ArrayList<PointMatch> inliers = new ArrayList< PointMatch >();
  		switch ( params.modelType )
  		{
  			case 0:
  				model = new TranslationModel2D();
  				break;
  			case 1:
  				model = new RigidModel2D();
  				break;
  			case 2:
  				model = new SimilarityModel2D();
  				break;
  			case 3:
  				model = new AffineModel2D();
  				break;
  			case 4:
  				model = new HomographyModel2D();
  				break;
  			default:
  				model = new RigidModel2D();
  				return model;
  		}
  	    boolean modelFound;
  		try
  		{
  			modelFound = model.filterRansac(
  					candidates,
  					inliers,
  					params.Niters,
  					params.maxEpsilon,
  					params.minInlierRatio,
  					10 );
  			System.out.println("model found with " + inliers.size() + " inliers");
  		}
  		catch ( final NotEnoughDataPointsException e )
  		{
  		  System.out.println("no model found..");
  			modelFound = false;
  		}
  		return model;
  	}


    public static < T extends RealType<T>, S extends RealType<S> > PairWiseStitchingResult computePhaseCorrelation ( final ImagePlus img1, final ImagePlus img2, final int numPeaks, final boolean subpixelAccuracy )
  	{

      ImageConverter ic1 = new ImageConverter(img1);
      ic1.convertToGray8();
      img1.updateImage();
      ImageConverter ic2 = new ImageConverter(img2);
      ic2.convertToGray8();
      img2.updateImage();


  		Image <T> image1 = ImagePlusAdapter.wrap(img1);
      System.out.println("pc DEB 1");
  		Image <S> image2 = ImagePlusAdapter.wrap(img2);
      System.out.println("pc DEB 2");
      PhaseCorrelation< T,S > phaseCorr = new PhaseCorrelation<T,S>( image1,image2);
  		phaseCorr.setInvestigateNumPeaks( numPeaks );
      System.out.println("pc DEB 3");

  		if ( subpixelAccuracy )
  			phaseCorr.setKeepPhaseCorrelationMatrix( true );
      System.out.println("pc DEB 4");
  		phaseCorr.setComputeFFTinParalell( true );
  		if ( !phaseCorr.process() )
  		{
  			System.out.println( "Could not compute phase correlation: " + phaseCorr.getErrorMessage() );
  			return null;
  		}
      System.out.println("pc DEB 5");

  		// result
  		final PhaseCorrelationPeak pcp = phaseCorr.getShift();

  		final float[] shift = new float[ img1.getNDimensions() ];
  		final PairWiseStitchingResult result;
      System.out.println("pc DEB 6");

  		if ( subpixelAccuracy )
  		{
  			final Image<FloatType> pcm = phaseCorr.getPhaseCorrelationMatrix();

  			final ArrayList<DifferenceOfGaussianPeak<FloatType>> list = new ArrayList<DifferenceOfGaussianPeak<FloatType>>();
  			final Peak p = new Peak( pcp );
  			list.add( p );

  			final SubpixelLocalization<FloatType> spl = new SubpixelLocalization<FloatType>( pcm, list );
  			final boolean move[] = new boolean[ pcm.getNumDimensions() ];
  			for ( int i = 0; i < pcm.getNumDimensions(); ++i )
  				move[ i ] = false;
  			spl.setCanMoveOutside( true );
  			spl.setAllowedToMoveInDim( move );
  			spl.setMaxNumMoves( 0 );
  			spl.setAllowMaximaTolerance( false );
  			spl.process();

  			final Peak peak = (Peak)list.get( 0 );

  			for ( int d = 0; d < img1.getNDimensions(); ++d )
  				shift[ d ] = peak.getPCPeak().getPosition()[ d ] + peak.getSubPixelPositionOffset( d );

  			pcm.close();

  			result = new PairWiseStitchingResult( shift, pcp.getCrossCorrelationPeak(), p.getValue().get() );
  		}
  		else
  		{
  			for ( int d = 0; d < img1.getNDimensions(); ++d )
  				shift[ d ] = pcp.getPosition()[ d ];

  			result = new PairWiseStitchingResult( shift, pcp.getCrossCorrelationPeak(), pcp.getPhaseCorrelationPeak() );
  		}
      System.out.println("pc DEB 7");
  		return result;
  	}


    public static RigidModel2D createInverseModel(RigidModel2D initmodel)
  	{
  		System.out.println("Now calculating inverse.....");
  		RigidModel2D model = new RigidModel2D();

  		//calculate angle
  		double [] array = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  		initmodel.toArray(array);
  		double rot = Math.atan(array[2]/array[3]);

      System.out.println("ROT =");
      System.out.println(rot);
  		model.set(-1*rot, -1*array[4], -1*array[5]);
  		return model;
  	}

    /*public static ImagePlus createSection(RenderDataClient r,final Double z, String stack,List<TileSpec> tilespecs)
  	{
      //create image of box of region covering the tilespecs

  		System.out.println("test");
  		ImagePlus sectionImage = new ImagePlus();
  		try{
  			sectionImage = generateImageForZ(r, z, stack, 1.0,tilespecs);
  			return sectionImage;
  		}
  		catch ( final Exception e )
  			{
  				e.printStackTrace();
  				return sectionImage;
  			}
  	}*/

    public static ImagePlus createSection(RenderDataClient r,final Double z, String stack,List<TileSpec> tilespecs)
  	{
      //create image of box of region covering the tilespecs

      if (tilespecs.size() > 1)
      {
    		System.out.println("test");
    		ImagePlus sectionImage = new ImagePlus();
    		try{
    			sectionImage = generateImageForZ(r, z, stack, 1.0,tilespecs);
    			return sectionImage;
    		}
    		catch ( final Exception e )
    			{
    				e.printStackTrace();
    				return sectionImage;
    			}
      }
      else
      {
        ImagePlus sectionImage = new ImagePlus(tilespecs.get(0).getFirstMipmapEntry().getValue().getImageFilePath());

        //System.out.println(tilespecs.get(0).getFirstMipmapEntry().getValue().getImageFilePath());
        //System.exit(0);
        return sectionImage;
      }
  	}



    public static ImagePlus createSection(RenderDataClient r,final Double z, String stack, Bounds refBounds)
  	{
  		System.out.println("test");
  		ImagePlus sectionImage = new ImagePlus();
  		try{
  			sectionImage = generateImageForZ(r, z, stack, 1.0,refBounds);
  			return sectionImage;
  		}
  		catch ( final Exception e )
  			{
  				e.printStackTrace();
  				return sectionImage;
  			}
  	}

    public static void extractfeatures(ImagePlus imp, List< Feature > fs, Params params)
    {
      extractfeatures(imp,fs,params,1);
    }

    public static void extractfeatures(ImagePlus imp, List< Feature > fs, Params params, Integer scale)
    {
      if ( imp == null )
              System.err.println( "Failed to load image!!!" );
        else
            {
                ImageProcessor ip=imp.getProcessor();

                //scale image
                if (scale > 1)
                {
                  ip.setInterpolationMethod(ImageProcessor.BILINEAR);
                  ip = ip.resize(imp.getWidth()/scale,imp.getHeight()/scale,true);
                }



                //enhance contrast of image
                Calibration cal = new Calibration(imp);
                ImageStatistics reference_stats = ImageStatistics.getStatistics(ip, Measurements.MIN_MAX, cal);
                ContrastEnhancer cenh=new ContrastEnhancer();
                if (params.contrastEnhance == true)
                {
            cenh.setNormalize(true);
            cenh.equalize(ip);
            //cenh.stretchHistogram(ip,params.percentSaturated,reference_stats);
          }

                /* calculate sift features for the image or sub-region */
                FloatArray2DSIFT.Param siftParam = new FloatArray2DSIFT.Param();
                siftParam.initialSigma = params.initialSigma;
                siftParam.steps = params.steps;
                siftParam.minOctaveSize = params.minOctaveSize;
                int maxsize=params.maxOctaveSize;
                if (params.maxOctaveSize==0){
                  maxsize = (int) Math.min(imp.getHeight()/4,imp.getWidth()/4);
                }
                siftParam.maxOctaveSize = maxsize;
                siftParam.fdSize = params.fdSize;
                siftParam.fdBins = params.fdBins;
                FloatArray2DSIFT sift = new FloatArray2DSIFT(siftParam);
                SIFT ijSIFT = new SIFT(sift);

                ijSIFT.extractFeatures( ip, fs );
                System.out.println( "found " + fs.size() + " features in imagefile" );
            }

    }


    public static void ensureStackExists(final RenderDataClient renderDataClient,
                                         final String acquireStackName,
                                         final StackMetaData acquisition) throws Exception {
        //LOG.info("ensureAcquireStackExists: entry");

        StackMetaData stackMetaData;
        try {
            stackMetaData = renderDataClient.getStackMetaData(acquireStackName);
        } catch (final Throwable t) {

            //LOG.info("failed to retrieve stack metadata, will attempt to create new stack");
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

        /*if (! stackMetaData.isLoading()) {
            throw new IllegalStateException("stack state is " + stackMetaData.getState() +
                                            " but must be LOADING, stackMetaData=" + stackMetaData);
        }*/

        //LOG.info("ensureAcquireStackExists: exit, stackMetaData is {}", stackMetaData);
    }


    public static ImagePlus generateImageForZ(RenderDataClient renderDataClient, Double z, String stack, Double scale, List<TileSpec> ts)
  					throws Exception {

  			//LOG.info("generateImageForZ: {}, entry, sectionDirectory={}, dataClient={}",
  			//				 z, sectionDirectory, renderDataClient);

        //only one tile in List
        TileSpec t =ts.get(0);
        t.deriveBoundingBox(t.getMeshCellSize(), true);
        //TileBounds layerBounds = new TileBounds(t.getTileId(), t.getMinX(), t.getMinY(), t.getMaxX(), t.getMaxY());
        TileBounds layerBounds = new TileBounds(t.getTileId(), t.getLayout().getSectionId(),t.getZ(), t.getMinX(), t.getMinY(), t.getMaxX(), t.getMaxY());
  			//final Bounds layerBounds = renderDataClient.getLayerBounds(stack, z);
        z = t.getZ();
  			final String parametersUrl =
  							renderDataClient.getRenderParametersUrlString(stack,
  																														layerBounds.getMinX(),
  																														layerBounds.getMinY(),
  																														z,
  																														(int) (layerBounds.getDeltaX() + 0.5),
  																														(int) (layerBounds.getDeltaY() + 0.5),
  																														scale, null);


  			//LOG.debug("generateImageForZ: {}, loading {}", z, parametersUrl);

  			final RenderParameters renderParameters = RenderParameters.loadFromUrl(parametersUrl);
  			renderParameters.setDoFilter(false);

  			//final File sectionFile = getSectionFile(z);

  			final BufferedImage sectionImage = renderParameters.openTargetImage();

    		// set cache size to 50MB so that masks get cached but most of RAM is left for target image
  			final int maxCachedPixels = 50 * 1000000;
  			final ImageProcessorCache imageProcessorCache;
  		  imageProcessorCache = new ImageProcessorCache(maxCachedPixels, false, false);
  			ShortRenderer.render(renderParameters, sectionImage, imageProcessorCache);

  			/*Utils.saveImage(sectionImage, sectionFile.getAbsolutePath(), clientParameters.format, true, 0.85f);
  			LOG.info("generateImageForZ: {}, exit", z);*/
        String fullfilename = t.getFirstMipmapEntry().getValue().getImageFilePath();
				String delims = "[/]";
				String[] tokens = fullfilename.split(delims);
				ImagePlus I = new ImagePlus(tokens[tokens.length-1], sectionImage);

  			//ImagePlus I = new ImagePlus("sectionImage", sectionImage);
  			return I;
  	}



    public static ImagePlus generateImageForZ(RenderDataClient renderDataClient, final Double z, String stack, Double scale, Bounds refBounds)
  					throws Exception {

  			//LOG.info("generateImageForZ: {}, entry, sectionDirectory={}, dataClient={}",
  			//				 z, sectionDirectory, renderDataClient);

        //final StackMetaData smd = renderDataClient.getStackMetaData(stack);
  			//final Bounds layerBounds = smd.getStats().getStackBounds();
  			final String parametersUrl =
  							renderDataClient.getRenderParametersUrlString(stack,
  																														refBounds.getMinX(),
  																														refBounds.getMinY(),
  																														z,
  																														(int) (layerBounds.getDeltaX() + 0.5),
  																														(int) (layerBounds.getDeltaY() + 0.5),
  																														scale,null);


  			//LOG.debug("generateImageForZ: {}, loading {}", z, parametersUrl);

  			final RenderParameters renderParameters = RenderParameters.loadFromUrl(parametersUrl);
  			renderParameters.setDoFilter(false);

  			//final File sectionFile = getSectionFile(z);

  			final BufferedImage sectionImage = renderParameters.openTargetImage();

    		// set cache size to 50MB so that masks get cached but most of RAM is left for target image
  			final int maxCachedPixels = 50 * 1000000;
  			final ImageProcessorCache imageProcessorCache;
  		  imageProcessorCache = new ImageProcessorCache(maxCachedPixels, false, false);
  			ShortRenderer.render(renderParameters, sectionImage, imageProcessorCache);

  			/*Utils.saveImage(sectionImage, sectionFile.getAbsolutePath(), clientParameters.format, true, 0.85f);
  			LOG.info("generateImageForZ: {}, exit", z);*/
  			ImagePlus I = new ImagePlus("sectionImage", sectionImage);
  			return I;
  	}


    public static String model2datastring(AbstractModel<?> model)
  	{
  		String modelstring = model.toString();
  		modelstring = modelstring.replace("[", "");
  		modelstring = modelstring.replace("]", "");
  		modelstring = modelstring.replace("AffineTransform", "");
  		String[] modelvalues = modelstring.split("[,()]");
  		String datastring = "";

  		//convert to mpicbg.trakem2.transform.AffineModel2D
  		String classname = "mpicbg.trakem2.transform.AffineModel2D";
  		datastring = modelvalues[2] + " " + modelvalues[3] + " " + modelvalues[5] + " " + modelvalues[6] + " " + modelvalues[4] + " " + modelvalues[7];
  		return datastring;
  	}

  	public static String model2datastring_inv(AbstractModel<?> model)
  	{
  		String modelstring = model.toString();
  		modelstring = modelstring.replace("[", "");
  		modelstring = modelstring.replace("]", "");
  		modelstring = modelstring.replace("AffineTransform", "");
  		String[] modelvalues = modelstring.split("[,()]");
  		String datastring = "";

  		//convert to mpicbg.trakem2.transform.AffineModel2D
  		String classname = "mpicbg.trakem2.transform.AffineModel2D";

  		Float tr_x = Float.parseFloat(modelvalues[4]) * -1;
  		Float tr_y = Float.parseFloat(modelvalues[7]) * -1;
      Float rot2 = Float.parseFloat(modelvalues[3]) * -1;
  		Float rot3 = Float.parseFloat(modelvalues[5]) * -1;
  		//datastring = modelvalues[2] + " " + modelvalues[3] + " " + modelvalues[5] + " " + modelvalues[6] + " " + Float.toString(tr_x) + " " + Float.toString(tr_y);
      datastring = modelvalues[2] + " " + Float.toString(rot2) + " " + Float.toString(rot3) + " " + modelvalues[6] + " " + Float.toString(tr_x) + " " + Float.toString(tr_y);

      return datastring;
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

    public static final int POOL_TIMEOUT_IN_SECONDS = 20000;
    public static final int STD_THREAD_POOL_SIZE = 1;

    public static void main( String[] args )
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
                jc.setProgramName( "java [-options] -cp something.jar org.janelia.alignment.RegisterSections" );
                jc.usage();
                return;
              }



              final Gson gson = new Gson();
              try{

        			     params = gson.fromJson( new FileReader( params.input_json ), Params.class );
                 }
              catch ( final Exception e )
              {
                  return;
              }
              //System.out.println(params.initialSigma);
              //System.out.println(params.stack);

              //System.exit(0);
              final RenderDataClient r ;

              try
              {

                  //load params


                  //initialize
                  r = new RenderDataClient(params.baseDataUrl,params.owner,params.project);

                  ResolvedTileSpecCollection resolvedTilesinput = r.getResolvedTiles(params.stack,params.section);

                  ResolvedTileSpecCollection resolvedTilesref = r.getResolvedTiles(params.referencestack,params.section);
                  //System.out.println("Debug 1");
                  //calculate initial model and invert
                  AbstractModel <?> model = new RigidModel2D();
              		//model = calculatetransform(resolvedTilesinput, resolvedTilesref, params,r); //MIGHT NEED TO SWITCH????
                  model = calculatetransform( resolvedTilesref, resolvedTilesinput,params,r);
                  String classname = "mpicbg.trakem2.transform.AffineModel2D";
              		//String modstring = model2datastring_inv(model);
                  String modstring = model2datastring(model);
                  LeafTransformSpec modtrans = new LeafTransformSpec(classname,modstring);
                  //System.out.println("Debug 2");
                  //createtilespec ArrayList and apply the initial model
                  List<TileSpec> inputtileSpecs = settilespecs(resolvedTilesinput);
                  List<TileSpec> originputtileSpecs = inputtileSpecs;
                  final List<TileSpec> outputtileSpecs = inputtileSpecs; //initialize output
                  List<TileSpec> referencetileSpecs = settilespecs(resolvedTilesref);

                  //System.out.println("Debug 3");
                  for (int j = 0; j < inputtileSpecs.size(); j++)
                	{
                		ListTransformSpec listtspec = inputtileSpecs.get(j).getTransforms();
                		listtspec.addSpec(modtrans);
                	}

                  //tile pair matching
                  ArrayList<TileBounds> tbl = new ArrayList();
                  Map<String,Integer> tsHashMap = new HashMap<String,Integer> ();
                  for (int i = 0; i < referencetileSpecs.size(); i ++)
                  {
                    TileSpec t =referencetileSpecs.get(i);
                    t.deriveBoundingBox(t.getMeshCellSize(), true);
                    TileBounds tb = new TileBounds(t.getTileId(), t.getLayout().getSectionId(),t.getZ(), t.getMinX(), t.getMinY(), t.getMaxX(), t.getMaxY());
                    tbl.add(tb);
                    tsHashMap.put(t.getTileId(),i);
                  }


                  ArrayList<Integer> badindices = new ArrayList<Integer>();
                	ExecutorService tilePool = Executors.newFixedThreadPool(STD_THREAD_POOL_SIZE);
                	for (int tempj = 0; tempj < inputtileSpecs.size(); tempj ++)
                	{
          					final int j = tempj;
          					TileBoundsRTree tree = new TileBoundsRTree(referencetileSpecs.get(0).getZ(),tbl);
          					TileSpec u =inputtileSpecs.get(j);
          					u.deriveBoundingBox(u.getMeshCellSize(), true);


                    List<TileBounds> tileBoundsList  = tree.findTilesInBox(u.getMinX(), u.getMinY(), u.getMaxX(), u.getMaxY());
                    //find closest tile
          					if (tileBoundsList.size() < 1)
          					{
          							System.out.println("Tile bounds not found...");
          							badindices.add(tempj);
          					}

          					else
          					{
          						ArrayList <Double> distsq = new ArrayList();
          						for (int i = 0; i < tileBoundsList.size(); i++)
          						{
          							double sum = Math.pow(u.getMinX() - tileBoundsList.get(i).getMinX(),2) + Math.pow(u.getMinY() - tileBoundsList.get(i).getMinY(),2) + Math.pow(u.getMaxX() - tileBoundsList.get(i).getMaxX(),2) + Math.pow(u.getMaxY() - tileBoundsList.get(i).getMaxY(),2);
          							distsq.add(sum );
          						}


          						int index = distsq.indexOf(Collections.min(distsq));
                      if (distsq.get(index) < params.tileDistance)
                      {
              						TileSpec reftile = referencetileSpecs.get(tsHashMap.get(tileBoundsList.get(index).getTileId()));

              						ArrayList<TileSpec> ref = new ArrayList(); ref.add(reftile);
              						ArrayList<TileSpec> inp = new ArrayList(); inp.add(inputtileSpecs.get(j));
              						params.percentSaturated = 0.5f;
              						params.maxEpsilon = 2.5f;
              						params.initialSigma = 2.5f;
              						final Params jparams = params;
              						final AbstractModel<?> jmodel = model;
              						final String jclassname = classname;
              						final TileSpec jreftile = reftile;
                          final TileSpec jinptile = originputtileSpecs.get(j);
                          /*System.out.println("TESTING TILESPECS");
                          System.out.println(params.tileDistance);
                          System.out.println(jreftile.toJson().toString());
                          System.out.println(jinptile.toJson().toString());
                          System.out.println(distsq.toString());
                          System.out.println(distsq.get(index));*/
                          //System.exit(0);
                          final ArrayList<TileSpec> jref = ref;
              						final ArrayList<TileSpec> jinp = inp;

              						Runnable submissible = new Runnable() {
              							public void run() {

              								AbstractModel<?> tilemodel = new RigidModel2D();
              								tilemodel = calculatetransform(jref,jinp, jparams,(RigidModel2D)jmodel,r);
                              //tilemodel = calculatetransform(jinp,jref, jparams,(RigidModel2D)jmodel,r);

                              //String datastring = model2datastring_inv(tilemodel);
                              String datastring = model2datastring(tilemodel);
                              System.out.println("DATASTRING: "+ datastring);
              								System.out.println("MYTILELIST1: ");
              								System.out.println("MYTILELIST11: " + jclassname);
              								LeafTransformSpec tilelts = new LeafTransformSpec(jclassname, datastring);
              								System.out.println("MYTILELIST111: " + tilelts.toJson());
              								System.out.println("MYTILELIST1111: " + jreftile.getLastTransform().toJson());
              								//LeafTransformSpec rfspec = (LeafTransformSpec) jreftile.getLastTransform();
                              //LeafTransformSpec inpspec = (LeafTransformSpec) jinptile.getLastTransform();
              								System.out.println("MYTILELIST2: ");
              								//ListTransformSpec mytilelist = new ListTransformSpec(jparams.referenceID,null);
                              //ListTransformSpec mytilelist = new ListTransformSpec("REFID",null);
                              ListTransformSpec mytilelist = jreftile.getTransforms();
                              //System.out.println("MYTILELIST3: ");
                              //mytilelist.removeLastSpec();
              								//mytilelist.addSpec(inpspec);
                              //mytilelist.addSpec(jinptile.getLastTransform());
                              mytilelist.addSpec(tilelts);
              								System.out.println("MYTILELIST: ");
              								System.out.println(mytilelist.toString());
              								outputtileSpecs.get(j).setTransforms(mytilelist);


                							} //end run
                						}; //end Runnable
                						tilePool.submit(submissible);
                        }//end if distsq < 5000
          					}//end else
          				}//end for

          			tilePool.shutdown();
          			try
          			{
          				tilePool.awaitTermination(POOL_TIMEOUT_IN_SECONDS,TimeUnit.SECONDS);
          			}
          			catch (Exception ex)
          			{
          				throw new RuntimeException(ex);
          			}


                final StringBuilder json = new StringBuilder(16 * 1024);
                System.out.println("NOW OUTPUTTING TO FILE: ");
                int numadded = 0;
                for (int n = 0; n< outputtileSpecs.size(); n++)
                {

          				System.out.println(n);
          				if (badindices.contains(n))
          					System.out.println("Skipping "+n);
          				else
          				{
          					String myjson =outputtileSpecs.get(n).toJson() ;
          					if (numadded >0 )
          						myjson = "," + myjson;
          					json.append(myjson);
          					numadded = numadded+1;
          				}
                }


                //////////OUTPUT


              	FileOutputStream jsonStream = null;
              	String par1 = "[";
              	String par2 = "]";

                //This part to comment
              	try
              	{
                  jsonStream = new FileOutputStream("testingoutput.json");
              		//jsonStream = new FileOutputStream(params.outputtilespec);
              		jsonStream.write(par1.getBytes());
                  jsonStream.write(json.toString().getBytes());
                  jsonStream.write(par2.getBytes());
                }
              	catch (final IOException e)
              	{
                  throw new RuntimeException("failed to write to JSON stream", e);
                }


                //end commented

                //final List<TransformSpec> trans = new ArrayList();
                Collection<TransformSpec> trans = resolvedTilesref.getTransformSpecs();
                ResolvedTileSpecCollection resTiles = new ResolvedTileSpecCollection(trans,outputtileSpecs);

                try
        				{
        		        final StackMetaData smd = r.getStackMetaData(params.stack);
                    System.out.println("NOW OUTPUTTING RESTILES TO JSON");
                    System.out.println(resTiles.toJson().toString());
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
              catch ( final Exception e )
              {
                  return;
              }

            }
}
