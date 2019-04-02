package at_modules;

import ij.IJ;
import ij.gui.Roi;

import java.awt.Rectangle;
import java.util.ArrayList;
import java.util.Vector;
import java.util.concurrent.atomic.AtomicInteger;

import mpicbg.imglib.multithreading.SimpleMultiThreading;
import mpicbg.imglib.util.Util;
import mpicbg.models.TranslationModel2D;
import mpicbg.models.TranslationModel3D;
//import mpicbg.stitching.ImageCollectionandHashContainer;
import mpicbg.stitching.ImageCollectionElement;
import mpicbg.stitching.StitchingParameters;
import mpicbg.stitching.ImagePlusTimePoint;
import mpicbg.stitching.ComparePair;
import mpicbg.stitching.PairWiseStitchingImgLib;
import mpicbg.stitching.PairWiseStitchingResult;
import mpicbg.stitching.GlobalOptimization;

import java.util.HashMap;
import java.util.Map;

public class CollectionStitchingImgLibCC
{


              public static ImageCollectionandHashContainer stitchCollectionandcalculateconnections( final ArrayList< ImageCollectionElement > elements, final StitchingParameters params )
	{


		// the result
		final ArrayList< ImagePlusTimePoint > optimized;
                final Map<String,Integer> connects = new HashMap<String, Integer> ();



		if ( params.computeOverlap )
		{

			// find overlapping tiles
			final Vector< ComparePair > pairs = findOverlappingTiles( elements, params );

			if ( pairs == null || pairs.size() == 0 )
			{
				IJ.log( "No overlapping tiles could be found given the approximate layout." );
				return null;
			}

			// compute all compare pairs
			// compute all matchings
			final AtomicInteger ai = new AtomicInteger(0);

			final int numThreads;

			if ( params.cpuMemChoice == 0 )
				numThreads = 1;
			else
				numThreads = Runtime.getRuntime().availableProcessors();

	        final Thread[] threads = SimpleMultiThreading.newThreads( numThreads );

	        for ( int ithread = 0; ithread < threads.length; ++ithread )
	            threads[ ithread ] = new Thread(new Runnable()
	            {
	                @Override
	                public void run()
	                {
	                   	final int myNumber = ai.getAndIncrement();

	                    for ( int i = 0; i < pairs.size(); i++ )
	                    {
	                    	if ( i % numThreads == myNumber )
	                    	{
	                    		final ComparePair pair = pairs.get( i );

	                    		long start = System.currentTimeMillis();

	                    		// where do we approximately overlap?
	                			final Roi roi1 = getROI( pair.getTile1().getElement(), pair.getTile2().getElement() );
	                			final Roi roi2 = getROI( pair.getTile2().getElement(), pair.getTile1().getElement() );

	            				final PairWiseStitchingResult result = PairWiseStitchingImgLib.stitchPairwise( pair.getImagePlus1(), pair.getImagePlus2(), roi1, roi2, pair.getTimePoint1(), pair.getTimePoint2(), params );
	            				if ( result == null )
	            				{
	            					IJ.log( "Collection stitching failed" );
	            					return;
	            				}

	            				if ( params.dimensionality == 2 )
	            					pair.setRelativeShift( new float[]{ result.getOffset( 0 ), result.getOffset( 1 ) } );
	            				else
	            					pair.setRelativeShift( new float[]{ result.getOffset( 0 ), result.getOffset( 1 ), result.getOffset( 2 ) } );

	            				pair.setCrossCorrelation( result.getCrossCorrelation() );

	            				IJ.log( pair.getImagePlus1().getTitle() + "[" + pair.getTimePoint1() + "]" + " <- " + pair.getImagePlus2().getTitle() + "[" + pair.getTimePoint2() + "]" + ": " +
	            						Util.printCoordinates( result.getOffset() ) + " correlation (R)=" + result.getCrossCorrelation() + " (" + (System.currentTimeMillis() - start) + " ms)");

                                                /*if (result.getCrossCorrelation() > params.regThreshold)
						{
                                                	int count1 = connects.containsKey(pair.getImagePlus1().getTitle()) ? connects.get(pair.getImagePlus1().getTitle()) : 0;
	                                        	connects.put(pair.getImagePlus1().getTitle(), count1+1);
							int count2 = connects.containsKey(pair.getImagePlus2().getTitle()) ? connects.get(pair.getImagePlus2().getTitle()) : 0;
	                                        	connects.put(pair.getImagePlus2().getTitle(), count2+1);

						}*/
	                    	}
	                    }
	                }
	            });


	        final long time = System.currentTimeMillis();
	        SimpleMultiThreading.startAndJoin( threads );

	        // get the final positions of all tiles
		optimized = GlobalOptimization.optimize( pairs, pairs.get( 0 ).getTile1(), params );
		IJ.log( "Finished registration process (" + (System.currentTimeMillis() - time) + " ms)." );

			System.out.println("Starting to print out hash table!");
			for(Object objname:connects.keySet()) {
		   		System.out.println(objname);
		   		System.out.println(connects.get(objname));
 			}

                for (ImagePlusTimePoint ipt : optimized)
		{
			connects.put(ipt.getImagePlus().getTitle(), 100);
		}

		}

		else
		{

			// all ImagePlusTimePoints, each of them needs its own model
			optimized = new ArrayList< ImagePlusTimePoint >();

			for ( final ImageCollectionElement element : elements )
			{
				final ImagePlusTimePoint imt = new ImagePlusTimePoint( element.open( params.virtual ), element.getIndex(), 1, element.getModel(), element );

				// set the models to the offset
				if ( params.dimensionality == 2 )
				{
					final TranslationModel2D model = (TranslationModel2D)imt.getModel();
					model.set( element.getOffset( 0 ), element.getOffset( 1 ) );
				}
				else
				{
					final TranslationModel3D model = (TranslationModel3D)imt.getModel();
					model.set( element.getOffset( 0 ), element.getOffset( 1 ), element.getOffset( 2 ) );
				}

				optimized.add( imt );
			}

		}

		ImageCollectionandHashContainer cont =new ImageCollectionandHashContainer();
		cont.setIPTPArray(optimized);
		cont.setconnections(connects);
                return cont;
		//return optimized;
	}







































	public static ArrayList< ImagePlusTimePoint > stitchCollection( final ArrayList< ImageCollectionElement > elements, final StitchingParameters params )

	{
		// the result
		final ArrayList< ImagePlusTimePoint > optimized;
                final Map<String,Integer> connects = new HashMap<String, Integer> ();


		if ( params.computeOverlap )
		{
			// find overlapping tiles
			final Vector< ComparePair > pairs = findOverlappingTiles( elements, params );

			if ( pairs == null || pairs.size() == 0 )
			{
				IJ.log( "No overlapping tiles could be found given the approximate layout." );
				return null;
			}

			// compute all compare pairs
			// compute all matchings
			final AtomicInteger ai = new AtomicInteger(0);

			final int numThreads;

			if ( params.cpuMemChoice == 0 )
				numThreads = 1;
			else
				numThreads = Runtime.getRuntime().availableProcessors();

	        final Thread[] threads = SimpleMultiThreading.newThreads( numThreads );

	        for ( int ithread = 0; ithread < threads.length; ++ithread )
	            threads[ ithread ] = new Thread(new Runnable()
	            {
	                @Override
	                public void run()
	                {
	                   	final int myNumber = ai.getAndIncrement();

	                    for ( int i = 0; i < pairs.size(); i++ )
	                    {
	                    	if ( i % numThreads == myNumber )
	                    	{
	                    		final ComparePair pair = pairs.get( i );

	                    		long start = System.currentTimeMillis();

	                    		// where do we approximately overlap?
	                			final Roi roi1 = getROI( pair.getTile1().getElement(), pair.getTile2().getElement() );
	                			final Roi roi2 = getROI( pair.getTile2().getElement(), pair.getTile1().getElement() );

	            				final PairWiseStitchingResult result = PairWiseStitchingImgLib.stitchPairwise( pair.getImagePlus1(), pair.getImagePlus2(), roi1, roi2, pair.getTimePoint1(), pair.getTimePoint2(), params );
	            				if ( result == null )
	            				{
	            					IJ.log( "Collection stitching failed" );
	            					return;
	            				}

	            				if ( params.dimensionality == 2 )
	            					pair.setRelativeShift( new float[]{ result.getOffset( 0 ), result.getOffset( 1 ) } );
	            				else
	            					pair.setRelativeShift( new float[]{ result.getOffset( 0 ), result.getOffset( 1 ), result.getOffset( 2 ) } );

	            				pair.setCrossCorrelation( result.getCrossCorrelation() );

	            				IJ.log( pair.getImagePlus1().getTitle() + "[" + pair.getTimePoint1() + "]" + " <- " + pair.getImagePlus2().getTitle() + "[" + pair.getTimePoint2() + "]" + ": " +
	            				Util.printCoordinates( result.getOffset() ) + " correlation (R)=" + result.getCrossCorrelation() + " (" + (System.currentTimeMillis() - start) + " ms)");
                                                if (result.getCrossCorrelation() > 0.7)
                                                {
                                                	int count1 = connects.containsKey(pair.getImagePlus1().getTitle()) ? connects.get(pair.getImagePlus1().getTitle()) : 0;
                                                	connects.put(pair.getImagePlus1().getTitle(), count1+1);
                                                	int count2 = connects.containsKey(pair.getImagePlus2().getTitle()) ? connects.get(pair.getImagePlus2().getTitle()) : 0;
                                                	connects.put(pair.getImagePlus2().getTitle(), count2+1);

                                                }
	                    		}
	                    	}
	                	}
	            	});


	        final long time = System.currentTimeMillis();
	        SimpleMultiThreading.startAndJoin( threads );

	        // get the final positions of all tiles
	        optimized = GlobalOptimization.optimize( pairs, pairs.get( 0 ).getTile1(), params );
	        IJ.log( "Finished registration process (" + (System.currentTimeMillis() - time) + " ms)." );

			System.out.println("Starting to print out hash table!");
			for(Object objname:connects.keySet()) {
		   		System.out.println(objname);
		   		System.out.println(connects.get(objname));
 			}

		}

		else
		{

			// all ImagePlusTimePoints, each of them needs its own model
			optimized = new ArrayList< ImagePlusTimePoint >();

			for ( final ImageCollectionElement element : elements )
			{
				final ImagePlusTimePoint imt = new ImagePlusTimePoint( element.open( params.virtual ), element.getIndex(), 1, element.getModel(), element );

				// set the models to the offset
				if ( params.dimensionality == 2 )
				{
					final TranslationModel2D model = (TranslationModel2D)imt.getModel();
					model.set( element.getOffset( 0 ), element.getOffset( 1 ) );
				}
				else
				{
					final TranslationModel3D model = (TranslationModel3D)imt.getModel();
					model.set( element.getOffset( 0 ), element.getOffset( 1 ), element.getOffset( 2 ) );
				}

				optimized.add( imt );
			}

		}

		ImageCollectionandHashContainer cont =new ImageCollectionandHashContainer();
		cont.setIPTPArray(optimized);
		cont.setconnections(connects);
                //return cont;
		return optimized;
	}

	protected static Roi getROI( final ImageCollectionElement e1, final ImageCollectionElement e2 )
	{
		final int start[] = new int[ 2 ], end[] = new int[ 2 ];

		for ( int dim = 0; dim < 2; ++dim )
		{
			// begin of 2 lies inside 1
			if ( e2.getOffset()[ dim ] >= e1.getOffset()[ dim ] && e2.getOffset()[ dim ] <= e1.getOffset()[ dim ] + e1.getDimension(dim))
			{
				start[ dim ] = Math.round( e2.getOffset()[ dim ] - e1.getOffset()[ dim ] );

				// end of 2 lies inside 1
				if ( e2.getOffset()[ dim ] + e2.getDimensions()[ dim ] <= e1.getOffset()[ dim ] + e1.getDimensions()[ dim ] )
					end[ dim ] = Math.round( e2.getOffset()[ dim ] + e2.getDimensions()[ dim ] - e1.getOffset()[ dim ] );
				else
					end[ dim ] = Math.round( e1.getDimensions()[ dim ] );
			}
			else if ( e2.getOffset()[ dim ] + e2.getDimensions()[ dim ] <= e1.getOffset()[ dim ] + e1.getDimensions()[ dim ] ) // end of 2 lies inside 1
			{
				start[ dim ] = 0;
				end[ dim ] = Math.round( e2.getOffset()[ dim ] + e2.getDimensions()[ dim ] - e1.getOffset()[ dim ] );
			}
			else // if both outside then the whole image
			{
				start[ dim ] = -1;
				end[ dim ] = -1;
			}
		}

		return new Roi( new Rectangle( start[ 0 ], start[ 1 ], end[ 0 ] - start[ 0 ], end[ 1 ] - start[ 1 ] ) );
	}

	protected static Vector< ComparePair > findOverlappingTiles( final ArrayList< ImageCollectionElement > elements, final StitchingParameters params )
	{
		for ( final ImageCollectionElement element : elements )
		{

			if ( element.open( params.virtual ) == null )
				return null;
		}

		// all ImagePlusTimePoints, each of them needs its own model
		final ArrayList< ImagePlusTimePoint > listImp = new ArrayList< ImagePlusTimePoint >();
		for ( final ImageCollectionElement element : elements )
			listImp.add( new ImagePlusTimePoint( element.open( params.virtual ), element.getIndex(), 1, element.getModel(), element ) );

		// get the connecting tiles
		final Vector< ComparePair > overlappingTiles = new Vector< ComparePair >();

		// Added by John Lapage: if the sequential option has been chosen, pair up each image
		// with the images within the specified range, and return.

		if ( params.sequential )
		{
			for ( int i = 0; i < elements.size(); i++ )
			{
				for ( int j = 1 ; j <= params.seqRange ; j++ )
				{
					if ( ( i + j ) >= elements.size() )
						break;

					overlappingTiles.add( new ComparePair( listImp.get( i ), listImp.get( i+j ) ) );
				}
			}
			return overlappingTiles;
		}
		// end of addition

		for ( int i = 0; i < elements.size() - 1; i++ )
			for ( int j = i + 1; j < elements.size(); j++ )
			{
				final ImageCollectionElement e1 = elements.get( i );
				final ImageCollectionElement e2 = elements.get( j );

				boolean overlapping = true;

        for ( int d = 0; d < params.dimensionality; ++d )
				{
					if ( !( ( e2.getOffset()[ d ] >= e1.getOffset()[ d ] && e2.getOffset()[ d ] <= e1.getOffset()[ d ] + e1.getDimensions()[ d ] ) ||
						    ( e2.getOffset()[ d ] + e2.getDimensions()[ d ] >= e1.getOffset()[ d ] && e2.getOffset()[ d ] + e2.getDimensions()[ d ] <= e1.getOffset()[ d ] + e1.getDimensions()[ d ] ) ||
						    ( e2.getOffset()[ d ] <= e1.getOffset()[ d ] && e2.getOffset()[ d ] >= e1.getOffset()[ d ] + e1.getDimensions()[ d ] )
					   )  )
									overlapping = false;
				}

				if ( overlapping )
				{
					//final ImagePlusTimePoint impA = new ImagePlusTimePoint( e1.open(), e1.getIndex(), 1, e1.getModel().copy(), e1 );
					//final ImagePlusTimePoint impB = new ImagePlusTimePoint( e2.open(), e2.getIndex(), 1, e2.getModel().copy(), e2 );
					overlappingTiles.add( new ComparePair( listImp.get( i ), listImp.get( j ) ) );
				}
			}

		return overlappingTiles;
	}
}
