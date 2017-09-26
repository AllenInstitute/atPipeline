package at_modules;

import ij.IJ;

import java.util.ArrayList;

import mpicbg.stitching.ImagePlusTimePoint;
import java.util.HashMap;
import java.util.Map;

public class ImageCollectionandHashContainer
{
	public ArrayList< ImagePlusTimePoint > IPTPArray;
	public Map<String,Integer> connections;

	public void ImageCollectionandHashContainer(ArrayList< ImagePlusTimePoint > newarray, Map<String,Integer> newconnections)
	{
		IPTPArray = newarray;
		connections = newconnections;
	}
	public void ImageCollectionandHashContainer()
	{ }

	public void setIPTPArray(ArrayList< ImagePlusTimePoint > newarray)
	{
		IPTPArray = newarray;
	}
	public void setconnections (Map<String,Integer> newconnections)
	{
		connections = newconnections;
	}
	public ArrayList< ImagePlusTimePoint > getIPTPArray()
	{
		return IPTPArray;
	}

	public Map<String,Integer> getconnections()
	{
		return connections;
	}
}
